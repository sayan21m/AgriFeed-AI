const actionCopy = {
  'feed': {
    'en': 'Feed',
    'hi': 'खिलाएँ',
    'summary_en': "Safe to feed. Use the protein range below when mixing today's ration.",
    'summary_hi': 'खिलाना सुरक्षित है। आज के राशन में नीचे दी गई प्रोटीन सीमा का उपयोग करें।',
  },
  'dilute': {
    'en': 'Dilute / mix',
    'hi': 'मिलाकर खिलाएँ',
    'summary_en': 'Do not feed this bag or pit alone. Mix with a safer lot and use soon.',
    'summary_hi': 'इस बोरी या साइलेज को अकेले न खिलाएँ। बेहतर चारे के साथ मिलाएँ और जल्दी उपयोग करें।',
  },
  'reject': {
    'en': 'Reject',
    'hi': 'न खिलाएँ',
    'summary_en': 'Do not feed. Discard or send a sample to the union lab.',
    'summary_hi': 'न खिलाएँ। फेंक दें या यूनियन लैब में नमूना भेजें।',
  },
};

const reasonCopy = {
  'urea at or above BIS 1%': {
    'en': 'Urea screen at or above the BIS 1% limit.',
    'hi': 'यूरिया जाँच BIS की 1% सीमा पर या उससे अधिक है।',
  },
  '4-DMAB yellow — suspect urea': {
    'en': '4-DMAB strip turned yellow — suspect added urea.',
    'hi': '4-DMAB पट्टी पीली हुई — मिलावटी यूरिया की आशंका।',
  },
  'visible mould': {
    'en': 'Visible mould on the sample.',
    'hi': 'नमूने पर फफूंद दिख रही है।',
  },
  'compounded-feed moisture above BIS 11%': {
    'en': 'Compounded feed moisture above BIS 11%. Store dry or use soon.',
    'hi': 'मिश्रित दाने में नमी BIS 11% से अधिक है। सुखाकर रखें या जल्दी खिलाएँ।',
  },
  'high-AF-risk ingredient plus mould': {
    'en': 'High aflatoxin-risk ingredient plus mould. Need a lab or strip test.',
    'hi': 'अफलाटॉक्सिन-जोखिम वाला चारा और फफूंद। लैब या स्ट्रिप जाँच चाहिए।',
  },
  'silage too wet — effluent and clostridia risk': {
    'en': 'Silage is very wet. Effluent runs off and butyric spoilage is likely.',
    'hi': 'साइलेज बहुत गीला है। रस बहने और खराब सड़न का खतरा है।',
  },
  'acid-insoluble ash above the BIS sand limit': {
    'en': 'Acid-insoluble ash above the BIS limit — sand or soil in the feed.',
    'hi': 'अम्ल-अघुलनशील राख BIS सीमा से अधिक — चारे में रेत या मिट्टी है।',
  },
  'grit settled in the jar test — suspect sand': {
    'en': 'Grit settled in the water jar — suspect sand. Get an AIA test.',
    'hi': 'पानी के जार में रेत बैठी — मिलावट की आशंका। AIA जाँच कराएँ।',
  },
  'no reject/dilute trigger from sensors + tables': {
    'en': 'No reject or dilute trigger from the sensors and tables.',
    'hi': 'सेंसर और तालिका से कोई अस्वीकार संकेत नहीं।',
  },
  'bag past expiry date (QR)': {
    'en': 'Bag is past its expiry date (from QR code).',
    'hi': 'बोरी की समाप्ति तिथि बीत चुकी है (QR कोड से)।',
  },
  'declared CP does not match tables (QR)': {
    'en': 'Declared crude protein on the bag does not match Indian tables (QR check).',
    'hi': 'बोरी पर लिखा प्रोटीन भारतीय तालिका से मेल नहीं खाता (QR जाँच)।',
  },
  'declared moisture does not match measurement (QR)': {
    'en': 'Declared moisture on the bag does not match the sensor reading (QR check).',
    'hi': 'बोरी पर लिखी नमी सेंसर रीडिंग से मेल नहीं खाती (QR जाँच)।',
  },
};

