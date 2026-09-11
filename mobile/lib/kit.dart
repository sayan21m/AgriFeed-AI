import 'dart:convert';

import 'package:http/http.dart' as http;

class KitReading {
  KitReading({this.deviceId, this.moisturePct, this.ph, this.as7265x});
  final String? deviceId;
  final double? moisturePct;
  final double? ph;
  final List<double>? as7265x;
}

/// Optional ESP32 hotspot. Measurement only — scoring stays on the phone.
/// Farmers never type an IP; the app tries the board's usual addresses.
class KitClient {
  static const _hosts = ['http://192.168.4.1', 'http://192.168.0.1'];
  String? _live;

  Future<KitReading?> sensors() async {
    final order = <String>[
      ?_live,
      ..._hosts.where((h) => h != _live),
    ];
    for (final host in order) {
      final hit = await _once(host);
      if (hit != null) {
        _live = host;
        return hit;
      }
    }
    _live = null;
    return null;
  }

  Future<KitReading?> _once(String base) async {
    try {
      final root = base.endsWith('/') ? base.substring(0, base.length - 1) : base;
      final res = await http.get(Uri.parse('$root/api/sensors')).timeout(const Duration(seconds: 3));
      if (res.statusCode != 200) return null;
      final body = jsonDecode(res.body) as Map<String, dynamic>;
      final spec = body['as7265x'];
      return KitReading(
        deviceId: body['device_id']?.toString() ?? 'esp32',
        moisturePct: (body['moisture_pct'] as num?)?.toDouble(),
        ph: (body['ph'] as num?)?.toDouble(),
        as7265x: spec is List ? spec.map((x) => (x as num).toDouble()).toList() : null,
      );
    } catch (_) {
      return null;
    }
  }
}
