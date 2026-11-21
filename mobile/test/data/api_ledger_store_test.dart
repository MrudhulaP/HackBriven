import 'dart:convert';

import 'package:bolkhata/core/models.dart';
import 'package:bolkhata/data/api_ledger_store.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Just enough of the FastAPI backend to exercise sync.
class FakeServer {
  final customers = <Map<String, dynamic>>[];
  final txs = <Map<String, dynamic>>[];
  bool down = false;

  late final client = MockClient((req) async {
    if (down) throw http.ClientException('offline');
    final path = req.url.path;
    Map<String, dynamic> body() => jsonDecode(req.body) as Map<String, dynamic>;
    if (path == '/api/auth/demo') return _json({'access_token': 't'});
    if (req.headers['Authorization'] != 'Bearer t') return http.Response('', 401);
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
      final t = {...b, 'id': 't${txs.length}', 'amount': '${b['amount']}.00', 'created_at': '2026-11-21T10:00:00'};
      txs.add(t);
      return _json(t, 201);
    }
    return http.Response('not found', 404);
  });

  http.Response _json(Object o, [int status = 200]) => http.Response(jsonEncode(o), status);
}

void main() {
  late FakeServer server;

  setUp(() {
    SharedPreferences.setMockInitialValues({});
    server = FakeServer();
  });

  test('pulls server customers and confirmed transactions on open', () async {
    server.customers.add({'id': 'r1', 'name': 'Ramesh', 'created_at': '2026-11-20T10:00:00'});
    server.txs.addAll([
      {'id': 'a', 'customer_id': 'r1', 'type': 'CREDIT', 'amount': '340.00', 'created_at': '2026-11-20T10:00:00'},
      {'id': 'b', 'customer_id': 'r1', 'type': 'PAYMENT', 'amount': '200.00', 'created_at': '2026-11-20T11:00:00'},
    ]);
    final store = await ApiLedgerStore.open('http://x', client: server.client);
    expect(store.balanceOf('r1'), 140);
  });

  test('new entry is pushed once, reusing the existing customer by name', () async {
    server.customers.add({'id': 'r1', 'name': 'Ramesh', 'created_at': '2026-11-20T10:00:00'});
    final store = await ApiLedgerStore.open('http://x', client: server.client);
    await store.addEntry(customerName: 'ramesh', type: EntryType.credit, amount: 50);
    await store.flushed;
    await store.addEntry(customerName: 'Sita', type: EntryType.payment, amount: 20);
    await store.flushed;

    expect(server.customers.map((c) => c['name']), ['Ramesh', 'Sita']);
    expect(server.txs, hasLength(2));
    expect(server.txs.first['customer_id'], 'r1');
    expect(server.txs.first['type'], 'CREDIT');
    expect(server.txs.last['type'], 'PAYMENT');
  });

  test('entries saved offline are pushed on the next open', () async {
    server.down = true;
    final offline = await ApiLedgerStore.open('http://x', client: server.client);
    await offline.addEntry(customerName: 'Ramesh', type: EntryType.credit, amount: 75);
    await offline.flushed;
    expect(offline.balanceOf(offline.customers.single.id), 75, reason: 'still works offline');
    expect(server.txs, isEmpty);

    server.down = false;
    final online = await ApiLedgerStore.open('http://x', client: server.client);
    expect(server.txs.single['amount'], '75.00');
    expect(online.balanceOf(online.customers.single.id), 75);
  });
}
