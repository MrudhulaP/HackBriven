// Syncs the ledger with the BolKhata FastAPI backend (backend/app/api).
// The phone cache stays what the UI reads, so the app keeps working offline:
// new entries are pushed in the background and retried on the next save or app start.
// PROTOTYPE: the login token sits in SharedPreferences next to the (also unencrypted) cache.

import 'dart:async';
import 'dart:convert';
import 'dart:developer' as dev;

import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

import '../core/ledger_store.dart';
import '../core/models.dart';
import 'prefs_ledger_store.dart';

/// The server rejected the request; [message] is its explanation.
class ApiException implements Exception {
  final int statusCode;
  final String message;
  ApiException(this.statusCode, this.message);

  bool get isUnauthorized => statusCode == 401;

  @override
  String toString() => message;
}

class ApiLedgerStore extends PrefsLedgerStore {
  static const tokenKey = 'bolkhata_token';
  static const _accountKey = 'bolkhata_account_id';
  static const _syncedKey = 'bolkhata_synced_ids_v1';
  static const _pageSize = 200; // backend caps /transactions?limit at 200

  final String baseUrl;
  final http.Client _http;
  final Set<String> _synced = {};
  final Map<String, String> _serverCustomerIds = {};
  String? _token;
  Future<void> _queue = Future.value();

  ApiLedgerStore(super.prefs, this.baseUrl, {http.Client? client})
      : _http = client ?? http.Client();

  /// Opens with the saved token. Returns null when there is none, or the
  /// server says it has expired: the caller shows the login screen.
  /// Offline, it opens from the phone cache.
  static Future<ApiLedgerStore?> open(String baseUrl, {http.Client? client}) async {
    final s = ApiLedgerStore(await SharedPreferences.getInstance(), baseUrl, client: client);
    s._token = s.prefs.getString(tokenKey);
    if (s._token == null) return null;
    s.loadCache();
    s._synced.addAll(s.prefs.getStringList(_syncedKey) ?? []);
    try {
      await s._enqueue(() async {
        await s._pushPending(); // anything saved while offline goes up first
        await s._pull();
      });
    } catch (e) {
      if (e is ApiException && e.isUnauthorized) {
        await s.prefs.remove(tokenKey); // keep the cache: unsynced entries go up after login
        return null;
      }
      dev.log('Server unreachable, using phone cache: $e', name: 'bolkhata');
    }
    return s;
  }

