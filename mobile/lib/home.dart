import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:image_picker/image_picker.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:smartfeed_app/brand.dart';
import 'package:smartfeed_app/kit.dart';
import 'package:smartfeed_app/l10n.dart';
import 'package:smartfeed_app/wifi_link.dart';
import 'package:smartfeed_app/offline/pipeline.dart';
import 'package:smartfeed_app/offline/sensors.dart';
import 'package:smartfeed_app/offline/tables.dart';
import 'package:smartfeed_app/type.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

enum _KitLink { idle, looking, connected, offline }

class _HomePageState extends State<HomePage> {
  final _tts = FlutterTts();
  final _kit = KitClient();
  L10n t = L10n(false);
  int _tab = 0;

  List<String> _ingredients = [];
  String _ingredient = '';
  String _form = 'ingredient';
  final _moisture = TextEditingController();
  final _ph = TextEditingController();
  final _urea = TextEditingController();
  final _grit = TextEditingController();
  final _sampleG = TextEditingController();
  final _aia = TextEditingController();
  bool _mould = false;
  File? _photo;
  List<double>? _spectrum;
  _KitLink _kitLink = _KitLink.idle;
  KitReading? _lastKit;
  WifiJoin? _wifiJoin;
  bool _kitBusy = false;
  bool _busy = false;
  String? _error;
  Map<String, dynamic>? _result;
  String _packLine = '';

  @override
  void initState() {
    super.initState();
    _boot();
  }

  Future<void> _boot() async {
    final prefs = await SharedPreferences.getInstance();
    final hi = prefs.getBool('hi') ?? false;
    t = L10n(hi);
    try {
      await OfflineKit.load();
      final kit = OfflineKit.instance;
      _ingredients = kit.feeds.map((f) => f.canonical).toList();
      _packLine = 'v${kit.version} · ${kit.nFeeds} feeds';
    } catch (e) {
      _error = e.toString();
    }
    setState(() {});
    try {
      await _tts.setLanguage(hi ? 'hi-IN' : 'en-IN');
    } catch (_) {}
    await _pullKit(silent: true);
  }

  Future<void> _setHi(bool hi) async {
    t = L10n(hi);
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('hi', hi);
    try {
      await _tts.setLanguage(hi ? 'hi-IN' : 'en-IN');
    } catch (_) {}
    setState(() {});
  }

  Future<void> _openTab(int i) async {
    setState(() => _tab = i);
    if (i == 2) await _pullKit(silent: true);
  }

  String get _kitTitle {
    return switch (_kitLink) {
      _KitLink.looking => t.kitLooking,
      _KitLink.connected => t.kitConnected,
      _KitLink.offline => t.kitOffline,
      _KitLink.idle => t.kit,
    };
  }

  String get _kitDetail {
    final kit = _lastKit;
    if (_kitLink == _KitLink.connected && kit != null) {
      return t.kitReadings(
        kit.moisturePct != null ? '${kit.moisturePct}' : t.none,
        kit.ph != null ? '${kit.ph}' : t.none,
        kit.as7265x != null,
      );
    }
    if (_kitLink == _KitLink.offline) {
      if (_wifiJoin == WifiJoin.needWifi) return t.kitNeedWifi;
      if (_wifiJoin == WifiJoin.needPermission) return t.kitNeedPerm;
      return t.kitNone;
    }
    return t.kitIdle;
  }

  Color get _kitColor {
    return switch (_kitLink) {
      _KitLink.connected => Brand.feed,
      _KitLink.looking => Brand.saffron,
      _KitLink.offline => Brand.reject,
      _KitLink.idle => Brand.mute,
    };
  }

  Future<void> _connectKit() async {
    if (_kitBusy) return;
    _kitBusy = true;
    setState(() {
      _kitLink = _KitLink.looking;
      _wifiJoin = null;
    });
    try {
      _wifiJoin = await joinSmartFeedAp();
      if (!mounted) return;
      await _readSensors(silent: false);
      if (!mounted) return;
      if (_kitLink != _KitLink.connected && _wifiJoin == WifiJoin.ok) {
        await Future<void>.delayed(const Duration(seconds: 1));
        await _readSensors(silent: false);
      }
    } finally {
      _kitBusy = false;
    }
  }

