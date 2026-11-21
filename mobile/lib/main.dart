import 'package:flutter/material.dart';

import 'core/ledger_store.dart';
import 'data/api_ledger_store.dart';
import 'data/prefs_ledger_store.dart';
import 'ui/home_screen.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  // e.g. --dart-define=BOLKHATA_API_URL=http://10.0.2.2:8000 (Android emulator). Unset = phone-only ledger.
  const apiUrl = String.fromEnvironment('BOLKHATA_API_URL');
  final LedgerStore store =
      apiUrl.isEmpty ? await PrefsLedgerStore.open() : await ApiLedgerStore.open(apiUrl);
  runApp(BolKhataApp(store: store));
}

class BolKhataApp extends StatelessWidget {
  final LedgerStore store;

  const BolKhataApp({super.key, required this.store});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'BolKhata',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(colorSchemeSeed: Colors.teal, useMaterial3: true),
      home: HomeScreen(store: store),
    );
  }
}
