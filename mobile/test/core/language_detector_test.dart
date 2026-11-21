import 'package:bolkhata/core/language_detector.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  String? d(String s) => LanguageDetector.detect(s);

  test('native scripts', () {
    expect(d('रमेश ने 340 उधार लिया'), 'hi');
    expect(d('हाँ'), 'hi', reason: 'script is clear even for one word');
    expect(d('ರಮೇಶ್ 340 ಸಾಲ ತಗೊಂಡರು'), 'kn');
    expect(d('రమేష్ 340 అప్పు తీసుకున్నారు'), 'te');
    expect(d('ரமேஷ் 340 கடன் வாங்கினார்'), 'ta');
  });

  test('romanised Hindi and English', () {
    expect(d('Ramesh ne 340 udhaar liya'), 'hi');
    expect(d('Ramesh ka balance kitna hai'), 'hi');
    expect(d('Ramesh took 340 on credit'), 'en');
    expect(d('how much does Ramesh owe'), 'en');
  });

  test('romanised Kannada, Telugu, Tamil', () {
    expect(d('Ramesh 340 saala tagondru'), 'kn');
    expect(d('Ramesh 340 appu teesukunnaru'), 'te');
    expect(d('Ramesh 340 kadan vaanginar'), 'ta');
  });

  test('no clear signal keeps the current language', () {
    expect(d('340'), isNull);
    expect(d('yes'), isNull);
    expect(d('Ramesh'), isNull);
    expect(d('Ramesh 340'), isNull);
    expect(d(''), isNull);
  });
}