  Future<void> _pullKit({bool silent = false}) async {
    if (_kitBusy) return;
    _kitBusy = true;
    if (!silent) {
      setState(() => _kitLink = _KitLink.looking);
    }
    try {
      await _readSensors(silent: silent);
    } finally {
      _kitBusy = false;
    }
  }

  Future<void> _readSensors({required bool silent}) async {
    try {
      final kit = await _kit.sensors();
      if (!mounted) return;
      if (kit == null) {
        setState(() {
          _kitLink = silent && _lastKit == null ? _KitLink.idle : _KitLink.offline;
          if (!silent) _lastKit = null;
        });
        return;
      }
      if (kit.moisturePct != null) _moisture.text = '${kit.moisturePct}';
      if (kit.ph != null) _ph.text = '${kit.ph}';
      _spectrum = kit.as7265x;
      setState(() {
        _lastKit = kit;
        _kitLink = _KitLink.connected;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _kitLink = silent && _lastKit == null ? _KitLink.idle : _KitLink.offline;
      });
    }
  }

  double? _num(TextEditingController c) {
    final v = c.text.trim();
    if (v.isEmpty) return null;
    return double.tryParse(v);
  }

  Future<void> _pickPhoto(ImageSource source) async {
    final shot = await ImagePicker().pickImage(source: source, imageQuality: 85, maxWidth: 1600);
    if (shot == null) return;
    setState(() => _photo = File(shot.path));
  }

  Future<void> _test() async {
    if (_ingredient.trim().isEmpty) return;
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      final out = await assess(
        ingredient: _ingredient.trim(),
        form: _form,
        moisturePct: _num(_moisture),
        ph: _num(_ph),
        ureaYellowAreaPct: _num(_urea),
        visibleMould: _mould,
        gritSettledMl: _num(_grit),
        sampleG: _num(_sampleG),
        aiaPct: _num(_aia),
        nirAbsorbance: _spectrum,
        imagePath: _photo?.path,
      );
      setState(() {
        _result = out;
        _tab = 1;
      });
    } on SensorRangeError catch (e) {
      setState(() {
        _error = e.message;
        _tab = 1;
        _result = null;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _tab = 1;
        _result = null;
      });
    } finally {
      setState(() => _busy = false);
    }
  }

  void _setForm(String form) => setState(() => _form = form);

  void _setMould(bool value) => setState(() => _mould = value);

  Future<void> _speak() async {
    final spoken = Map<String, dynamic>.from(_result?['spoken'] as Map? ?? {});
    final raw = t.hi ? spoken['hi'] : spoken['en'];
    if (raw is String && raw.isNotEmpty) {
      await _tts.stop();
      await _tts.speak(raw);
    }
  }

  @override
  void dispose() {
    _moisture.dispose();
    _ph.dispose();
    _urea.dispose();
    _grit.dispose();
    _sampleG.dispose();
    _aia.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          _TopBar(state: this),
          Expanded(
            child: IndexedStack(
              index: _tab,
              children: [
                _TestTab(state: this),
                _ResultTab(state: this),
                _KitTab(state: this),
              ],
            ),
          ),
        ],
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _tab,
        onDestinationSelected: _openTab,
        destinations: [
          NavigationDestination(icon: const Icon(Icons.grass_outlined), selectedIcon: const Icon(Icons.grass), label: t.tabTest),
          NavigationDestination(icon: const Icon(Icons.pets_outlined), selectedIcon: const Icon(Icons.pets), label: t.tabResult),
          NavigationDestination(icon: const Icon(Icons.sensors_outlined), selectedIcon: const Icon(Icons.sensors), label: t.tabKit),
        ],
      ),
    );
  }
}

class _TopBar extends StatelessWidget {
  const _TopBar({required this.state});
  final _HomePageState state;