const prefixes = {
  'silage Flieg': {
    'en': 'Silage fermentation score is low.',
    'hi': 'साइलेज का किण्वन अंक कम है।',
  },
  'silage pH': {
    'en': 'Silage pH is above 4.2 on low dry matter — it never soured properly.',
    'hi': 'कम शुष्क पदार्थ पर साइलेज का pH 4.2 से ऊपर है — ठीक से खट्टा नहीं हुआ।',
  },
};

String translateReason(String reason, String lang) {
  final pack = reasonCopy[reason];
  if (pack != null) return pack[lang]!;
  for (final entry in prefixes.entries) {
    if (reason.startsWith(entry.key)) {
      return lang == 'hi' ? '${entry.value['hi']} ($reason)' : '${entry.value['en']} ($reason)';
    }
  }
  return reason;
}

Map<String, dynamic> farmerCard(Map<String, dynamic> decision) {
  final action = '${decision['action'] ?? 'feed'}';
  final pack = actionCopy[action] ?? actionCopy['feed']!;
  final other = List<String>.from(decision['other_flags'] ?? const []);
  final reasons = List<String>.from(decision['reasons'] ?? const []);
  return {
    'action': action,
    'label_en': pack['en'],
    'label_hi': pack['hi'],
    'summary_en': pack['summary_en'],
    'summary_hi': pack['summary_hi'],
    'reasons_en': [for (final r in reasons) translateReason(r, 'en')],
    'reasons_hi': [for (final r in reasons) translateReason(r, 'hi')],
    'other_flags_en': [for (final r in other) translateReason(r, 'en')],
    'other_flags_hi': [for (final r in other) translateReason(r, 'hi')],
  };
}

const role = {
  'crop_residue': ('Filler roughage', 'भराव चारा'),
  'hay': ('Roughage', 'सूखा चारा'),
  'silage': ('Succulent roughage', 'रसीला चारा'),
  'grains': ('Energy source', 'ऊर्जा स्रोत'),
  'byproducts': ('Mixed energy / fibre', 'मिश्रित ऊर्जा व रेशा'),
  'oilcakes': ('Protein source', 'प्रोटीन स्रोत'),
  'molasses': ('Energy / palatability', 'ऊर्जा व स्वाद'),
  'compounded': ('Balanced concentrate', 'संतुलित दाना'),
};

