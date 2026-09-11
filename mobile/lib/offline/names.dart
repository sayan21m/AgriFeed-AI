// Ingredient name normalisation — same aliases as `smartfeed/names.py`.

const replacements = <(String, String)>[
  ('rice bran (de-oiled)', 'deoiled rice bran'),
  ('rice bran (deoiled)', 'deoiled rice bran'),
  ('cottonseed meal (undecorticated)', 'cottonseed cake undecorticated'),
  ('cottonseed meal (decorticated)', 'cottonseed meal'),
  ('cottonseed oil cake (undecorticated)', 'cottonseed cake undecorticated'),
  ('un-decorticated cottonseed cake', 'cottonseed cake undecorticated'),
  ('sunflower meal (undecorticated)', 'sunflower meal'),
  ('mustard seed cake', 'mustard cake'),
  ('rapeseed oil cake', 'mustard cake'),
  ('rape seed cake', 'mustard cake'),
  ('rapeseed meal', 'mustard meal'),
  ('deoiled mustard cake', 'mustard meal'),
  ('groundnut oil cake', 'groundnut cake'),
  ('groundnut meal', 'groundnut meal'),
  ('soyabean meal', 'soybean meal'),
  ('coconut oil cake', 'coconut cake'),
  ('sesame oil cake', 'til cake'),
  ('til oil cake', 'til cake'),
  ('linseed oil cake', 'linseed cake'),
  ('wheat bran a', 'wheat bran'),
  ('wheat bran b', 'wheat bran'),
  ('maize grain', 'maize'),
  ('barley grain', 'barley'),
  ('oat grain', 'oats'),
  ('wheat grain', 'wheat'),
  ('broken rice', 'rice'),
  ('rice grit', 'rice'),
  ('cane molasses', 'molasses'),
  ('jowar', 'sorghum'),
  ('cotton seed cake', 'cottonseed cake'),
  ('dorb', 'deoiled rice bran'),
  ('gnc', 'groundnut cake'),
  ('sarson khali', 'mustard cake'),
  ('sarson cake', 'mustard cake'),
  ('binola khali', 'cottonseed cake undecorticated'),
  ('wheat chokar', 'wheat bran'),
  ('chokar', 'wheat bran'),
  ('gram flour', 'gram'),
  ('tuar chuni', 'arhar chuni'),
];

const farmerAliases = {
  'maize silage': 'maize silage',
  'corn silage': 'maize silage',
  'wheat silage': 'wheat silage',
  'compounded cattle feed': 'compounded feed',
  'cattle feed': 'compounded feed',
  'oat': 'oats',
};

String normalizeName(String name) {
  var text = name.trim().toLowerCase();
  text = text.replaceAll('de-oiled', 'deoiled').replaceAll('soyabean', 'soybean');
  text = text.replaceAll(RegExp(r'[()]'), ' ');
  text = text.replaceAll('-', ' ');
  text = text.replaceAll(RegExp(r'[^a-z0-9\s]'), ' ');
  text = text.replaceAll(RegExp(r'\s+'), ' ').trim();
  text = text.replaceAll('de oiled', 'deoiled');
  if (farmerAliases.containsKey(text)) return farmerAliases[text]!;
  for (final pair in replacements) {
    final src = pair.$1;
    final dst = pair.$2;
    if (text == src || text.startsWith('$src ')) {
      return (dst + text.substring(src.length)).trim();
    }
  }
  return text;
}

/// Keyword class fallback on the phone (not ExtraTrees; not on the ESP32).
String keywordClass(String canonical) {
  final s = canonical.toLowerCase();
  if (s.contains('silage')) return 'silage';
  if (s.contains('straw') || s.contains('stover') || s.contains('bhusa')) return 'crop_residue';
  if (s.contains('hay')) return 'hay';
  if (s.contains('molasses')) return 'molasses';
  if (s.contains('bran') || s.contains('chuni') || s.contains('husk')) return 'byproducts';
  if (s.contains('cake') || s.contains('khali') || s.contains('meal')) return 'oilcakes';
  if (s.contains('grain')) return 'grains';
  return 'byproducts';
}

double sequenceRatio(String a, String b) {
  if (a == b) return 1;
  if (a.isEmpty || b.isEmpty) return 0;
  return 2.0 * _matching(a, b) / (a.length + b.length);
}

int _matching(String a, String b) {
  var total = 0;
  void rec(int alo, int ahi, int blo, int bhi) {
    var bestLen = 0, bestAi = alo, bestBi = blo;
    for (var i = alo; i < ahi; i++) {
      for (var j = blo; j < bhi; j++) {
        var k = 0;
        while (i + k < ahi && j + k < bhi && a[i + k] == b[j + k]) {
          k++;
        }
        if (k > bestLen) {
          bestLen = k;
          bestAi = i;
          bestBi = j;
        }
      }
    }
    if (bestLen == 0) return;
    total += bestLen;
    rec(alo, bestAi, blo, bestBi);
    rec(bestAi + bestLen, ahi, bestBi + bestLen, bhi);
  }

  rec(0, a.length, 0, b.length);
  return total;
}