  @override
  Widget build(BuildContext context) {
    final t = state.t;
    return Material(
      color: Brand.forest,
      child: SafeArea(
        bottom: false,
        child: Padding(
          padding: const EdgeInsets.fromLTRB(20, 10, 16, 12),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              ClipOval(
                child: Image.asset(Brand.mark, width: 42, height: 42, fit: BoxFit.cover),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(t.kicker, style: Type.kicker(color: Brand.onPhotoSoft)),
                    const SizedBox(height: 2),
                    Text(t.title, style: Type.displayMd(color: Brand.onPhoto)),
                  ],
                ),
              ),
              SegmentedButton<bool>(
                segments: const [
                  ButtonSegment(value: false, label: Text('EN')),
                  ButtonSegment(value: true, label: Text('हिं')),
                ],
                selected: {t.hi},
                onSelectionChanged: (s) => state._setHi(s.first),
                style: ButtonStyle(
                  visualDensity: VisualDensity.compact,
                  tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                  textStyle: WidgetStateProperty.all(Type.button().copyWith(fontSize: 12)),
                  foregroundColor: WidgetStateProperty.all(Brand.onPhoto),
                  backgroundColor: WidgetStateProperty.resolveWith(
                    (s) => s.contains(WidgetState.selected) ? const Color(0xFF2F5A38) : Colors.transparent,
                  ),
                  side: WidgetStateProperty.all(const BorderSide(color: Brand.onPhotoSoft)),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _TestTab extends StatelessWidget {
  const _TestTab({required this.state});
  final _HomePageState state;

  @override
  Widget build(BuildContext context) {
    final t = state.t;
    return ListView(
      padding: Brand.pagePad,
      children: [
        PhotoScrim(
          asset: Brand.hero,
          height: 168,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(t.tagline.toUpperCase(), style: Type.kicker(color: Brand.onPhotoSoft).copyWith(shadows: Type.photoShadow)),
              const SizedBox(height: 6),
              Text(t.heroLine, style: Type.displayMd(color: Brand.onPhoto)),
            ],
          ),
        ),
        const SizedBox(height: Brand.gap),
        PaperCard(child: _KitStatusRow(state: state, compact: true)),
        PaperCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(t.sectionFeed.toUpperCase(), style: Type.section()),
              const SizedBox(height: 12),
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  FormPhotoTile(
                    asset: Brand.grain,
                    label: t.formIng,
                    selected: state._form == 'ingredient',
                    onTap: () => state._setForm('ingredient'),
                  ),
                  const SizedBox(width: 10),
                  FormPhotoTile(
                    asset: Brand.forage,
                    label: t.formSil,
                    selected: state._form == 'silage',
                    onTap: () => state._setForm('silage'),
                  ),
                  const SizedBox(width: 10),
                  FormPhotoTile(
                    asset: Brand.hay,
                    label: t.formCmp,
                    selected: state._form == 'compounded',
                    onTap: () => state._setForm('compounded'),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Text(t.ingredient, style: Type.label()),
              const SizedBox(height: 8),
              Autocomplete<String>(
                optionsBuilder: (v) {
                  final q = v.text.toLowerCase();
                  final all = state._ingredients;
                  if (q.isEmpty) return all;
                  return all.where((name) => name.contains(q));
                },
                onSelected: (v) => state._ingredient = v,
                fieldViewBuilder: (context, controller, focus, onSubmit) {
                  return TextField(
                    controller: controller,
                    focusNode: focus,
                    onChanged: (v) => state._ingredient = v,
                    style: Type.body(),
                    decoration: const InputDecoration(
                      hintText: 'mustard cake / sarson khali',
                      prefixIcon: Icon(Icons.search, size: 20),
                    ),
                  );
                },
              ),
              const SizedBox(height: 20),
              Text(t.sectionSensors.toUpperCase(), style: Type.section()),
              const SizedBox(height: 12),
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(child: _numField(t.moisture, state._moisture)),
                  const SizedBox(width: 10),
                  Expanded(child: _numField(t.ph, state._ph)),
                ],
              ),
              _numField(t.urea, state._urea),
              Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Row(
                  children: [
                    Expanded(child: Text(t.mould, style: Type.bodyStrong())),
                    Switch.adaptive(value: state._mould, onChanged: state._setMould),
                  ],
                ),
              ),
              ExpansionTile(
                tilePadding: EdgeInsets.zero,
                childrenPadding: EdgeInsets.zero,
                title: Text(t.sand, style: Type.bodyStrong()),
                children: [
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Expanded(child: _numField(t.grit, state._grit)),
                      const SizedBox(width: 10),
                      Expanded(child: _numField(t.sampleG, state._sampleG)),
                    ],
                  ),
                  _numField(t.aia, state._aia),
                ],
              ),
              const SizedBox(height: 8),
              Text(t.photo, style: Type.label()),
              const SizedBox(height: 8),
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () => state._pickPhoto(ImageSource.camera),
                      icon: const Icon(Icons.photo_camera, size: 18),
                      label: Text(t.camera),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () => state._pickPhoto(ImageSource.gallery),
                      icon: const Icon(Icons.photo_library, size: 18),
                      label: Text(t.gallery),
                    ),
                  ),
                ],
              ),
              if (state._photo != null) ...[
                const SizedBox(height: 12),
                ClipRRect(
                  borderRadius: BorderRadius.circular(12),
                  child: Image.file(state._photo!, height: 160, width: double.infinity, fit: BoxFit.cover),
                ),
              ],
              const SizedBox(height: 18),
              FilledButton.icon(
                onPressed: state._busy ? null : state._test,
                style: FilledButton.styleFrom(minimumSize: const Size.fromHeight(52)),
                icon: const Icon(Icons.science_outlined),
                label: Text(state._busy ? t.testing : t.test),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _numField(String label, TextEditingController c) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: TextField(
        controller: c,
        style: Type.body(),
        keyboardType: const TextInputType.numberWithOptions(decimal: true),
        decoration: InputDecoration(labelText: label),
      ),
    );
  }
}

