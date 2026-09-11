import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:smartfeed_app/brand.dart';
import 'package:smartfeed_app/l10n.dart';
import 'package:smartfeed_app/type.dart';

/// Decodes a base64 QR payload to a map, or null on failure.
Map<String, dynamic>? decodeQrPayload(String raw) {
  try {
    final bytes = base64Url.decode(base64Url.normalize(raw));
    return json.decode(utf8.decode(bytes)) as Map<String, dynamic>;
  } catch (_) {
    return null;
  }
}

/// Encodes bag info as a base64 QR payload string (for demo generation).
String encodeQrPayload(Map<String, dynamic> data) {
  return base64Url.encode(utf8.encode(json.encode(data)));
}

class QrTab extends StatefulWidget {
  const QrTab({super.key, required this.t});
  final L10n t;

  @override
  State<QrTab> createState() => _QrTabState();
}

class _QrTabState extends State<QrTab> {
  Map<String, dynamic>? _bag;
  String? _error;
  bool _scanning = false;

  void _onDetect(BarcodeCapture capture) {
    if (!_scanning) return;
    for (final barcode in capture.barcodes) {
      final raw = barcode.rawValue;
      if (raw == null || raw.isEmpty) continue;
      final bag = decodeQrPayload(raw);
      if (bag != null) {
        setState(() {
          _bag = bag;
          _error = null;
          _scanning = false;
        });
        return;
      }
    }
  }

  void _startScan() {
    setState(() {
      _scanning = true;
      _bag = null;
      _error = null;
    });
  }

  void _stopScan() {
    setState(() => _scanning = false);
  }

  void _loadDemo() {
    // Pre-filled demo payload for evaluators without a printed QR code
    final demo = {
      'manufacturer': 'Amul Cattle Feed Plant, Anand',
      'batch_no': 'ACF-2026-0914',
      'pack_date': '2026-08-15',
      'expiry_date': '2027-02-15',
      'declared_cp_pct_dm': 22.0,
      'declared_moisture_pct': 10.0,
      'bis_license': 'IS 2052:2023 Type I',
      'feed_type': 'compounded',
    };
    setState(() {
      _bag = demo;
      _error = null;
      _scanning = false;
    });
  }

  bool get _isExpired {
    final exp = _bag?['expiry_date'];
    if (exp is! String) return false;
    try {
      return DateTime.parse(exp).isBefore(DateTime.now());
    } catch (_) {
      return false;
    }
  }

  @override
  Widget build(BuildContext context) {
    final t = widget.t;
    return ListView(
      padding: Brand.pagePad,
      children: [
        PaperCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(t.qrTitle.toUpperCase(), style: Type.section()),
              const SizedBox(height: 8),
              Text(t.qrLead, style: Type.body(size: 14)),
              const SizedBox(height: 14),
              if (_scanning)
                Column(
                  children: [
                    ClipRRect(
                      borderRadius: BorderRadius.circular(12),
                      child: SizedBox(
                        height: 260,
                        child: MobileScanner(onDetect: _onDetect),
                      ),
                    ),
                    const SizedBox(height: 10),
                    OutlinedButton(onPressed: _stopScan, child: Text(t.qrStop)),
                  ],
                )
              else
                Row(
                  children: [
                    Expanded(
                      child: FilledButton.icon(
                        onPressed: _startScan,
                        icon: const Icon(Icons.qr_code_scanner, size: 20),
                        label: Text(t.qrScan),
                      ),
                    ),
                    const SizedBox(width: 10),
                    OutlinedButton(onPressed: _loadDemo, child: Text(t.qrDemo)),
                  ],
                ),
            ],
          ),
        ),
        if (_error != null)
          PaperCard(
            child: Text(_error!, style: Type.body(color: Brand.reject)),
          ),
        if (_bag != null) _bagCard(t),
      ],
    );
  }

  Widget _bagCard(L10n t) {
    final bag = _bag!;
    final expired = _isExpired;
    return PaperCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Icon(
                expired ? Icons.warning_amber : Icons.verified,
                color: expired ? Brand.reject : Brand.feed,
                size: 22,
              ),
              const SizedBox(width: 8),
              Text(
                expired ? t.qrExpired : t.qrValid,
                style: Type.bodyStrong(color: expired ? Brand.reject : Brand.feed),
              ),
            ],
          ),
          const SizedBox(height: 12),
          _row(t.qrMfr, '${bag['manufacturer'] ?? '—'}'),
          _row(t.qrBatch, '${bag['batch_no'] ?? '—'}'),
          _row(t.qrPack, '${bag['pack_date'] ?? '—'}'),
          _row(t.qrExpiry, '${bag['expiry_date'] ?? '—'}'),
          _row(t.qrDeclaredCp, '${bag['declared_cp_pct_dm'] ?? '—'}% DM'),
          _row(t.qrDeclaredMoist, '${bag['declared_moisture_pct'] ?? '—'}%'),
          _row(t.qrBis, '${bag['bis_license'] ?? '—'}'),
          const SizedBox(height: 10),
          Text(
            t.qrNote,
            style: Type.body(size: 12, color: Brand.mute),
          ),
        ],
      ),
    );
  }

  Widget _row(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 130,
            child: Text(label, style: Type.label()),
          ),
          Expanded(child: Text(value, style: Type.body())),
        ],
      ),
    );
  }
}
