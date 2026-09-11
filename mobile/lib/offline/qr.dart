import 'dart:convert';

/// Mill/cooperative bag QR — unsigned prototype, same payload as `smartfeed/qr.py`.
String encodeQrPayload(Map<String, dynamic> data) {
  return base64Url.encode(utf8.encode(json.encode(data)));
}

Map<String, dynamic>? decodeQrPayload(String raw) {
  final payload = raw.trim();
  if (payload.startsWith('{')) {
    try {
      final parsed = json.decode(payload);
      return parsed is Map<String, dynamic> ? parsed : null;
    } catch (_) {
      return null;
    }
  }
  try {
    final bytes = base64Url.decode(base64Url.normalize(payload));
    final parsed = json.decode(utf8.decode(bytes));
    return parsed is Map<String, dynamic> ? parsed : null;
  } catch (_) {
    return null;
  }
}

Map<String, dynamic> verifyQr(String payload, [Map<String, dynamic>? nutrition]) {
  final bag = decodeQrPayload(payload);
  if (bag == null) {
    return {
      'present': true,
      'decoded': false,
      'verified': false,
      'warnings': ['Could not decode QR payload.'],
    };
  }

  final warnings = <String>[];
  var expired = false;
  final expiryStr = bag['expiry_date'];
  if (expiryStr is String && expiryStr.isNotEmpty) {
    try {
      final expiry = DateTime.parse(expiryStr);
      final today = DateTime.now();
      final expiryDay = DateTime(expiry.year, expiry.month, expiry.day);
      final todayDay = DateTime(today.year, today.month, today.day);
      if (expiryDay.isBefore(todayDay)) {
        expired = true;
        warnings.add('Bag expired on $expiryStr.');
      }
    } catch (_) {
      warnings.add('Invalid expiry date format: $expiryStr');
    }
  }

  var cpMismatch = false;
  final declaredCp = _asDouble(bag['declared_cp_pct_dm']);
  if (declaredCp != null && nutrition != null) {
    final nutrients = (nutrition['nutrients_pct_dm'] as Map?)?['crude_protein_pct_dm'] as Map?;
    final tableCp = _asDouble(nutrients?['mean']);
    if (tableCp != null) {
      final diff = (declaredCp - tableCp).abs();
      if (diff > 5.0) {
        cpMismatch = true;
        warnings.add(
          'Declared CP $declaredCp% DM differs from table value $tableCp% DM by ${diff.toStringAsFixed(1)} percentage points.',
        );
      }
    }
  }

  var moistureMismatch = false;
  final declaredMoisture = _asDouble(bag['declared_moisture_pct']);
  if (declaredMoisture != null && nutrition != null) {
    final measured = _asDouble(nutrition['moisture_pct']);
    if (measured != null) {
      final diff = (declaredMoisture - measured).abs();
      if (diff > 3.0) {
        moistureMismatch = true;
        warnings.add(
          'Declared moisture $declaredMoisture% differs from measured $measured% by ${diff.toStringAsFixed(1)} points.',
        );
      }
    }
  }

  final verified = !expired && !cpMismatch && !moistureMismatch && warnings.isEmpty;
  return {
    'present': true,
    'decoded': true,
    'verified': verified,
    'expired': expired,
    'cp_mismatch': cpMismatch,
    'moisture_mismatch': moistureMismatch,
    'warnings': warnings,
    'bag_info': {
      'manufacturer': bag['manufacturer'],
      'batch_no': bag['batch_no'],
      'pack_date': bag['pack_date'],
      'expiry_date': bag['expiry_date'],
      'declared_cp_pct_dm': declaredCp,
      'declared_moisture_pct': declaredMoisture,
      'bis_license': bag['bis_license'],
      'feed_type': bag['feed_type'],
      'ingredient': bag['ingredient'],
    },
    'note': 'Prototype QR verification. Production systems should use signed payloads.',
  };
}

Map<String, dynamic> demoBag({required String kind}) {
  switch (kind) {
    case 'expired':
      return {
        'manufacturer': 'Kaira Union Feed',
        'batch_no': 'EXP-99',
        'pack_date': '2019-01-10',
        'expiry_date': '2020-01-10',
        'declared_cp_pct_dm': 35.0,
        'declared_moisture_pct': 11.0,
        'ingredient': 'mustard cake',
        'feed_type': 'ingredient',
      };
    case 'mismatch':
      return {
        'manufacturer': 'CheapFeeds Ltd',
        'batch_no': 'M-042',
        'pack_date': '2026-06-01',
        'expiry_date': '2027-06-01',
        'declared_cp_pct_dm': 12.0,
        'declared_moisture_pct': 10.0,
        'ingredient': 'mustard cake',
        'feed_type': 'ingredient',
      };
    default:
      return {
        'manufacturer': 'Amul Cattle Feed Plant, Anand',
        'batch_no': 'ACF-2026-0914',
        'pack_date': '2026-08-15',
        'expiry_date': '2027-08-01',
        'declared_cp_pct_dm': 36.0,
        'declared_moisture_pct': 10.0,
        'bis_license': 'IS 2052:2023',
        'ingredient': 'mustard cake',
        'feed_type': 'ingredient',
      };
  }
}

double? _asDouble(Object? value) {
  if (value is num) return value.toDouble();
  if (value is String) return double.tryParse(value);
  return null;
}