class _ResultTab extends StatelessWidget {
  const _ResultTab({required this.state});
  final _HomePageState state;

  @override
  Widget build(BuildContext context) {
    final t = state.t;
    if (state._error != null && state._result == null) {
      return Center(child: Padding(padding: const EdgeInsets.all(24), child: Text(state._error!, style: Type.body(), textAlign: TextAlign.center)));
    }
    final data = state._result;
    if (data == null) {
      return ListView(
        padding: Brand.pagePad,
        children: [
          PhotoScrim(
            asset: Brand.barn,
            height: 280,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(t.emptyVerdictTitle, style: Type.displayMd(color: Brand.onPhoto)),
                const SizedBox(height: 8),
                Text(t.resultEmpty, style: Type.body(color: Brand.onPhoto)),
              ],
            ),
          ),
        ],
      );
    }
    final farmer = data['farmer'] as Map? ?? {};
    final modules = data['modules'] as Map? ?? {};
    final nut = modules['nutrition'] as Map? ?? {};
    final moist = modules['moisture'] as Map? ?? {};
    final silage = modules['silage'] as Map? ?? {};
    final urea = modules['urea'] as Map? ?? {};
    final nir = modules['nir'] as Map? ?? {};
    final af = modules['aflatoxin'] as Map? ?? {};
    final ration = data['ration'] as Map? ?? {};
    final action = '${farmer['action'] ?? 'feed'}';
    final label = t.hi ? farmer['label_hi'] : farmer['label_en'];
    final summary = t.hi ? farmer['summary_hi'] : farmer['summary_en'];
    final reasons = List<String>.from((t.hi ? farmer['reasons_hi'] : farmer['reasons_en']) ?? const []);
    final other = List<String>.from((t.hi ? farmer['other_flags_hi'] : farmer['other_flags_en']) ?? const []);
    final tips = List<String>.from((t.hi ? ration['tips_hi'] : ration['tips_en']) ?? const []);
    final role = t.hi ? ration['role_hi'] : ration['role_en'];
    final warns = List<String>.from(data['sensor_warnings'] ?? const []);
    final spoken = data['spoken'] as Map? ?? {};
    final spokenText = t.hi ? spoken['hi'] : spoken['en'];
    final cp = (nut['nutrients_pct_dm'] as Map?)?['crude_protein_pct_dm'];
    final asfed = (nut['nutrients_as_fed'] as Map?)?['crude_protein_pct'];
    final color = switch (action) {
      'reject' => Brand.reject,
      'dilute' => Brand.dilute,
      _ => Brand.feed,
    };
    String chipNote = t.none;
    if (nir['used'] == false) {
      chipNote = t.hi ? '18 बैंड आए, प्रोटीन नहीं निकाला' : '18 bands received, not used for protein';
    }

    return ListView(
      padding: Brand.pagePad,
      children: [
        ClipRRect(
          borderRadius: BorderRadius.circular(18),
          child: Stack(
            children: [
              Image.asset(Brand.verdictPhoto(action), height: 200, width: double.infinity, fit: BoxFit.cover),
              Container(
                height: 200,
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topCenter,
                    end: Alignment.bottomCenter,
                    colors: [color.withValues(alpha: 0.2), color.withValues(alpha: 0.94)],
                  ),
                ),
              ),
              Positioned(
                left: 18,
                right: 18,
                bottom: 16,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('$label', style: Type.displayLg(color: Brand.onPhoto)),
                    const SizedBox(height: 6),
                    Text('$summary', style: Type.body(color: Brand.onPhoto)),
                  ],
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: Brand.gap),
        if (spokenText != null)
          PaperCard(
            child: Text('$spokenText', style: Type.body(size: 15.5)),
          ),
        FilledButton.icon(
          onPressed: state._speak,
          style: FilledButton.styleFrom(minimumSize: const Size.fromHeight(52)),
          icon: const Icon(Icons.volume_up),
          label: Text(t.hear),
        ),
        const SizedBox(height: 16),
        LayoutBuilder(
          builder: (context, box) {
            final width = (box.maxWidth - 10) / 2;
            final tiles = [
              (t.cp, _span(cp), Icons.spa_outlined),
              (t.asfed, _span(asfed), Icons.water_drop_outlined),
              (t.method, '${nut['method'] ?? t.none}', Icons.menu_book_outlined),
              (t.dm, '${moist['dry_matter_pct'] ?? t.none}', Icons.opacity),
              (t.flieg, '${silage['flieg_score'] ?? t.none}', Icons.science_outlined),
              (t.ureaEst, '${urea['urea_g_per_kg'] ?? t.none}', Icons.science),
              (t.chip, chipNote, Icons.palette_outlined),
            ];
            return Wrap(
              spacing: 10,
              runSpacing: 10,
              children: [
                for (final tile in tiles) SizedBox(width: width, child: _metric(tile.$1, tile.$2, tile.$3)),
              ],
            );
          },
        ),
        const SizedBox(height: 20),
        Text(t.why.toUpperCase(), style: Type.section()),
        const SizedBox(height: 6),
        ...reasons.map((r) => _line(r, Icons.chevron_right)),
        if (other.isNotEmpty) ...[
          const SizedBox(height: 14),
          Text(t.also.toUpperCase(), style: Type.section()),
          const SizedBox(height: 6),
          ...other.map((r) => _line(r, Icons.flag_outlined)),
        ],
        if (tips.isNotEmpty) ...[
          const SizedBox(height: 14),
          Text('${t.ration}${role != null ? ' — $role' : ''}'.toUpperCase(), style: Type.section()),
          const SizedBox(height: 6),
          ...tips.map((r) => _line(r, Icons.agriculture_outlined)),
        ],
        if (warns.isNotEmpty) ...[
          const SizedBox(height: 14),
          Text(t.sensor.toUpperCase(), style: Type.section(color: Brand.saffron)),
          const SizedBox(height: 6),
          ...warns.map((r) => _line(r, Icons.warning_amber_outlined)),
        ],
        const SizedBox(height: 12),
        PaperCard(
          child: Text(
            '${t.af}: ${af['high_risk_ingredient'] == true ? t.higher : t.lower}${af['matched_item'] != null ? ' · ${af['matched_item']}' : ''}',
            style: Type.body(size: 14),
          ),
        ),
        Text('${data['disclaimer'] ?? ''}', style: Type.body(color: Brand.mute, size: 13)),
      ],
    );
  }

  Widget _line(String text, IconData icon) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.only(top: 2),
            child: Icon(icon, size: 18, color: Brand.leaf),
          ),
          const SizedBox(width: 8),
          Expanded(child: Text(text, style: Type.body())),
        ],
      ),
    );
  }

  Widget _metric(String label, String value, IconData icon) {
    return Container(
      padding: const EdgeInsets.fromLTRB(12, 10, 12, 12),
      decoration: BoxDecoration(
        color: Brand.paper,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFFE4D7BE)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, size: 16, color: Brand.leaf),
          const SizedBox(height: 6),
          Text(label, style: Type.label(), maxLines: 2, overflow: TextOverflow.ellipsis),
          const SizedBox(height: 4),
          Text(value, style: Type.metric(), maxLines: 2, overflow: TextOverflow.ellipsis),
        ],
      ),
    );
  }

  String _span(dynamic span) {
    if (span is! Map) return state.t.none;
    if (span['min'] != null && span['max'] != null) {
      return '${span['mean']}  (${span['min']}–${span['max']})';
    }
    return '${span['mean'] ?? state.t.none}';
  }
}