Map<String, dynamic> rationAdvice(Map<String, dynamic> nutrition) {
  final feedClass = nutrition['feed_class']?.toString();
  final pair = role[feedClass] ?? ('Feed ingredient', 'चारा सामग्री');
  final span = ((nutrition['nutrients_pct_dm'] as Map?)?['crude_protein_pct_dm'] as Map?);
  final cp = (span?['mean'] as num?)?.toDouble();
  const lo = 12.0, hi = 16.0;
  final tipsEn = <String>[];
  final tipsHi = <String>[];
  if (nutrition['method'] == 'bis_standard_only') {
    tipsEn.add('Check the bag label against BIS: Type I needs CP >= 22% DM.');
    tipsHi.add('बोरी के लेबल को BIS से मिलाएँ: टाइप I में CP कम से कम 22% DM।');
  } else if (cp == null) {
    tipsEn.add('No protein figure for this name. Pick the closest listed feed.');
    tipsHi.add('इस नाम का प्रोटीन आँकड़ा नहीं है। सूची से मिलता-जुलता चारा चुनें।');
  } else if (cp < 6) {
    tipsEn.add(
      'Only about $cp% CP. Well below the $lo-$hi% a milking ration needs, so it cannot be the whole feed. Add a cake or compounded feed and green fodder.',
    );
    tipsHi.add('केवल लगभग $cp% प्रोटीन। दुधारू राशन के $lo-$hi% से बहुत कम, अकेले न खिलाएँ। खली या दाना और हरा चारा मिलाएँ।');
  } else if (cp < lo) {
    tipsEn.add('About $cp% CP, under the $lo-$hi% ration target. Pair with a protein feed.');
    tipsHi.add('लगभग $cp% प्रोटीन, $lo-$hi% लक्ष्य से कम। प्रोटीन वाला चारा साथ दें।');
  } else if (cp > 25) {
    tipsEn.add('Protein-rich at about $cp% CP. Feed as a measured share of the concentrate, not free choice.');
    tipsHi.add('लगभग $cp% प्रोटीन, बहुत अधिक। नापकर दाने के हिस्से के रूप में दें, खुला नहीं।');
  } else {
    tipsEn.add('About $cp% CP, inside the $lo-$hi% ration band.');
    tipsHi.add('लगभग $cp% प्रोटीन, $lo-$hi% राशन सीमा के भीतर।');
  }
  if (feedClass == 'silage') {
    tipsEn.add("Keep the silo face tight and clean after taking today's cut.");
    tipsHi.add('आज का साइलेज निकालने के बाद गड्ढे का मुँह कसकर बंद रखें।');
  }
  if (nutrition['method'] == 'keyword_class_fallback' || nutrition['method'] == 'best_cv_name_model') {
    tipsEn.add('This name was not in the Indian tables, so the figure is a guess from the name.');
    tipsHi.add('यह नाम भारतीय तालिका में नहीं था, इसलिए यह आँकड़ा नाम से लगाया गया अनुमान है।');
  }
  // --- Mineral deficiency advisory ---
  if (feedClass == 'crop_residue' || feedClass == 'hay') {
    tipsEn.add('This roughage is low in Calcium and Phosphorus. Add 50–100 g Area-Specific Mineral Mixture (ASMM) daily per animal.');
    tipsHi.add('इस चारे में कैल्शियम और फ़ॉस्फ़ोरस कम है। प्रति पशु प्रतिदिन 50–100 ग्राम क्षेत्र-विशिष्ट खनिज मिश्रण (ASMM) दें।');
  } else if (feedClass == 'grains') {
    tipsEn.add('Grain-heavy diets lack minerals. Ensure a mineral mixture is part of the daily ration.');
    tipsHi.add('अनाज-प्रधान आहार में खनिज कम होते हैं। दैनिक राशन में खनिज मिश्रण अवश्य शामिल करें।');
  } else if (feedClass == 'oilcakes' && cp != null && cp > 30) {
    tipsEn.add('High-protein cakes can have a Calcium–Phosphorus imbalance. Balance with a mineral supplement.');
    tipsHi.add('अधिक प्रोटीन वाली खली में कैल्शियम-फ़ॉस्फ़ोरस असंतुलन हो सकता है। खनिज पूरक के साथ संतुलित करें।');
  }
  return {
    'role_en': pair.$1,
    'role_hi': pair.$2,
    'cp_pct_dm_mean': cp,
    'ration_cp_target_pct_dm': [lo, hi],
    'tips_en': tipsEn,
    'tips_hi': tipsHi,
    'note': "Guidance for one ingredient. It does not replace a nutritionist's balanced ration.",
  };
}

Map<String, double?>? _cpSpan(Map nutrition) {
  final span = ((nutrition['nutrients_pct_dm'] as Map?)?['crude_protein_pct_dm'] as Map?);
  if (span == null) return null;
  return {
    'mean': (span['mean'] as num?)?.toDouble(),
    'min': (span['min'] as num?)?.toDouble(),
    'max': (span['max'] as num?)?.toDouble(),
  };
}

Map<String, double?>? _asfedSpan(Map nutrition) {
  final span = ((nutrition['nutrients_as_fed'] as Map?)?['crude_protein_pct'] as Map?);
  if (span == null) return null;
  return {
    'mean': (span['mean'] as num?)?.toDouble(),
    'min': (span['min'] as num?)?.toDouble(),
    'max': (span['max'] as num?)?.toDouble(),
  };
}