  /// Logs in, or creates the account when [register] is true, then opens the
  /// store. Throws [ApiException] with the server's message on failure.
  static Future<ApiLedgerStore> signIn(
    String baseUrl, {
    required bool register,
    required Map<String, String> fields,
    http.Client? client,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    final s = ApiLedgerStore(prefs, baseUrl, client: client);
    final res = await s._request('POST', register ? '/auth/register' : '/auth/login', fields);
    final userId = res['user']['id'] as String;

    final previous = prefs.getString(_accountKey);
    // No previous account: a ledger kept phone-only so far is adopted by this account.
    if (previous != null && previous != userId) {
      // The phone cache belongs to another account: never push it into this one.
      s.loadCache();
      s._synced.addAll(prefs.getStringList(_syncedKey) ?? []);
      if (s.unsyncedCount > 0) {
        throw ApiException(409,
            'This phone has ${s.unsyncedCount} entries from another account that are not on the server yet. Log in to that account first.');
      }
      s.loadAll([], []);
      await s.savePrefsCache();
      await prefs.remove(_syncedKey);
    }
    await prefs.setString(tokenKey, res['access_token'] as String);
    await prefs.setString(_accountKey, userId);
    return (await open(baseUrl, client: client))!;
  }

  /// Entries saved on the phone but not yet on the server.
  int get unsyncedCount => entries.where((e) => !_synced.contains(e.id)).length;

  /// Pushes what it can, then logs out and clears the phone cache.
  /// Refuses (returns the count) while entries are still only on this phone.
  Future<int> logout() async {
    try {
      await _enqueue(_pushPending);
    } catch (_) {}
    if (unsyncedCount > 0) return unsyncedCount;
    loadAll([], []);
    await savePrefsCache();
    for (final k in [tokenKey, _accountKey, _syncedKey]) {
      await prefs.remove(k);
    }
    return 0;
  }

  /// Completes when background pushes queued so far have finished.
  Future<void> get flushed => _queue;

  Future<void> savePrefsCache() => super.persist();

  @override
  Future<void> persist() async {
    await super.persist();
    // Not awaited: a slow or offline server must not hold up the voice reply.
    unawaited(_enqueue(_pushPending).catchError((Object e) {
      dev.log('Sync failed, will retry: $e', name: 'bolkhata');
    }));
  }

  Future<void> _enqueue(Future<void> Function() job) {
    final run = _queue.then((_) => job());
    _queue = run.catchError((_) {}); // keep the queue alive after a failure
    return run;
  }

  Future<void> _pushPending() async {
    for (final e in entries.where((e) => !_synced.contains(e.id)).toList()) {
      final customerId = await _serverCustomerId(customerById(e.customerId)!.name);
      await _request('POST', '/transactions', {
        'customer_id': customerId,
        'type': e.type == EntryType.credit ? 'CREDIT' : 'PAYMENT',
        'amount': paiseToDecimal(e.paise),
        'transaction_date': e.createdAt.toIso8601String().substring(0, 10),
        'description': e.rawText,
        'input_method': 'VOICE',
        'idempotency_key': e.id, // server ignores a repeat, so retries are safe
      });
      _synced.add(e.id);
      await prefs.setStringList(_syncedKey, _synced.toList());
    }
  }

  /// Exact, case-insensitive name match, same rule as LedgerStore.findCustomer.
  Future<String> _serverCustomerId(String name) async {
    final key = LedgerStore.normalizeName(name);
    final cached = _serverCustomerIds[key];
    if (cached != null) return cached;
    final found = await _request('GET', '/customers?search=${Uri.encodeQueryComponent(name.trim())}') as List;
    final match = found.cast<Map<String, dynamic>>().where((c) => LedgerStore.normalizeName(c['name'] as String) == key);
    final id = match.isNotEmpty
        ? match.first['id'] as String
        : (await _request('POST', '/customers', {'name': name.trim()}))['id'] as String;
    return _serverCustomerIds[key] = id;
  }

  Future<void> _pull() async {
    final customers = [
      for (final c in (await _request('GET', '/customers') as List).cast<Map<String, dynamic>>())
        Customer(id: c['id'] as String, name: c['name'] as String, createdAt: DateTime.parse(c['created_at'] as String)),
    ];
    final pulled = <LedgerEntry>[];
    for (var offset = 0;; offset += _pageSize) {
      final page = (await _request('GET', '/transactions?status=CONFIRMED&limit=$_pageSize&offset=$offset') as List)
          .cast<Map<String, dynamic>>();
      pulled.addAll(page.map((t) => LedgerEntry(
            id: t['id'] as String,
            customerId: t['customer_id'] as String,
            type: t['type'] == 'CREDIT' ? EntryType.credit : EntryType.payment,
            paise: paiseFromDecimal(t['amount'] as Object),
            createdAt: DateTime.parse(t['created_at'] as String),
            rawText: t['description'] as String?,
          )));
      if (page.length < _pageSize) break;
    }
    loadAll(customers, pulled);
    _serverCustomerIds
      ..clear()
      ..addAll({for (final c in customers) LedgerStore.normalizeName(c.name): c.id});
    _synced
      ..clear()
      ..addAll(pulled.map((e) => e.id));
    await prefs.setStringList(_syncedKey, _synced.toList());
    await super.persist();
  }

  Future<dynamic> _request(String method, String path, [Object? body]) async {
    final req = http.Request(method, Uri.parse('$baseUrl/api$path'))
      ..headers['Content-Type'] = 'application/json';
    if (_token != null) req.headers['Authorization'] = 'Bearer $_token';
    if (body != null) req.body = jsonEncode(body);
    final res = await http.Response.fromStream(
        await _http.send(req).timeout(const Duration(seconds: 10)));
    final text = utf8.decode(res.bodyBytes);
    if (res.statusCode >= 300) throw ApiException(res.statusCode, _detail(text));
    return jsonDecode(text);
  }

  /// FastAPI puts the reason in "detail": a string, or a list of field errors.
  static String _detail(String body) {
    try {
      final d = (jsonDecode(body) as Map)['detail'];
      if (d is String) return d;
      if (d is List && d.isNotEmpty) return '${(d.first as Map)['loc']?.last}: ${(d.first as Map)['msg']}';
    } catch (_) {}
    return body;
  }
}
