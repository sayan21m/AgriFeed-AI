class SensorRangeError implements Exception {
  SensorRangeError(this.message);
  final String message;
  @override
  String toString() => message;
}

const ranges = {
  'moisture_pct': (0.0, 100.0),
  'ph': (0.0, 14.0),
  'urea_yellow_area_pct': (0.0, 100.0),
  'aia_pct': (0.0, 100.0),
  'grit_settled_ml': (0.0, 1000.0),
  'sample_g': (0.1, 10000.0),
};

const plausible = {
  'moisture_pct': (2.0, 95.0),
  'ph': (3.0, 9.0),
};

double? check(String name, double? value) {
  if (value == null) return null;
  if (value.isNaN) throw SensorRangeError('$name is not a number');
  final lohi = ranges[name]!;
  if (value < lohi.$1 || value > lohi.$2) {
    throw SensorRangeError('$name=$value is outside the valid range ${lohi.$1}-${lohi.$2}');
  }
  return value;
}

List<String> checkAll(Map<String, double?> readings) {
  for (final name in ranges.keys) {
    if (readings.containsKey(name)) check(name, readings[name]);
  }
  final out = <String>[];
  for (final entry in plausible.entries) {
    final val = readings[entry.key];
    if (val != null && (val < entry.value.$1 || val > entry.value.$2)) {
      out.add('${entry.key}=$val is outside the usual ${entry.value.$1}-${entry.value.$2} band — check the sensor.');
    }
  }
  return out;
}

double dryMatterPct(double moisturePct) => double.parse((100.0 - moisturePct).toStringAsFixed(2));

double? asFed(double? valuePctDm, double? moisturePct) {
  if (valuePctDm == null || moisturePct == null) return null;
  return double.parse((valuePctDm * (1.0 - moisturePct / 100.0)).toStringAsFixed(2));
}

Map<String, double?>? asFedSpan(Map<String, double?>? span, double? moisturePct) {
  if (span == null || moisturePct == null) return null;
  return {
    'mean': asFed(span['mean'], moisturePct),
    'min': asFed(span['min'], moisturePct),
    'max': asFed(span['max'], moisturePct),
  };
}

Map<String, dynamic> assessMoisture(double? moisturePct, {String? form}) {
  if (moisturePct == null) {
    return {'present': false, 'note': 'No moisture reading. Tables stay on a % DM basis.'};
  }
  final m = moisturePct;
  final flags = <String>[];
  if (form == 'silage') {
    if (m < 60) {
      flags.add('silage_too_dry_risk_heat');
    } else if (m > 75) {
      flags.add('silage_too_wet_risk_effluent');
    } else {
      flags.add('silage_dm_in_typical_band');
    }
  } else {
    if (m > 14) flags.add('dry_feed_above_safe_store_moisture');
    if (m > 11 && form == 'compounded') flags.add('above_bis_moisture_max_11');
  }
  return {
    'present': true,
    'moisture_pct': m,
    'dry_matter_pct': dryMatterPct(m),
    'flags': flags,
    'note': 'Moisture converts % DM to as-fed. It is not crude protein.',
  };
}

const fliegFormula = '220 + (2 * DM% - 15) - 40 * pH';

double fliegScore(double dmPct, double ph) => 220 + (2.0 * dmPct - 15) - 40.0 * ph;
