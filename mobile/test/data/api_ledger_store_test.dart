import 'dart:convert';

import 'package:bolkhata/core/models.dart';
import 'package:bolkhata/data/api_ledger_store.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Just enough of the FastAPI backend to exercise login and sync.
class FakeServer {
  final customers = <Map<String, dynamic>>[];
  final txs = <Map<String, dynamic>>[];
  final passwords = {'9000000001': 'pw1', '9000000002': 'pw2'};
  String validToken = 't-9000000001';
  bool down = false;

  late final client = MockClient((req) async {
    if (down) throw http.ClientException('offline');
    final path = req.url.path;
    Map<String, dynamic> body() => jsonDecode(req.body) as Map<String, dynamic>;
    if (path == '/api/auth/login') {
      final b = body();
      if (passwords[b['mobile']] != b['password']) {
        return _json({'detail': 'Invalid mobile number or password'}, 401);
      }
      return _json({'access_token': 't-${b['mobile']}', 'user': {'id': 'u-${b['mobile']}'}});
    }
    if (req.headers['Authorization'] != 'Bearer $validToken') {
      return _json({'detail': 'Session expired. Please log in again.'}, 401);
    }
    if (path == '/api/customers' && req.method == 'GET') {
      final q = (req.url.queryParameters['search'] ?? '').toLowerCase();
      return _json(customers.where((c) => (c['name'] as String).toLowerCase().contains(q)).toList());
    }
    if (path == '/api/customers') {
      final c = {'id': 'c${customers.length}', 'name': body()['name'], 'created_at': '2026-11-21T10:00:00'};
      customers.add(c);
      return _json(c, 201);
    }
    if (path == '/api/transactions' && req.method == 'GET') return _json(txs);
    if (path == '/api/transactions') {
      final b = body();
      if (txs.any((t) => t['idempotency_key'] == b['idempotency_key'])) return _json(txs.first, 201);
      final t = {...b, 'id': 't${txs.length}', 'created_at': '2026-11-21T10:00:00'};
      txs.add(t);
      return _json(t, 201);
    }
    return http.Response('not found', 404);
  });

  http.Response _json(Object o, [int status = 200]) => http.Response(jsonEncode(o), status);
}

void main() {
  late FakeServer server;
  Future<ApiLedgerStore> openLoggedIn() async =>
      (await ApiLedgerStore.open('http://x', client: server.client))!;
  Future<ApiLedgerStore> signIn(String mobile, String pw) => ApiLedgerStore.signIn('http://x',
      register: false, fields: {'mobile': mobile, 'password': pw}, client: server.client);

  setUp(() {
    SharedPreferences.setMockInitialValues(
        {ApiLedgerStore.tokenKey: 't-9000000001', 'bolkhata_account_id': 'u-9000000001'});
    server = FakeServer();
  });

  test('pulls server customers and confirmed transactions on open', () async {
    server.customers.add({'id': 'r1', 'name': 'Ramesh', 'created_at': '2026-11-20T10:00:00'});
    server.txs.addAll([
      {'id': 'a', 'customer_id': 'r1', 'type': 'CREDIT', 'amount': '340.00', 'created_at': '2026-11-20T10:00:00'},
      {'id': 'b', 'customer_id': 'r1', 'type': 'PAYMENT', 'amount': '200.50', 'created_at': '2026-11-20T11:00:00'},
    ]);
    final store = await openLoggedIn();
    expect(store.balanceOf('r1'), 13950, reason: '340.00 - 200.50, kept to the paisa');
  });

  test('new entry is pushed once, reusing the existing customer by name', () async {
    server.customers.add({'id': 'r1', 'name': 'Ramesh', 'created_at': '2026-11-20T10:00:00'});
    final store = await openLoggedIn();
    await store.addEntry(customerName: 'ramesh', type: EntryType.credit, paise: 5000);
    await store.flushed;
    await store.addEntry(customerName: 'Sita', type: EntryType.payment, paise: 2025);
    await store.flushed;

    expect(server.customers.map((c) => c['name']), ['Ramesh', 'Sita']);
    expect(server.txs, hasLength(2));
    expect(server.txs.first['customer_id'], 'r1');
    expect(server.txs.first['type'], 'CREDIT');
    expect(server.txs.last['type'], 'PAYMENT');
    expect(server.txs.last['amount'], '20.25');
  });

  test('entries saved offline are pushed on the next open', () async {
    server.down = true;
    final offline = await openLoggedIn();
    await offline.addEntry(customerName: 'Ramesh', type: EntryType.credit, paise: 7500);
    await offline.flushed;
    expect(offline.balanceOf(offline.customers.single.id), 7500, reason: 'still works offline');
    expect(server.txs, isEmpty);

    server.down = false;
    final online = await openLoggedIn();
    expect(server.txs.single['amount'], '75.00');
    expect(online.balanceOf(online.customers.single.id), 7500);
  });

  test('no saved token means the login screen', () async {
    SharedPreferences.setMockInitialValues({});
    expect(await ApiLedgerStore.open('http://x', client: server.client), isNull);
  });

  test('expired token: back to login, offline entries survive and go up after login', () async {
    server.down = true;
    final offline = await openLoggedIn();
    await offline.addEntry(customerName: 'Ramesh', type: EntryType.credit, paise: 100);
    await offline.flushed;

    server
      ..down = false
      ..validToken = 'renewed';
    expect(await ApiLedgerStore.open('http://x', client: server.client), isNull);
    expect(server.txs, isEmpty, reason: 'nothing sent with the expired token');

    server.validToken = 't-9000000001';
    final store = await signIn('9000000001', 'pw1');
    expect(server.txs.single['amount'], '1.00');
    expect(store.unsyncedCount, 0);
  });

  test('wrong password shows the server message', () async {
    await expectLater(
      signIn('9000000001', 'nope'),
      throwsA(isA<ApiException>().having((e) => e.message, 'message', 'Invalid mobile number or password')),
    );
  });

  test('logout is refused while entries are only on the phone', () async {
    server.down = true;
    final store = await openLoggedIn();
    await store.addEntry(customerName: 'Ramesh', type: EntryType.credit, paise: 100);
    await store.flushed;
    expect(await store.logout(), 1);

    server.down = false;
    expect(await store.logout(), 0, reason: 'pushed, then logged out');
    expect(server.txs, hasLength(1));
    expect(store.entries, isEmpty);
    expect(await ApiLedgerStore.open('http://x', client: server.client), isNull);
  });

  test("another account's unsynced entries are never pushed into this one", () async {
    server.down = true;
    final store = await openLoggedIn();
    await store.addEntry(customerName: 'Ramesh', type: EntryType.credit, paise: 100);
    await store.flushed;
    server
      ..down = false
      ..validToken = 't-9000000002';

    await expectLater(signIn('9000000002', 'pw2'), throwsA(isA<ApiException>()));
    expect(server.txs, isEmpty);
  });

  test('a phone-only ledger is adopted by the first account', () async {
    SharedPreferences.setMockInitialValues({
      'bolkhata_ledger_v1': jsonEncode({
        'customers': [{'id': 'l1', 'name': 'Ramesh', 'createdAt': '2026-11-20T10:00:00.000'}],
        'entries': [{'id': 'e1', 'customerId': 'l1', 'type': 'credit', 'amount': 340, 'createdAt': '2026-11-20T10:00:00.000'}],
      }),
    });
    await signIn('9000000001', 'pw1');
    expect(server.txs.single['amount'], '340.00');
  });
}
