// Syncs the ledger with the BolKhata FastAPI backend (backend/app/api).
// The phone cache stays what the UI reads, so the app keeps working offline:
// new entries are pushed in the background and retried on the next save or app start.

import 'dart:async';
import 'dart:convert';
import 'dart:developer' as dev;

import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

import '../core/ledger_store.dart';
import '../core/models.dart';
import 'prefs_ledger_store.dart';

class ApiLedgerStore extends PrefsLedgerStore {
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

  static Future<ApiLedgerStore> open(String baseUrl, {http.Client? client}) async {
    final s = ApiLedgerStore(await SharedPreferences.getInstance(), baseUrl, client: client)
      ..loadCache();
    s._synced.addAll(s.prefs.getStringList(_syncedKey) ?? []);
    try {
      await s._enqueue(() async {
        await s._pushPending(); // anything saved while offline goes up first
        await s._pull();
      });
    } catch (e) {
      dev.log('Server unreachable, using phone cache: $e', name: 'bolkhata');
    }
    return s;
  }

  /// Completes when background pushes queued so far have finished.
  Future<void> get flushed => _queue;

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
      await _send('POST', '/transactions', {
        'customer_id': customerId,
        'type': e.type == EntryType.credit ? 'CREDIT' : 'PAYMENT',
        'amount': e.amount,
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
    final found = await _send('GET', '/customers?search=${Uri.encodeQueryComponent(name.trim())}') as List;
    final match = found.cast<Map<String, dynamic>>().where((c) => LedgerStore.normalizeName(c['name'] as String) == key);
    final id = match.isNotEmpty
        ? match.first['id'] as String
        : (await _send('POST', '/customers', {'name': name.trim()}))['id'] as String;
    return _serverCustomerIds[key] = id;
  }

  Future<void> _pull() async {
    final customers = [
      for (final c in (await _send('GET', '/customers') as List).cast<Map<String, dynamic>>())
        Customer(id: c['id'] as String, name: c['name'] as String, createdAt: DateTime.parse(c['created_at'] as String)),
    ];
    final pulled = <LedgerEntry>[];
    for (var offset = 0;; offset += _pageSize) {
      final page = (await _send('GET', '/transactions?status=CONFIRMED&limit=$_pageSize&offset=$offset') as List)
          .cast<Map<String, dynamic>>();
      pulled.addAll(page.map((t) => LedgerEntry(
            id: t['id'] as String,
            customerId: t['customer_id'] as String,
            type: t['type'] == 'CREDIT' ? EntryType.credit : EntryType.payment,
            // shortcut: the app stores whole rupees, so paise from the web app are rounded; move to paise ints if that matters.
            amount: num.parse('${t['amount']}').round(),
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

  Future<dynamic> _send(String method, String path, [Object? body]) async {
    // shortcut: always the backend's demo shop; add a login screen before real shopkeepers use it.
    _token ??= (await _request('POST', '/auth/demo'))['access_token'] as String;
    return _request(method, path, body);
  }

  Future<dynamic> _request(String method, String path, [Object? body]) async {
    final req = http.Request(method, Uri.parse('$baseUrl/api$path'))
      ..headers['Content-Type'] = 'application/json';
    if (_token != null) req.headers['Authorization'] = 'Bearer $_token';
    if (body != null) req.body = jsonEncode(body);
    final res = await http.Response.fromStream(
        await _http.send(req).timeout(const Duration(seconds: 10)));
    if (res.statusCode >= 300) {
      throw http.ClientException('${res.statusCode} ${res.body}', req.url);
    }
    return jsonDecode(utf8.decode(res.bodyBytes));
  }
}
