import 'dart:io';
import 'dart:math';
import 'dart:typed_data';

import 'package:image/image.dart' as img;

Map<String, dynamic> mouldScoreRgb(Uint8List rgb, int nPix) {
  var green = 0, dark = 0, whiteFuzzy = 0;
  for (var i = 0; i < nPix; i++) {
    final r = rgb[i * 3] / 255.0;
    final g = rgb[i * 3 + 1] / 255.0;
    final b = rgb[i * 3 + 2] / 255.0;
    final mx = max(r, max(g, b));
    final mn = min(r, min(g, b));
    final diff = mx - mn;
    final s = mx == 0 ? 0.0 : diff / max(mx, 1e-6);
    final v = mx;
    var h = 0.0;
    if (diff > 1e-6) {
      if (mx == r) {
        h = ((g - b) / diff) % 6;
      } else if (mx == g) {
        h = (b - r) / diff + 2;
      } else {
        h = (r - g) / diff + 4;
      }
      h *= 60.0;
      if (h < 0) h += 360;
    }
    if (h > 70 && h < 170 && s > 0.18 && v > 0.15) green++;
    if (v < 0.18 && s < 0.35) dark++;
    if (v > 0.75 && s < 0.18) whiteFuzzy++;
  }
  final gf = green / nPix;
  final df = dark / nPix;
  final wf = whiteFuzzy / nPix;
  final score = min(1.0, 2.2 * gf + 0.9 * df + 0.5 * wf);
  return {
    'green_frac': double.parse(gf.toStringAsFixed(4)),
    'dark_frac': double.parse(df.toStringAsFixed(4)),
    'white_frac': double.parse(wf.toStringAsFixed(4)),
    'mould_score': double.parse(score.toStringAsFixed(3)),
    'flag': score >= 0.12,
  };
}

Map<String, dynamic> mouldScoreImage(img.Image rgb) {
  final w = rgb.width;
  final h = rgb.height;
  final pix = Uint8List(w * h * 3);
  var i = 0;
  for (var y = 0; y < h; y++) {
    for (var x = 0; x < w; x++) {
      final p = rgb.getPixel(x, y);
      pix[i++] = p.r.toInt();
      pix[i++] = p.g.toInt();
      pix[i++] = p.b.toInt();
    }
  }
  return mouldScoreRgb(pix, w * h);
}

Map<String, dynamic> assessImage({String? imagePath, bool? visibleMould}) {
  if (imagePath != null) {
    final file = File(imagePath);
    if (!file.existsSync()) {
      return {'present': false, 'note': 'Image not found: $imagePath'};
    }
    final decoded = img.decodeImage(file.readAsBytesSync());
    if (decoded == null) {
      return {'present': false, 'note': 'Could not read the photo.'};
    }
    var rgb = decoded.convert(numChannels: 3);
    if (rgb.width > 128 || rgb.height > 128) {
      rgb = rgb.width >= rgb.height
          ? img.copyResize(rgb, width: 128)
          : img.copyResize(rgb, height: 128);
    }
    final hsv = mouldScoreImage(rgb);
    return {
      'present': true,
      'method': 'hsv_screen',
      'image': imagePath,
      ...hsv,
      'note':
          'Colour screen only on this phone (not the synthetic CNN). Green fodder can false-flag. Petri-dish or bag mould ≠ AFB1 µg/kg.',
    };
  }
  if (visibleMould == null) {
    return {'present': false, 'note': 'No photo and no farmer mould flag.'};
  }
  return {
    'present': true,
    'method': 'farmer_flag',
    'mould_score': visibleMould ? 1.0 : 0.0,
    'flag': visibleMould,
    'note': 'Farmer-reported visible mould. Do not convert this to ppb.',
  };
}
