import 'package:smartfeed_app/offline/copy.dart';
import 'package:smartfeed_app/offline/cv_mould.dart';
import 'package:smartfeed_app/offline/nutrition.dart';
import 'package:smartfeed_app/offline/screens.dart';
import 'package:smartfeed_app/offline/sensors.dart';

const severity = {'feed': 0, 'dilute': 1, 'reject': 2};

Map<String, dynamic> decide(Map<String, dynamic> parts) {
  final triggers = <(String, String)>[];
  final urea = Map<String, dynamic>.from(parts['urea'] as Map);
  if (urea['over_bis'] == true) {
    triggers.add(('reject', 'urea at or above BIS 1%'));
  } else if (urea['suspect'] == true) {
    triggers.add(('dilute', '4-DMAB yellow — suspect urea'));
  }
  final cv = Map<String, dynamic>.from(parts['cv'] as Map);
  if (cv['flag'] == true) triggers.add(('reject', 'visible mould'));

  final silage = Map<String, dynamic>.from(parts['silage'] as Map);
  if (silage['present'] == true) {
    if (silage['class'] == 'poor') {
      triggers.add(('reject', 'silage Flieg ${silage['flieg_score']} poor'));
    } else if (silage['class'] == 'moderate') {
      triggers.add(('dilute', 'silage Flieg ${silage['flieg_score']} moderate'));
    }
    final flags = List<String>.from(silage['flags'] ?? const []);
    if (flags.contains('high_pH_low_DM')) {
      triggers.add(('dilute', 'silage pH ${silage['pH']} above 4.2 on low DM'));
    }
  }

  final moistFlags = List<String>.from((parts['moisture'] as Map)['flags'] ?? const []);
  if (moistFlags.contains('above_bis_moisture_max_11')) {
    triggers.add(('dilute', 'compounded-feed moisture above BIS 11%'));
  }
  if (moistFlags.contains('silage_too_wet_risk_effluent')) {
    triggers.add(('dilute', 'silage too wet — effluent and clostridia risk'));
  }

  final sand = Map<String, dynamic>.from(parts['sand'] as Map);
  if (sand['over_bis'] == true) {
    triggers.add(('reject', 'acid-insoluble ash above the BIS sand limit'));
  } else if (sand['suspect'] == true) {
    triggers.add(('dilute', 'grit settled in the jar test — suspect sand'));
  }

  if ((parts['aflatoxin'] as Map)['high_risk_ingredient'] == true && cv['flag'] == true) {
    triggers.add(('reject', 'high-AF-risk ingredient plus mould'));
  }

  if (triggers.isEmpty) {
    return {'action': 'feed', 'reasons': ['no reject/dilute trigger from sensors + tables']};
  }
  final action = triggers.map((t) => t.$1).reduce((a, b) => (severity[a] ?? 0) >= (severity[b] ?? 0) ? a : b);
  final reasons = [for (final t in triggers) if (t.$1 == action) t.$2];
  final downgraded = [for (final t in triggers) if (t.$1 != action) t.$2];
  return {
    'action': action,
    'reasons': reasons,
    if (downgraded.isNotEmpty) 'other_flags': downgraded,
  };
}

Future<Map<String, dynamic>> assess({
  required String ingredient,
  String? form,
  double? moisturePct,
  double? ph,
  double? ureaYellowAreaPct,
  bool? visibleMould,
  String? imagePath,
  List<double>? nirAbsorbance,
  double? aiaPct,
  double? gritSettledMl,
  double? sampleG,
}) async {
  final sensorWarnings = checkAll({
    'moisture_pct': moisturePct,
    'ph': ph,
    'urea_yellow_area_pct': ureaYellowAreaPct,
    'aia_pct': aiaPct,
    'grit_settled_ml': gritSettledMl,
    'sample_g': sampleG,
  });
  final nutrition = assessNutrition(ingredient, moisturePct: moisturePct, form: form);
  final moisture = assessMoisture(moisturePct, form: form);
  final silage = (form == 'silage' || ph != null)
      ? assessSilage(ph, moisturePct, ingredient)
      : {'present': false, 'note': 'Not scored as silage.'};
  final urea = assessUrea(ureaYellowAreaPct, ingredient);
  final cv = assessImage(imagePath: imagePath, visibleMould: visibleMould);
  final mouldFlag = cv['present'] == true ? cv['flag'] as bool? : visibleMould;
  final aflatoxin = assessAflatoxin(ingredient, visibleMould: mouldFlag);
  final nir = assessNir(nirAbsorbance);
  final sand = assessSand(aiaPct: aiaPct, gritSettledMl: gritSettledMl, sampleG: sampleG, form: form);
  final parts = {
    'nutrition': nutrition,
    'moisture': moisture,
    'silage': silage,
    'urea': urea,
    'cv': cv,
    'aflatoxin': aflatoxin,
    'sand': sand,
    'nir': nir,
  };
  final decision = decide(parts);
  final farmer = farmerCard(decision);
  final ration = rationAdvice(nutrition);
  final out = <String, dynamic>{
    'offline': true,
    'ingredient': ingredient,
    'form': form,
    'decision': decision,
    'farmer': farmer,
    'ration': ration,
    'sensor_warnings': sensorWarnings,
    'modules': parts,
    'disclaimer':
        'Village kit on this phone: lookup + moisture + pH + 4-DMAB + mould screen + AIA sand check. '
        'NIR CP is only valid on the Brazilian forage matrix, not AS7265x. ExtraTrees / CNN stay in the notebooks.',
  };
  out['spoken'] = spokenAdvice(out);
  return out;
}
