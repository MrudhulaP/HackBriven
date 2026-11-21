// Saves the ledger as JSON in SharedPreferences.
// PROTOTYPE ONLY: not encrypted. Replace with SQLCipher after the demo.

import 'dart:convert';

import 'package:shared_preferences/shared_preferences.dart';

import '../core/ledger_store.dart';
import '../core/models.dart';

class PrefsLedgerStore extends LedgerStore {
  static const _key = 'bolkhata_ledger_v1';
  final SharedPreferences prefs;

  PrefsLedgerStore(this.prefs);

  static Future<PrefsLedgerStore> open() async =>
      PrefsLedgerStore(await SharedPreferences.getInstance())..loadCache();

  void loadCache() {
    final raw = prefs.getString(_key);
    if (raw != null) {
      final j = jsonDecode(raw) as Map<String, dynamic>;
      loadAll(
        (j['customers'] as List)
            .map((e) => Customer.fromJson(e as Map<String, dynamic>))
            .toList(),
        (j['entries'] as List)
            .map((e) => LedgerEntry.fromJson(e as Map<String, dynamic>))
            .toList(),
      );
    }
  }

  @override
  Future<void> persist() async {
    final data = {
      'customers': customers.map((c) => c.toJson()).toList(),
      'entries': entries.map((e) => e.toJson()).toList(),
    };
    await prefs.setString(_key, jsonEncode(data));
  }
}
