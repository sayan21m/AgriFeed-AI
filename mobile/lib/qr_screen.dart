import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:qr_flutter/qr_flutter.dart';
import 'package:smartfeed_app/brand.dart';
import 'package:smartfeed_app/l10n.dart';
import 'package:smartfeed_app/offline/qr.dart';
import 'package:smartfeed_app/type.dart';

class QrTab extends StatefulWidget {
  const QrTab({
    super.key,
    required this.t,
    required this.payload,
    required this.onScanned,
    required this.onUseInTest,
    required this.onClear,
  });

  final L10n t;
  final String? payload;
  final ValueChanged<String> onScanned;
  final VoidCallback onUseInTest;
  final VoidCallback onClear;

  @override
  State<QrTab> createState() => _QrTabState();
}

class _QrTabState extends State<QrTab> {
  String? _error;
  bool _scanning = false;
  String _issueKind = 'valid';

  Map<String, dynamic>? get _bag {
    final payload = widget.payload;
    if (payload == null || payload.isEmpty) return null;
    return decodeQrPayload(payload);
  }

  void _onDetect(BarcodeCapture capture) {
    if (!_scanning) return;
    for (final barcode in capture.barcodes) {
      final raw = barcode.rawValue;
      if (raw == null || raw.isEmpty) continue;
      final bag = decodeQrPayload(raw);
      if (bag == null) {
        setState(() => _error = widget.t.qrInvalid);
        continue;
      }
      setState(() {
        _error = null;
        _scanning = false;
      });
      widget.onScanned(raw.trim());
      return;
    }
  }

  void _startScan() {
    setState(() {
      _scanning = true;
      _error = null;
    });
  }

  void _stopScan() {
    setState(() => _scanning = false);
  }

  void _loadDemo(String kind) {
    final payload = encodeQrPayload(demoBag(kind: kind));
    setState(() {
      _error = null;
      _scanning = false;
      _issueKind = kind;
    });
    widget.onScanned(payload);
  }

  bool get _isExpired {
    final exp = _bag?['expiry_date'];
    if (exp is! String) return false;
    try {
      final expiry = DateTime.parse(exp);
      final now = DateTime.now();
      return DateTime(expiry.year, expiry.month, expiry.day)
          .isBefore(DateTime(now.year, now.month, now.day));
    } catch (_) {
      return false;
    }
  }

  @override
  Widget build(BuildContext context) {
    final t = widget.t;
    final issuePayload = encodeQrPayload(demoBag(kind: _issueKind));
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
                    OutlinedButton(onPressed: () => _loadDemo('valid'), child: Text(t.qrDemo)),
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
        PaperCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(t.qrIssue.toUpperCase(), style: Type.section()),
              const SizedBox(height: 8),
              Text(t.qrIssueLead, style: Type.body(size: 14)),
              const SizedBox(height: 12),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  _kindChip(t.qrDemoValid, 'valid'),
                  _kindChip(t.qrDemoExpired, 'expired'),
                  _kindChip(t.qrDemoMismatch, 'mismatch'),
                ],
              ),
              const SizedBox(height: 16),
              Center(
                child: Container(
                  padding: const EdgeInsets.all(12),
                  color: Colors.white,
                  child: QrImageView(
                    data: issuePayload,
                    size: 200,
                    backgroundColor: Colors.white,
                  ),
                ),
              ),
              const SizedBox(height: 10),
              Text(t.qrNote, style: Type.body(size: 12, color: Brand.mute)),
            ],
          ),
        ),
      ],
    );
  }

  Widget _kindChip(String label, String kind) {
    final selected = _issueKind == kind;
    return ChoiceChip(
      label: Text(label),
      selected: selected,
      onSelected: (_) => _loadDemo(kind),
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
              Expanded(
                child: Text(
                  expired ? t.qrExpired : t.qrValid,
                  style: Type.bodyStrong(color: expired ? Brand.reject : Brand.feed),
                ),
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
          const SizedBox(height: 8),
          Text(t.qrCheckRunsOnTest, style: Type.body(size: 13, color: Brand.mute)),
          const SizedBox(height: 12),
          FilledButton(onPressed: widget.onUseInTest, child: Text(t.qrUseInTest)),
          const SizedBox(height: 8),
          OutlinedButton(onPressed: widget.onClear, child: Text(t.qrClear)),
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
