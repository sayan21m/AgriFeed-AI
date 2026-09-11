import 'package:smartfeed_app/offline/names.dart';
import 'package:smartfeed_app/offline/sensors.dart';
import 'package:smartfeed_app/offline/tables.dart';

Map<String, double?>? _span(FeedRow row, String stem) {
  final mean = row.value('${stem}_mean');
  if (mean == null) return null;
  return {
    'mean': double.parse(mean.toStringAsFixed(2)),
    'min': double.parse((row.value('${stem}_min') ?? mean).toStringAsFixed(2)),
    'max': double.parse((row.value('${stem}_max') ?? mean).toStringAsFixed(2)),
  };
}

Map<String, dynamic> assessNutrition(String ingredient, {double? moisturePct, String? form}) {
  final kit = OfflineKit.instance;
  final bis = kit.bis;
  var canonical = normalizeName(ingredient);
  if (form == 'silage' && !canonical.contains('silage')) {
    canonical = '$canonical silage';
  }
  if (form == 'compounded' || canonical == 'compounded feed') {
    final cp = bis['Crude protein'] as Map;
    final moist = bis['Moisture'] as Map;
    final urea = bis['Urea'] as Map;
    final af = bis['Aflatoxin B1'] as Map;
    return {
      'ingredient': ingredient,
      'canonical': canonical,
      'method': 'bis_standard_only',
      'feed_class': 'compounded',
      'bis_compounded_feed': {
        'type_I_cp_min': (cp['type_I'] as num).toDouble(),
        'type_II_cp_min': (cp['type_II'] as num).toDouble(),
        'moisture_max': (moist['type_I'] as num).toDouble(),
        'urea_max_pct': (urea['type_I'] as num).toDouble(),
        'afb1_max_ug_kg': (af['type_I'] as num).toDouble(),
      },
      'disclaimer': kit.disclaimer,
    };
  }

  var hit = kit.byCanonical[canonical];
  var match = 'exact';
  if (hit == null) {
    String? best;
    var bestRatio = 0.0;
    for (final name in kit.byCanonical.keys) {
      final r = sequenceRatio(canonical, name);
      if (r >= 0.82 && r > bestRatio) {
        bestRatio = r;
        best = name;
      }
    }
    if (best != null) {
      hit = kit.byCanonical[best];
      match = 'fuzzy:$best';
      canonical = best;
    }
  }

  String method;
  String feedClass;
  Map<String, Map<String, double?>?> nutrients;
  String? sources;
  int? nRows;

  if (hit != null) {
    moisturePct ??= hit.value('moisture_pct_mean');
    nutrients = {
      'crude_protein_pct_dm': _span(hit, 'cp_pct_dm'),
      'fibre_pct_dm': _span(hit, 'fibre_pct_dm'),
      'fat_ee_pct_dm': _span(hit, 'ee_pct_dm'),
      'energy_me_mcal_kg': _span(hit, 'me_mcal_kg'),
    };
    method = 'indian_table_lookup';
    feedClass = hit.feedClass;
    sources = hit.sources;
    nRows = hit.nRows;
  } else {
    feedClass = keywordClass(canonical);
    method = 'keyword_class_fallback';
    match = 'keyword';
    final cls = kit.classFor(feedClass);
    Map<String, double?>? cp;
    if (cls != null) {
      cp = {
        'mean': double.parse(cls.cpMean.toStringAsFixed(2)),
        'min': double.parse(cls.cpMin.toStringAsFixed(2)),
        'max': double.parse(cls.cpMax.toStringAsFixed(2)),
      };
    }
    nutrients = {
      'crude_protein_pct_dm': cp,
      'fibre_pct_dm': null,
      'fat_ee_pct_dm': null,
      'energy_me_mcal_kg': null,
    };
  }

  return {
    'ingredient': ingredient,
    'canonical': canonical,
    'moisture_pct': moisturePct,
    'form': form,
    'method': method,
    'match': match,
    'feed_class': feedClass,
    'nutrients_pct_dm': nutrients,
    'nutrients_as_fed': {
      'crude_protein_pct': asFedSpan(nutrients['crude_protein_pct_dm'], moisturePct),
      'fibre_pct': asFedSpan(nutrients['fibre_pct_dm'], moisturePct),
    },
    'sources': sources,
    'n_source_rows': nRows,
    'disclaimer': kit.disclaimer,
  };
}
