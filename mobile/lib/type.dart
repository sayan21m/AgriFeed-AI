import 'package:flutter/material.dart';
import 'package:smartfeed_app/brand.dart';

/// Village-kit type: Source Serif 4 for display, Hind for UI + Hindi.
class Type {
  static const display = 'SourceSerif';
  static const ui = 'Hind';
  static const hindi = 'HindDevanagari';
  static const fallback = [hindi];

  static const photoShadow = [
    Shadow(color: Color(0xCC000000), blurRadius: 8, offset: Offset(0, 1)),
    Shadow(color: Color(0x99000000), blurRadius: 2, offset: Offset(0, 1)),
  ];

  static TextStyle kicker({Color color = Brand.onPhotoSoft}) => TextStyle(
        fontFamily: ui,
        fontFamilyFallback: fallback,
        fontSize: 11,
        fontWeight: FontWeight.w700,
        letterSpacing: 1.5,
        height: 1.25,
        color: color,
      );

  static TextStyle onPhoto({double size = 15, FontWeight weight = FontWeight.w600}) => TextStyle(
        fontFamily: ui,
        fontFamilyFallback: fallback,
        fontSize: size,
        fontWeight: weight,
        height: 1.3,
        color: Brand.onPhoto,
        shadows: photoShadow,
      );

  static TextStyle displayLg({Color color = Brand.ink}) => TextStyle(
        fontFamily: display,
        fontFamilyFallback: fallback,
        fontSize: 32,
        fontWeight: FontWeight.w700,
        height: 1.15,
        letterSpacing: -0.3,
        color: color,
        shadows: color == Brand.onPhoto || color == Colors.white ? photoShadow : null,
      );

  static TextStyle displayMd({Color color = Brand.ink}) => TextStyle(
        fontFamily: display,
        fontFamilyFallback: fallback,
        fontSize: 22,
        fontWeight: FontWeight.w700,
        height: 1.25,
        letterSpacing: -0.15,
        color: color,
        shadows: color == Brand.onPhoto || color == Colors.white ? photoShadow : null,
      );

  static TextStyle title({Color color = Brand.ink}) => TextStyle(
        fontFamily: display,
        fontFamilyFallback: fallback,
        fontSize: 17,
        fontWeight: FontWeight.w600,
        height: 1.25,
        color: color,
      );

  static TextStyle section({Color color = Brand.ink}) => TextStyle(
        fontFamily: ui,
        fontFamilyFallback: fallback,
        fontSize: 13,
        fontWeight: FontWeight.w700,
        letterSpacing: 0.8,
        height: 1.2,
        color: color,
      );

  static TextStyle body({Color color = Brand.ink, double size = 15}) => TextStyle(
        fontFamily: ui,
        fontFamilyFallback: fallback,
        fontSize: size,
        fontWeight: FontWeight.w500,
        height: 1.45,
        color: color,
        shadows: color == Brand.onPhoto || color == Colors.white ? photoShadow : null,
      );

  static TextStyle bodyStrong({Color color = Brand.ink}) => TextStyle(
        fontFamily: ui,
        fontFamilyFallback: fallback,
        fontSize: 15,
        fontWeight: FontWeight.w600,
        height: 1.35,
        color: color,
      );

  static TextStyle label({Color color = Brand.mute}) => TextStyle(
        fontFamily: ui,
        fontFamilyFallback: fallback,
        fontSize: 13,
        fontWeight: FontWeight.w700,
        height: 1.25,
        color: color,
      );

  static TextStyle metric({Color color = Brand.ink}) => TextStyle(
        fontFamily: ui,
        fontFamilyFallback: fallback,
        fontSize: 14.5,
        fontWeight: FontWeight.w700,
        height: 1.25,
        color: color,
      );

  static TextStyle button() => const TextStyle(
        fontFamily: ui,
        fontFamilyFallback: fallback,
        fontSize: 15,
        fontWeight: FontWeight.w700,
        letterSpacing: 0.2,
      );

  static TextStyle nav() => const TextStyle(
        fontFamily: ui,
        fontFamilyFallback: fallback,
        fontWeight: FontWeight.w700,
        fontSize: 12,
        color: Brand.ink,
      );
}