class _KitTab extends StatelessWidget {
  const _KitTab({required this.state});
  final _HomePageState state;

  @override
  Widget build(BuildContext context) {
    final t = state.t;
    return ListView(
      padding: Brand.pagePad,
      children: [
        PhotoScrim(
          asset: Brand.fields,
          height: 168,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(t.kitPacked, style: Type.displayMd(color: Brand.onPhoto)),
              const SizedBox(height: 6),
              Text(state._packLine.isEmpty ? t.none : state._packLine, style: Type.body(color: Brand.onPhoto)),
            ],
          ),
        ),
        const SizedBox(height: Brand.gap),
        PaperCard(child: _KitStatusRow(state: state, compact: false)),
        PaperCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(t.kitHow.toUpperCase(), style: Type.section()),
              const SizedBox(height: 10),
              _HowStep(n: '1', text: t.kitStep1),
              _HowStep(n: '2', text: t.kitStep2),
              _HowStep(n: '3', text: t.kitStep3),
              const SizedBox(height: 8),
              Text(t.kitLead, style: Type.body(size: 13.5, color: Brand.mute)),
            ],
          ),
        ),
        PaperCard(
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              ClipOval(child: Image.asset(Brand.cow, width: 48, height: 48, fit: BoxFit.cover)),
              const SizedBox(width: 12),
              Expanded(child: Text(t.offlineNote, style: Type.body(size: 13.5))),
            ],
          ),
        ),
        if (state._error != null)
          Padding(padding: const EdgeInsets.only(top: 8), child: Text(state._error!, style: Type.body(color: Brand.reject))),
      ],
    );
  }
}

