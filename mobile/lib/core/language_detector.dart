// Guesses which of the 5 app languages an utterance is in. Pure Dart: no Flutter imports.
// Native script decides at once. Romanised text (what the phone recognizer
// often returns, e.g. "Ramesh ne 340 udhaar liya") is decided by marker words.
// Returns null when there is no clear signal, so the caller keeps the current language.

class LanguageDetector {
  static const Map<String, (int, int)> _scripts = {
    'hi': (0x0900, 0x097F), // Devanagari
    'ta': (0x0B80, 0x0BFF),
    'te': (0x0C00, 0x0C7F),
    'kn': (0x0C80, 0x0CFF),
  };

  /// Romanised words that only make sense in one language.
  static const Map<String, Set<String>> _markers = {
    'hi': {
      'ne', 'se', 'ko', 'ka', 'ki', 'ke', 'udhaar', 'udhar', 'udhari', 'liya',
      'liye', 'diya', 'diye', 'jama', 'chukaya', 'wapas', 'waapas', 'mila',
      'mile', 'kitna', 'kitne', 'kitni', 'bakaya', 'hisab', 'hisaab', 'haan',
      'nahi', 'nahin', 'hai', 'tha', 'thi', 'rupaye', 'aaj', 'kal', 'abhi',
      'kiya', 'kiye', 'likho', 'theek', 'sahi', 'galat', 'mat', 'mujhe', 'maine',
    },
    'kn': {
      'saala', 'kotta', 'kottaru', 'eshtu', 'houdu', 'haudu', 'illa', 'beda',
      'rupayi', 'baaki', 'avaru', 'ide',
    },
    'te': {
      'appu', 'ichcharu', 'ichchadu', 'entha', 'avunu', 'kaadu', 'vaddu',
      'sare', 'rupayalu', 'baakee',
    },
    'ta': {
      'kadan', 'evvalavu', 'baakki', 'aamaa', 'aama', 'illai', 'venam',
      'vendam', 'seri', 'roobai',
    },
    'en': {
      'took', 'borrowed', 'owes', 'owe', 'paid', 'gave', 'returned',
      'deposited', 'how', 'much', 'what', 'the', 'is', 'has', 'yes', 'no',
      'rupees', 'outstanding', 'credit', 'payment', 'cancel',
    },
  };

  /// Romanised verb stems that take suffixes (tagondru, teesukunnaru, ...).
  static const Map<String, List<String>> _stems = {
    'kn': ['tagond', 'kottid'],
    'te': ['teesukunn', 'chellinch', 'ichch'],
    'ta': ['vaangin', 'koduth', 'kattin'],
  };

  static String? detect(String text) {
    // 1. Native script: count letters per script, take the biggest.
    final counts = <String, int>{};
    for (final r in text.runes) {
      for (final MapEntry(key: lang, value: (lo, hi)) in _scripts.entries) {
        if (r >= lo && r <= hi) counts[lang] = (counts[lang] ?? 0) + 1;
      }
    }
    if (counts.isNotEmpty) return _best(counts);

    // 2. Romanised: count marker words. A single word ("yes", "340", "Ramesh")
    // is too little to switch on, so it keeps the current language.
    final words = text
        .toLowerCase()
        .split(RegExp(r'[^a-z]+'))
        .where((w) => w.isNotEmpty)
        .toList();
    if (words.length < 2) return null;
    final scores = <String, int>{};
    for (final w in words) {
      for (final MapEntry(key: lang, value: set) in _markers.entries) {
        if (set.contains(w)) scores[lang] = (scores[lang] ?? 0) + 1;
      }
      for (final MapEntry(key: lang, value: stems) in _stems.entries) {
        if (stems.any(w.startsWith)) scores[lang] = (scores[lang] ?? 0) + 1;
      }
    }
    return _best(scores);
  }

  /// The top scorer, or null on an empty map or a tie.
  static String? _best(Map<String, int> scores) {
    if (scores.isEmpty) return null;
    final sorted = scores.entries.toList()..sort((a, b) => b.value.compareTo(a.value));
    if (sorted.length > 1 && sorted[0].value == sorted[1].value) return null;
    return sorted.first.key;
  }
}
