import 'package:bolkhata/core/models.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('formatRupees', () {
    expect(formatRupees(34000), '340');
    expect(formatRupees(34050), '340.50');
    expect(formatRupees(5), '0.05');
    expect(formatRupees(-2000), '-20');
  });

  test('decimal strings round-trip exactly', () {
    expect(paiseFromDecimal('340.50'), 34050);
    expect(paiseFromDecimal('340.5'), 34050);
    expect(paiseFromDecimal('340'), 34000);
    expect(paiseFromDecimal(340), 34000);
    expect(paiseFromDecimal('0.07'), 7);
    expect(paiseToDecimal(34050), '340.50');
    expect(paiseToDecimal(7), '0.07');
  });

  test('old rupee caches load as paise', () {
    final e = LedgerEntry.fromJson({
      'id': '1', 'customerId': 'c', 'type': 'credit', 'amount': 340,
      'createdAt': '2026-11-20T10:00:00.000',
    });
    expect(e.paise, 34000);
    expect(LedgerEntry.fromJson(e.toJson()).paise, 34000);
  });
}