Map<String, String> spokenAdvice(Map<String, dynamic> result) {
  final farmer = Map<String, dynamic>.from(result['farmer'] as Map? ?? {});
  final modules = Map<String, dynamic>.from(result['modules'] as Map? ?? {});
  final nutrition = Map<String, dynamic>.from(modules['nutrition'] as Map? ?? {});
  final moisture = Map<String, dynamic>.from(modules['moisture'] as Map? ?? {});
  final silage = Map<String, dynamic>.from(modules['silage'] as Map? ?? {});
  final nir = Map<String, dynamic>.from(modules['nir'] as Map? ?? {});
  final cv = Map<String, dynamic>.from(modules['cv'] as Map? ?? {});
  final ration = Map<String, dynamic>.from(result['ration'] as Map? ?? {});
  final name = '${result['ingredient'] ?? nutrition['canonical'] ?? 'this feed'}';
  final action = '${farmer['action'] ?? 'feed'}';
  return {
    'en': _english(name, action, farmer, nutrition, moisture, silage, nir, cv, ration, result),
    'hi': _hindi(name, action, farmer, nutrition, moisture, silage, nir, cv, ration, result),
  };
}

String _english(
  String name,
  String action,
  Map farmer,
  Map nutrition,
  Map moisture,
  Map silage,
  Map nir,
  Map cv,
  Map ration,
  Map result,
) {
  final parts = <String>['${farmer['label_en'] ?? 'Feed'}. ${farmer['summary_en'] ?? ''}'.trim()];
  parts.add('You tested $name.');
  final span = _cpSpan(nutrition);
  if (span != null && span['min'] != null) {
    parts.add(
      'Indian tables put crude protein around ${span['min']}–${span['max']}% on dry matter (about ${span['mean']}% typical).',
    );
  } else if (nutrition['method'] == 'bis_standard_only') {
    parts.add('This is compounded cattle feed. Check the bag against BIS Type I or Type II, not a photo.');
  }
  final asfed = _asfedSpan(nutrition);
  if (moisture['present'] == true && asfed != null && asfed['mean'] != null) {
    parts.add(
      'The moisture probe read ${moisture['moisture_pct']}%, so as-fed protein is about ${asfed['mean']}%. Moisture is not protein — it only converts the dry-matter table to what the cow actually eats.',
    );
  } else if (moisture['present'] == true) {
    parts.add('The moisture probe read ${moisture['moisture_pct']}%.');
  }
  if (silage['present'] == true && silage['flieg_score'] != null) {
    parts.add(
      'Silage pH ${silage['pH']} and dry matter ${silage['dm_pct']}% give a Flieg score of ${silage['flieg_score']} (${silage['class'] ?? ''}).',
    );
  } else if (silage['present'] == true) {
    parts.add('Silage pH is ${silage['pH']}. Add a moisture reading to finish the Flieg score.');
  }
  if (cv['flag'] == true) {
    final how = cv['method'] == 'hsv_screen' ? 'the photo' : 'your mould mark';
    parts.add('Mould showed on $how. Do not feed this lot; send a sample if you need an aflatoxin test.');
  } else if (cv['method'] == 'hsv_screen') {
    parts.add('The phone photo did not look mouldy on the colour screen. That is not an aflatoxin ppb result.');
  }
  if (nir['present'] == true && nir['used'] == false && '${nir['note']}'.contains('18')) {
    parts.add(
      'The kit colour chip sent 18 bands (410–940 nm). Those bands are stored but not used for protein — this chip cannot see the protein overtones.',
    );
  }
  final tips = List<String>.from(ration['tips_en'] ?? const []);
  if (tips.isNotEmpty) parts.add(tips.first);
  final reasons = List<String>.from(farmer['reasons_en'] ?? const []);
  if (action != 'feed' && reasons.isNotEmpty) parts.add('Main reason: ${reasons.first}');
  final warns = List<String>.from(result['sensor_warnings'] ?? const []);
  if (warns.isNotEmpty) parts.add('Check the probe: ${warns.first}');
  return parts.where((p) => p.trim().isNotEmpty).map((p) => p.trim()).join(' ');
}

