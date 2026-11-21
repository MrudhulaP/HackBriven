import 'package:flutter/material.dart';

import 'core/ledger_store.dart';
import 'data/api_ledger_store.dart';
import 'data/prefs_ledger_store.dart';
import 'ui/home_screen.dart';
import 'ui/login_screen.dart';

// e.g. --dart-define=BOLKHATA_API_URL=http://10.0.2.2:8000 (Android emulator). Unset = phone-only ledger.
const apiUrl = String.fromEnvironment('BOLKHATA_API_URL');

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  // null = logged out, so the login screen shows.
  final LedgerStore? store =
      apiUrl.isEmpty ? await PrefsLedgerStore.open() : await ApiLedgerStore.open(apiUrl);
  runApp(BolKhataApp(store: store));
}

class BolKhataApp extends StatefulWidget {
  final LedgerStore? store;

  const BolKhataApp({super.key, required this.store});

  @override
  State<BolKhataApp> createState() => _BolKhataAppState();
}

class _BolKhataAppState extends State<BolKhataApp> {
  late LedgerStore? _store = widget.store;

  @override
  Widget build(BuildContext context) {
    final store = _store;
    return MaterialApp(
      title: 'BolKhata',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(colorSchemeSeed: Colors.teal, useMaterial3: true),
      home: store == null
          ? LoginScreen(apiUrl: apiUrl, onLoggedIn: (s) => setState(() => _store = s))
          : HomeScreen(
              key: ObjectKey(store),
              store: store,
              onLogout: store is ApiLedgerStore
                  ? () async {
                      final left = await store.logout();
                      if (left == 0) setState(() => _store = null);
                      return left;
                    }
                  : null,
            ),
    );
  }
}
