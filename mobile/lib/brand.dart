import 'package:flutter/material.dart';
import 'package:smartfeed_app/type.dart';

class Brand {
  static const forest = Color(0xFF1B3A24);
  static const leaf = Color(0xFF2A5A34);
  static const cream = Color(0xFFF4EBD8);
  static const paper = Color(0xFFFFFBF3);
  static const ink = Color(0xFF101610);
  static const mute = Color(0xFF334033);
  static const onPhoto = Color(0xFFFFFFF4);
  static const onPhotoSoft = Color(0xFFF6E9C8);
  static const saffron = Color(0xFF8A5A00);
  static const reject = Color(0xFF8B2E24);
  static const dilute = Color(0xFF9A6B12);
  static const feed = Color(0xFF2F6B3A);

  static const hero = 'assets/images/hero_cattle.jpg';
  static const barn = 'assets/images/barn.jpg';
  static const cow = 'assets/images/cow.jpg';
  static const grain = 'assets/images/grain.jpg';
  static const hay = 'assets/images/hay.jpg';
  static const forage = 'assets/images/forage.jpg';
  static const fields = 'assets/images/silage.jpg';
  static const mark = 'assets/images/mark.jpg';

  static const pagePad = EdgeInsets.fromLTRB(20, 16, 20, 32);
  static const gap = 12.0;
  static const inset = 18.0;

  static String verdictPhoto(String action) {
    return switch (action) {
      'reject' => cow,
      'dilute' => hay,
      _ => barn,
    };
  }
}

class PhotoScrim extends StatelessWidget {
  const PhotoScrim({
    super.key,
    required this.asset,
    required this.child,
    this.height = 188,
    this.alignment = Alignment.bottomLeft,
    this.dark = 0.78,
  });

  final String asset;
  final Widget child;
  final double height;
  final Alignment alignment;
  final double dark;

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(22),
      child: SizedBox(
        height: height,
        width: double.infinity,
        child: Stack(
          fit: StackFit.expand,
          children: [
            Image.asset(asset, fit: BoxFit.cover),
            DecoratedBox(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    Colors.black.withValues(alpha: 0.28),
                    Colors.black.withValues(alpha: dark * 0.55),
                    Colors.black.withValues(alpha: dark),
                  ],
                  stops: const [0.0, 0.45, 1.0],
                ),
              ),
            ),
            Align(
              alignment: alignment,
              child: Padding(padding: const EdgeInsets.fromLTRB(18, 16, 18, 16), child: child),
            ),
          ],
        ),
      ),
    );
  }
}

class PaperCard extends StatelessWidget {
  const PaperCard({super.key, required this.child, this.padding = const EdgeInsets.all(Brand.inset)});
  final Widget child;
  final EdgeInsets padding;

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 14),
      padding: padding,
      decoration: BoxDecoration(
        color: Brand.paper,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: const Color(0xFFE4D7BE)),
        boxShadow: const [
          BoxShadow(color: Color(0x1A1B3A24), blurRadius: 18, offset: Offset(0, 8)),
        ],
      ),
      child: child,
    );
  }
}

class FormPhotoTile extends StatelessWidget {
  const FormPhotoTile({
    super.key,
    required this.asset,
    required this.label,
    required this.selected,
    required this.onTap,
  });

  final String asset;
  final String label;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: GestureDetector(
        onTap: onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 180),
          height: 104,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
              color: selected ? Brand.leaf : const Color(0xFFD9CDB6),
              width: selected ? 2.5 : 1,
            ),
            boxShadow: selected
                ? const [BoxShadow(color: Color(0x332F6B3A), blurRadius: 10, offset: Offset(0, 4))]
                : null,
          ),
          clipBehavior: Clip.antiAlias,
          child: Stack(
            fit: StackFit.expand,
            children: [
              Image.asset(asset, fit: BoxFit.cover),
              DecoratedBox(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topCenter,
                    end: Alignment.bottomCenter,
                    colors: [
                      Colors.black.withValues(alpha: 0.18),
                      Colors.black.withValues(alpha: selected ? 0.82 : 0.74),
                    ],
                  ),
                ),
              ),
              Align(
                alignment: Alignment.bottomCenter,
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(6, 0, 6, 8),
                  child: Text(
                    label,
                    textAlign: TextAlign.center,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: Type.onPhoto(size: 12.5, weight: FontWeight.w700),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