class _HowStep extends StatelessWidget {
  const _HowStep({required this.n, required this.text});
  final String n;
  final String text;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          CircleAvatar(
            radius: 12,
            backgroundColor: Brand.forest,
            child: Text(n, style: Type.bodyStrong(color: Colors.white).copyWith(fontSize: 13)),
          ),
          const SizedBox(width: 10),
          Expanded(child: Text(text, style: Type.body())),
        ],
      ),
    );
  }
}

class _KitStatusRow extends StatelessWidget {
  const _KitStatusRow({required this.state, required this.compact});
  final _HomePageState state;
  final bool compact;

  @override
  Widget build(BuildContext context) {
    final t = state.t;
    final looking = state._kitLink == _KitLink.looking;
    final connected = state._kitLink == _KitLink.connected;
    final kit = state._lastKit;
    final button = FilledButton(
      onPressed: looking ? null : () => state._connectKit(),
      style: FilledButton.styleFrom(
        minimumSize: compact ? const Size(0, 44) : const Size.fromHeight(52),
        padding: compact ? const EdgeInsets.symmetric(horizontal: 14) : null,
        textStyle: Type.button().copyWith(fontSize: compact ? 13 : 15),
      ),
      child: looking
          ? SizedBox(
              width: compact ? 18 : 22,
              height: compact ? 18 : 22,
              child: const CircularProgressIndicator(strokeWidth: 2.4, color: Brand.paper),
            )
          : Text(t.kitPull),
    );

    final status = Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          width: 12,
          height: 12,
          margin: const EdgeInsets.only(top: 4),
          decoration: BoxDecoration(color: state._kitColor, shape: BoxShape.circle),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(state._kitTitle, style: Type.bodyStrong(color: state._kitColor)),
              const SizedBox(height: 4),
              Text(state._kitDetail, style: Type.body(size: 13.5)),
            ],
          ),
        ),
      ],
    );

    if (compact) {
      return Row(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          Expanded(child: status),
          const SizedBox(width: 10),
          button,
        ],
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        status,
        if (connected && kit != null) ...[
          const SizedBox(height: 14),
          Row(
            children: [
              Expanded(child: _SensorChip(label: t.moisture, value: kit.moisturePct != null ? '${kit.moisturePct}' : t.none)),
              const SizedBox(width: 10),
              Expanded(child: _SensorChip(label: t.ph, value: kit.ph != null ? '${kit.ph}' : t.none)),
            ],
          ),
        ],
        const SizedBox(height: 16),
        button,
      ],
    );
  }
}

class _SensorChip extends StatelessWidget {
  const _SensorChip({required this.label, required this.value});
  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(12, 10, 12, 10),
      decoration: BoxDecoration(
        color: Brand.cream,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFE4D7BE)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: Type.label()),
          const SizedBox(height: 4),
          Text(value, style: Type.metric()),
        ],
      ),
    );
  }
}
