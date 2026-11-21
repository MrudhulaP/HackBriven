import 'package:flutter/material.dart';

import '../data/api_ledger_store.dart';
import '../l10n/languages.dart';
import '../l10n/prompts.dart';

/// Shopkeeper login / sign-up against the backend's /api/auth.
class LoginScreen extends StatefulWidget {
  final String apiUrl;
  final void Function(ApiLedgerStore store) onLoggedIn;

  const LoginScreen({super.key, required this.apiUrl, required this.onLoggedIn});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _mobile = TextEditingController();
  final _password = TextEditingController();
  final _name = TextEditingController();
  final _shop = TextEditingController();
  AppLanguage _lang = kLanguages.first;
  bool _register = false;
  bool _busy = false;
  String? _error;

  String _t(String key) => Prompts.render(_lang.code, key);

  @override
  void dispose() {
    for (final c in [_mobile, _password, _name, _shop]) {
      c.dispose();
    }
    super.dispose();
  }

  Future<void> _submit() async {
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      final store = await ApiLedgerStore.signIn(
        widget.apiUrl,
        register: _register,
        fields: {
          'mobile': _mobile.text.trim(),
          'password': _password.text,
          if (_register) ...{
            'name': _name.text.trim(),
            'shop_name': _shop.text.trim(),
            'preferred_language': _lang.code,
          },
        },
      );
      widget.onLoggedIn(store);
    } on ApiException catch (e) {
      setState(() => _error = e.message);
    } catch (_) {
      setState(() => _error = _t('uiNoServer'));
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Widget _field(TextEditingController c, String label,
          {bool obscure = false, TextInputType? keyboard}) =>
      Padding(
        padding: const EdgeInsets.only(bottom: 12),
        child: TextField(
          controller: c,
          obscureText: obscure,
          keyboardType: keyboard,
          decoration: InputDecoration(labelText: label, border: const OutlineInputBorder()),
        ),
      );

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('BolKhata'),
        actions: [
          DropdownButton<AppLanguage>(
            value: _lang,
            underline: const SizedBox.shrink(),
            items: [
              for (final l in kLanguages) DropdownMenuItem(value: l, child: Text(l.label)),
            ],
            onChanged: (l) {
              if (l != null) setState(() => _lang = l);
            },
          ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: AutofillGroup(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                if (_register) ...[
                  _field(_name, _t('uiYourName')),
                  _field(_shop, _t('uiShopName')),
                ],
                _field(_mobile, _t('uiMobile'), keyboard: TextInputType.phone),
                _field(_password, _t('uiPassword'), obscure: true),
                if (_error != null)
                  Padding(
                    padding: const EdgeInsets.only(bottom: 12),
                    child: Text(_error!,
                        style: TextStyle(color: Theme.of(context).colorScheme.error)),
                  ),
                FilledButton(
                  onPressed: _busy ? null : _submit,
                  child: _busy
                      ? const SizedBox.square(
                          dimension: 20, child: CircularProgressIndicator(strokeWidth: 2))
                      : Text(_register ? _t('uiRegister') : _t('uiLogin')),
                ),
                TextButton(
                  onPressed: _busy
                      ? null
                      : () => setState(() {
                            _register = !_register;
                            _error = null;
                          }),
                  child: Text(_register ? _t('uiHaveAccount') : _t('uiNewShop')),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
