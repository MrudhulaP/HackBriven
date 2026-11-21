// BolKhata core models. Pure Dart: no Flutter imports allowed in lib/core/.

enum EntryType { credit, payment }

class Customer {
  final String id;
  final String name;
  final DateTime createdAt;

  const Customer({
    required this.id,
    required this.name,
    required this.createdAt,
  });

  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'createdAt': createdAt.toIso8601String(),
      };

  factory Customer.fromJson(Map<String, dynamic> j) => Customer(
        id: j['id'] as String,
        name: j['name'] as String,
        createdAt: DateTime.parse(j['createdAt'] as String),
      );
}

class LedgerEntry {
  final String id;
  final String customerId;
  final EntryType type;

  /// In paise (₹1 = 100). Always > 0. Never use double for money.
  final int paise;
  final DateTime createdAt;

  /// What the shopkeeper actually said or typed.
  final String? rawText;

  const LedgerEntry({
    required this.id,
    required this.customerId,
    required this.type,
    required this.paise,
    required this.createdAt,
    this.rawText,
  });

  Map<String, dynamic> toJson() => {
        'id': id,
        'customerId': customerId,
        'type': type.name,
        'paise': paise,
        'createdAt': createdAt.toIso8601String(),
        'rawText': rawText,
      };

  factory LedgerEntry.fromJson(Map<String, dynamic> j) => LedgerEntry(
        id: j['id'] as String,
        customerId: j['customerId'] as String,
        type: EntryType.values.byName(j['type'] as String),
        // Caches written before paise existed stored whole rupees under 'amount'.
        paise: j['paise'] as int? ?? (j['amount'] as int) * 100,
        createdAt: DateTime.parse(j['createdAt'] as String),
        rawText: j['rawText'] as String?,
      );
}

/// 34050 -> "340.50", 34000 -> "340", -2000 -> "-20". For showing and speaking.
String formatRupees(int paise) {
  final a = paise.abs();
  final p = a % 100;
  final s = p == 0 ? '${a ~/ 100}' : '${a ~/ 100}.${p.toString().padLeft(2, '0')}';
  return paise < 0 ? '-$s' : s;
}

/// 34050 -> "340.50". Exact decimal string for the backend.
String paiseToDecimal(int paise) =>
    '${paise ~/ 100}.${(paise % 100).toString().padLeft(2, '0')}';

/// "340.5" / "340.50" / 340 -> 34050. Parses the string, never via double.
int paiseFromDecimal(Object value) {
  final parts = '$value'.trim().split('.');
  final frac = parts.length > 1 ? '${parts[1]}00'.substring(0, 2) : '00';
  return int.parse(parts[0]) * 100 + int.parse(frac);
}
