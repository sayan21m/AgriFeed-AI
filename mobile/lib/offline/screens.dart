import 'package:smartfeed_app/offline/names.dart';
import 'package:smartfeed_app/offline/sensors.dart';
import 'package:smartfeed_app/offline/tables.dart';

Map<String, dynamic> classifyFlieg(double score) {
  for (final rec in OfflineKit.instance.flieg) {
    if (rec.minScore <= score && score <= rec.maxScore) {
      return {'class': rec.klass, 'advice': rec.advice};
    }
  }
  return {'class': 'unknown', 'advice': 'Score out of table range.'};
}

Map<String, dynamic> assessSilage(double? ph, double? moisturePct, String? ingredient) {
  if (ph == null) {
    return {'present': false, 'note': 'Silage needs a pocket pH. Spectra and photos cannot replace it.'};
  }
  final dm = moisturePct == null ? null : 100.0 - moisturePct;
  final out = <String, dynamic>{
    'present': true,
    'pH': ph,
    'dm_pct': dm == null ? null : double.parse(dm.toStringAsFixed(2)),
    'formula': fliegFormula,
    'kaur_punjab_farmer_n100': 'median pH 3.99, Flieg 104 (summary, not raw pits)',
  };
  final flags = <String>[];
  if (ph > 4.2 && (dm == null || dm < 30)) flags.add('high_pH_low_DM');
  if (dm == null) {
    out['flieg'] = null;
    out['note'] = 'Have pH but no moisture, so Flieg is incomplete.';
    out['flags'] = flags;
    return out;
  }
  final score = fliegScore(dm, ph);
  out.addAll({'flieg_score': double.parse(score.toStringAsFixed(1)), ...classifyFlieg(score), 'flags': flags});
  if (ingredient != null) out['ingredient'] = ingredient;
  return out;
}

UreaSlope _ureaFor(String ingredient) {
  final text = normalizeName(ingredient);
  String? label;
  const table = {
    'soybean meal': 'Soyabean meal',
    'soyabean meal': 'Soyabean meal',
    'groundnut cake': 'Groundnut cake',
    'cottonseed cake undecorticated': 'Un-decorticated cottonseed cake',
    'cottonseed cake': 'Un-decorticated cottonseed cake',
  };
  for (final entry in table.entries) {
    if (text.contains(entry.key)) {
      label = entry.value;
      break;
    }
  }
  final slopes = OfflineKit.instance.urea;
  UreaSlope? glob;
  for (final s in slopes) {
    if (label != null && s.cakeLabel == label) return s;
    if (s.key == 'global') glob = s;
  }
  return glob ?? slopes.last;
}

Map<String, dynamic> assessUrea(double? yellowAreaPct, String? ingredient) {
  if (yellowAreaPct == null) {
    return {'present': false, 'note': 'No 4-DMAB / foldscope yellow area. Urea is not visible on AS7265x.'};
  }
  final curve = _ureaFor(ingredient ?? '');
  final area = yellowAreaPct;
  var gPerKg = curve.intercept + curve.slope * area;
  if (gPerKg < 0) gPerKg = 0;
  var pct = gPerKg / 10.0;
  final extrapolated = area < curve.yellowLo || area > curve.yellowHi;
  if (area > curve.yellowHi) {
    gPerKg = curve.intercept + curve.slope * curve.yellowHi;
    if (gPerKg < 0) gPerKg = 0;
    pct = gPerKg / 10.0;
  }
  return {
    'present': true,
    'yellow_area_pct': area,
    'cake_curve': curve.cakeLabel ?? '__global__',
    'calibration_range_pct': [double.parse(curve.yellowLo.toStringAsFixed(2)), double.parse(curve.yellowHi.toStringAsFixed(2))],
    'extrapolated': extrapolated,
    'urea_g_per_kg': double.parse(gPerKg.toStringAsFixed(2)),
    'urea_pct_approx': double.parse(pct.toStringAsFixed(2)),
    'urea_pct_is_lower_bound': area > curve.yellowHi,
    'bis_max_pct': 1.0,
    'over_bis': pct >= 1.0 || area > curve.yellowHi,
    'suspect': area >= curve.yellowLo,
    'note':
        'Colour-area screen from Anitha 2022 (1-10 g/kg urea), not a Kjeldahl assay. Any yellow on a pure cake means added urea.',
  };
}

const gritScreenMlPer100g = 2.0;

