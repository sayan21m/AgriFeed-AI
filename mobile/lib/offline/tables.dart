import 'dart:convert';

import 'package:flutter/services.dart';

class FeedRow {
  FeedRow(this.raw);
  final Map<String, dynamic> raw;

  String get canonical => '${raw['canonical']}';
  String get feedClass => '${raw['feed_class']}';
  String get form => '${raw['form']}';
  int? get nRows => (raw['n_rows'] as num?)?.toInt();
  String? get sources => raw['sources']?.toString();
  double? value(String key) => (raw[key] as num?)?.toDouble();
}

class ClassCp {
  ClassCp({required this.feedClass, required this.cpMean, required this.cpMin, required this.cpMax});
  final String feedClass;
  final double cpMean;
  final double cpMin;
  final double cpMax;
}

class UreaSlope {
  UreaSlope({
    required this.key,
    required this.slope,
    required this.intercept,
    required this.yellowLo,
    required this.yellowHi,
    this.cakeLabel,
  });
  final String key;
  final double slope;
  final double intercept;
  final double yellowLo;
  final double yellowHi;
  final String? cakeLabel;
}

class FliegRule {
  FliegRule({required this.minScore, required this.maxScore, required this.klass, required this.advice});
  final double minScore;
  final double maxScore;
  final String klass;
  final String advice;
}

class KotinaguRow {
  KotinaguRow({
    required this.item,
    this.nAnalyzed,
    this.incidencePct,
    this.meanPpb,
    this.rangePpb,
  });
  final String item;
  final int? nAnalyzed;
  final double? incidencePct;
  final double? meanPpb;
  final String? rangePpb;
}

class OfflineKit {
  OfflineKit._(this.json);
  final Map<String, dynamic> json;

  static OfflineKit? _instance;

  static OfflineKit get instance {
    final kit = _instance;
    if (kit == null) {
      throw StateError('Offline tables not loaded. Call OfflineKit.load() first.');
    }
    return kit;
  }

  static Future<OfflineKit> load() async {
    if (_instance != null) return _instance!;
    final raw = await rootBundle.loadString('assets/offline_kit.json');
    _instance = OfflineKit.fromJson(jsonDecode(raw) as Map<String, dynamic>);
    return _instance!;
  }

  static OfflineKit fromJson(Map<String, dynamic> json) {
    final kit = OfflineKit._(json);
    _instance = kit;
    return kit;
  }

  static void resetForTest() => _instance = null;

  String get version => '${json['version'] ?? ''}';
  int get nFeeds => (json['n_feeds'] as num?)?.toInt() ?? feeds.length;
  String get disclaimer => '${json['disclaimer'] ?? ''}';

  late final List<FeedRow> feeds =
      (json['feeds'] as List<dynamic>).map((row) => FeedRow(Map<String, dynamic>.from(row as Map))).toList();

  late final Map<String, FeedRow> byCanonical = {for (final f in feeds) f.canonical: f};

  late final List<ClassCp> classCp = (json['class_cp'] as List<dynamic>)
      .map(
        (row) => ClassCp(
          feedClass: '${row['feed_class']}',
          cpMean: (row['cp_mean'] as num).toDouble(),
          cpMin: (row['cp_min'] as num).toDouble(),
          cpMax: (row['cp_max'] as num).toDouble(),
        ),
      )
      .toList();

  late final List<UreaSlope> urea = (json['urea'] as List<dynamic>)
      .map(
        (row) => UreaSlope(
          key: '${row['key']}',
          slope: (row['slope'] as num).toDouble(),
          intercept: (row['intercept'] as num).toDouble(),
          yellowLo: (row['yellow_lo'] as num).toDouble(),
          yellowHi: (row['yellow_hi'] as num).toDouble(),
          cakeLabel: row['cake_label']?.toString(),
        ),
      )
      .toList();

  late final List<FliegRule> flieg = (json['flieg'] as List<dynamic>)
      .map(
        (row) => FliegRule(
          minScore: (row['min_score'] as num).toDouble(),
          maxScore: (row['max_score'] as num).toDouble(),
          klass: '${row['class']}',
          advice: '${row['advice']}',
        ),
      )
      .toList();

  late final List<KotinaguRow> kotinagu = (json['kotinagu'] as List<dynamic>)
      .map(
        (row) => KotinaguRow(
          item: '${row['item']}',
          nAnalyzed: (row['n_analyzed'] as num?)?.toInt(),
          incidencePct: (row['incidence_pct'] as num?)?.toDouble(),
          meanPpb: (row['mean_ppb'] as num?)?.toDouble(),
          rangePpb: row['range_ppb']?.toString(),
        ),
      )
      .toList();

  Map<String, dynamic> get bis => Map<String, dynamic>.from(json['bis'] as Map);

  double bisLimit(String characteristic, {required bool compounded}) {
    final row = bis[characteristic] as Map? ?? {};
    final key = compounded ? 'type_I' : 'type_II';
    return (row[key] as num?)?.toDouble() ?? (row['type_II'] as num).toDouble();
  }

  ClassCp? classFor(String feedClass) {
    for (final row in classCp) {
      if (row.feedClass == feedClass) return row;
    }
    return null;
  }
}
