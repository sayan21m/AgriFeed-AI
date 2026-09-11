import 'package:flutter_test/flutter_test.dart';
import 'package:smartfeed_app/offline/pipeline.dart';
import 'package:smartfeed_app/offline/qr.dart';
import 'package:smartfeed_app/offline/screens.dart';
import 'package:smartfeed_app/offline/sensors.dart';
import 'package:smartfeed_app/offline/tables.dart';

Future<void> _load() async {
  await OfflineKit.load();
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUpAll(_load);

  test('mustard cake is feed from Indian tables', () async {
    final out = await assess(ingredient: 'mustard cake', moisturePct: 10);
    expect(out['decision']['action'], 'feed');
    expect(out['modules']['nutrition']['method'], 'indian_table_lookup');
    expect(out['farmer']['label_hi'], 'खिलाएँ');
    expect(out['offline'], isTrue);
  });

  test('wet compounded feed is dilute', () async {
    final out = await assess(ingredient: 'cattle feed', form: 'compounded', moisturePct: 16);
    expect(out['decision']['action'], 'dilute');
  });

  test('visible mould rejects', () async {
    final out = await assess(ingredient: 'groundnut cake', visibleMould: true);
    expect(out['decision']['action'], 'reject');
  });

  test('Flieg formula', () {
    expect((fliegScore(30, 4.0) - 105.0).abs(), lessThan(1e-6));
  });

  test('AS7265x is not used for CP', () async {
    final out = await assess(ingredient: 'wheat bran', nirAbsorbance: List.filled(18, 0.1));
    expect(out['modules']['nir']['used'], isFalse);
    expect(out['spoken']['en'], contains('18'));
  });

  test('worst trigger wins', () async {
    final out = await assess(
      ingredient: 'groundnut cake',
      visibleMould: true,
      moisturePct: 20,
      ureaYellowAreaPct: 20,
    );
    expect(out['decision']['action'], 'reject');
    expect(out['decision']['other_flags'], isNotEmpty);
  });

  test('urea above calibration is a lower bound', () {
    final r = assessUrea(95.0, 'groundnut cake');
    expect(r['extrapolated'], isTrue);
    expect(r['urea_pct_is_lower_bound'], isTrue);
    expect(r['over_bis'], isTrue);
    expect((r['urea_g_per_kg'] as num) <= 10.5, isTrue);
  });

  test('AIA above BIS rejects', () async {
    final out = await assess(ingredient: 'cattle feed', form: 'compounded', aiaPct: 4.0);
    expect(out['modules']['sand']['over_bis'], isTrue);
    expect(out['decision']['action'], 'reject');
  });

  test('jar test only suspects', () {
    final r = assessSand(gritSettledMl: 5.0, sampleG: 100.0);
    expect(r['suspect'], isTrue);
    expect(r['over_bis'], isFalse);
  });

  test('silage does not inherit maize grain AF risk', () {
    expect(assessAflatoxin('maize silage')['matched_item'], isNull);
    expect(assessAflatoxin('maize')['matched_item'], 'Maize');
  });

  test('high pH wet silage is not feed', () async {
    final out = await assess(ingredient: 'maize silage', form: 'silage', ph: 5.2, moisturePct: 78);
    expect(out['decision']['action'], 'dilute');
  });

  test('impossible moisture raises', () async {
    await expectLater(
      assess(ingredient: 'mustard cake', moisturePct: 150),
      throwsA(isA<SensorRangeError>()),
    );
  });

  test('straw tells farmer to supplement', () async {
    final out = await assess(ingredient: 'wheat straw', moisturePct: 9);
    expect(out['decision']['action'], 'feed');
    expect((out['ration']['tips_en'] as List).join(' ').toLowerCase(), contains('below'));
  });

  test('sarson khali aliases to mustard cake', () async {
    final out = await assess(ingredient: 'sarson khali');
    expect(out['modules']['nutrition']['canonical'], 'mustard cake');
    expect(out['modules']['nutrition']['method'], 'indian_table_lookup');
  });

  test('unknown cake name uses keyword class, not ExtraTrees', () async {
    final out = await assess(ingredient: 'mystery oilcake xyz');
    expect(out['modules']['nutrition']['method'], 'keyword_class_fallback');
    expect(out['modules']['nutrition']['feed_class'], 'oilcakes');
  });

  test('QR valid bag stays feed', () async {
    final payload = encodeQrPayload(demoBag(kind: 'valid'));
    final out = await assess(ingredient: 'mustard cake', moisturePct: 10, qrPayload: payload);
    expect(out['modules']['qr']['verified'], isTrue);
    expect(out['decision']['action'], 'feed');
  });

  test('QR expired bag is dilute', () async {
    final payload = encodeQrPayload(demoBag(kind: 'expired'));
    final out = await assess(ingredient: 'mustard cake', moisturePct: 10, qrPayload: payload);
    expect(out['modules']['qr']['expired'], isTrue);
    expect(out['decision']['action'], 'dilute');
    expect((out['decision']['reasons'] as List).join(' '), contains('expiry'));
  });

  test('QR CP mismatch is dilute', () async {
    final payload = encodeQrPayload(demoBag(kind: 'mismatch'));
    final out = await assess(ingredient: 'mustard cake', moisturePct: 10, qrPayload: payload);
    expect(out['modules']['qr']['cp_mismatch'], isTrue);
    expect(out['decision']['action'], 'dilute');
  });
}