Map<String, dynamic> assessSand({
  double? aiaPct,
  double? gritSettledMl,
  double? sampleG,
  String? form,
}) {
  final kit = OfflineKit.instance;
  final aia = kit.bis['Acid insoluble ash'] as Map;
  final limits = {'type_I_max': (aia['type_I'] as num).toDouble(), 'type_II_max': (aia['type_II'] as num).toDouble()};
  final limit = form == 'compounded' ? limits['type_I_max']! : limits['type_II_max']!;
  if (aiaPct == null && gritSettledMl == null) {
    return {
      'present': false,
      'bis_aia_max_pct': limits,
      'note': 'No AIA % and no settling-jar reading. Sand cannot be seen by NIR or a photo.',
    };
  }
  final out = <String, dynamic>{
    'present': true,
    'bis_aia_max_pct': limits,
    'limit_applied_pct': limit,
    'note': 'AIA is the BIS test for sand/silica. The jar test only screens for it.',
  };
  if (aiaPct != null) {
    out['aia_pct'] = aiaPct;
    out['method'] = 'measured_aia';
    out['over_bis'] = aiaPct > limit;
    out['suspect'] = out['over_bis'];
    return out;
  }
  final grit = gritSettledMl!;
  out['method'] = 'settling_jar_screen';
  out['grit_settled_ml'] = grit;
  out['over_bis'] = false;
  if (sampleG != null) {
    final per100 = grit * 100.0 / sampleG;
    out['grit_ml_per_100g'] = double.parse(per100.toStringAsFixed(2));
    out['suspect'] = per100 >= gritScreenMlPer100g;
  } else {
    out['suspect'] = grit > 0;
    out['note'] = '${out['note']} Give sample_g to normalise the jar reading.';
  }
  if (out['suspect'] == true) {
    out['next_step'] = 'Send a sample for acid-insoluble ash before accepting the lot.';
  }
  return out;
}

const _afAliases = {
  'cattle feed': 'Cattle feed',
  'compounded feed': 'Cattle feed',
  'compounded': 'Cattle feed',
  'cottonseed': 'Cotton seed cake',
  'groundnut': 'Groundnut cake',
  'soybean': 'Soyabean cake',
  'soyabean': 'Soyabean cake',
  'maize': 'Maize',
  'wheat bran': 'Wheat bran',
  'deoiled rice bran': 'Deoiled rice bran',
  'dorb': 'Deoiled rice bran',
};

String? _matchAfItem(String ingredient) {
  final text = normalizeName(ingredient);
  if (text.contains('silage')) return null;
  for (final entry in _afAliases.entries) {
    if (text.contains(entry.key)) return entry.value;
  }
  return null;
}

Map<String, dynamic> assessAflatoxin(String ingredient, {bool? visibleMould}) {
  final item = _matchAfItem(ingredient);
  KotinaguRow? row;
  if (item != null) {
    for (final r in OfflineKit.instance.kotinagu) {
      if (r.item == item) {
        row = r;
        break;
      }
    }
  }
  var highRisk = item == 'Groundnut cake' || item == 'Maize' || item == 'Cotton seed cake' || item == 'Soyabean cake';
  if (visibleMould == true) highRisk = true;
  return {
    'present': true,
    'matched_item': item,
    'historical': row == null
        ? null
        : {
            'n_analyzed': row.nAnalyzed,
            'incidence_pct': row.incidencePct,
            'mean_ppb_in_positives': row.meanPpb,
            'range_ppb': row.rangePpb,
          },
    'bis_afb1_max_ug_kg': 20.0,
    'high_risk_ingredient': highRisk,
    'visible_mould': visibleMould,
    'note':
        'Kotinagu 2015 AP/Telangana incidence. This is not this-bag µg/kg. Need a lateral-flow strip or a lab for AFB1.',
  };
}

Map<String, dynamic> assessNir(List<double>? absorbance) {
  if (absorbance == null) return {'present': false, 'note': 'No spectrum.'};
  if (absorbance.length == 18) {
    return {
      'present': true,
      'used': false,
      'note':
          'Got 18 AS7265x channels. No Indian paired calibration exists. Not scoring CP from this chip.',
    };
  }
  return {
    'present': true,
    'used': false,
    'note': 'Need 256 bands (890–1707 nm) or 18 AS7265x channels, got ${absorbance.length}. Brazilian PLS is not on this phone.',
  };
}