String _hindi(
  String name,
  String action,
  Map farmer,
  Map nutrition,
  Map moisture,
  Map silage,
  Map nir,
  Map cv,
  Map ration,
  Map result,
) {
  final parts = <String>['${farmer['label_hi'] ?? 'खिलाएँ'}। ${farmer['summary_hi'] ?? ''}'.trim()];
  parts.add('आपने $name जाँचा।');
  final span = _cpSpan(nutrition);
  if (span != null && span['min'] != null) {
    parts.add('भारतीय तालिका में क्रूड प्रोटीन शुष्क पदार्थ पर लगभग ${span['min']}–${span['max']}% है (औसत ${span['mean']}%)।');
  } else if (nutrition['method'] == 'bis_standard_only') {
    parts.add('यह मिश्रित दाना है। बोरी को BIS टाइप I या II से मिलाएँ, फोटो से प्रोटीन नहीं निकलेगा।');
  }
  final asfed = _asfedSpan(nutrition);
  if (moisture['present'] == true && asfed != null && asfed['mean'] != null) {
    parts.add(
      'नमी सेंसर ने ${moisture['moisture_pct']}% दिखाया, इसलिए जैसे-खिलाया प्रोटीन लगभग ${asfed['mean']}% है। नमी प्रोटीन नहीं मापती — केवल तालिका को गाय के खाने योग्य आँकड़े में बदलती है।',
    );
  } else if (moisture['present'] == true) {
    parts.add('नमी सेंसर ने ${moisture['moisture_pct']}% दिखाया।');
  }
  if (silage['present'] == true && silage['flieg_score'] != null) {
    parts.add(
      'साइलेज pH ${silage['pH']} और शुष्क पदार्थ ${silage['dm_pct']}% से Flieg अंक ${silage['flieg_score']} (${silage['class'] ?? ''}) है।',
    );
  } else if (silage['present'] == true) {
    parts.add('साइलेज का pH ${silage['pH']} है। Flieg पूरा करने के लिए नमी भी लें।');
  }
  if (cv['flag'] == true) {
    final how = cv['method'] == 'hsv_screen' ? 'फोटो' : 'आपके फफूंद निशान';
    parts.add('$how पर फफूंद दिखी। यह लॉट न खिलाएँ; अफलाटॉक्सिन के लिए लैब भेजें।');
  } else if (cv['method'] == 'hsv_screen') {
    parts.add('फोन फोटो पर रंग-जाँच से फफूंद नहीं दिखी। यह अफलाटॉक्सिन ppb नहीं है।');
  }
  if (nir['present'] == true && nir['used'] == false && '${nir['note']}'.contains('18')) {
    parts.add('किट के रंग चिप ने 18 बैंड भेजे (410–940 नैनोमीटर)। ये प्रोटीन के लिए इस्तेमाल नहीं हुए — इस चिप पर प्रोटीन बैंड नहीं आते।');
  }
  final tips = List<String>.from(ration['tips_hi'] ?? const []);
  if (tips.isNotEmpty) parts.add(tips.first);
  final reasons = List<String>.from(farmer['reasons_hi'] ?? const []);
  if (action != 'feed' && reasons.isNotEmpty) parts.add('मुख्य कारण: ${reasons.first}');
  final warns = List<String>.from(result['sensor_warnings'] ?? const []);
  if (warns.isNotEmpty) parts.add('सेंसर जाँचें: ${warns.first}');
  return parts.where((p) => p.trim().isNotEmpty).map((p) => p.trim()).join(' ');
}
