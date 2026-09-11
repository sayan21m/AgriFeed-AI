import 'package:flutter/material.dart';
import 'package:smartfeed_app/brand.dart';
import 'package:smartfeed_app/home.dart';
import 'package:smartfeed_app/type.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const SmartFeedApp());
}

class SmartFeedApp extends StatelessWidget {
  const SmartFeedApp({super.key});

  @override
  Widget build(BuildContext context) {
    final base = ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: Brand.leaf,
        brightness: Brightness.light,
        surface: Brand.cream,
      ),
    );
    return MaterialApp(
      title: 'AgriFeed-AI',
      debugShowCheckedModeBanner: false,
      theme: base.copyWith(
        scaffoldBackgroundColor: Brand.cream,
        textTheme: base.textTheme.apply(
          fontFamily: Type.ui,
          fontFamilyFallback: Type.fallback,
          bodyColor: Brand.ink,
          displayColor: Brand.ink,
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: Brand.forest,
          foregroundColor: Brand.cream,
          elevation: 0,
        ),
        navigationBarTheme: NavigationBarThemeData(
          backgroundColor: Brand.paper,
          indicatorColor: const Color(0xFFDCE8D9),
          height: 68,
          iconTheme: WidgetStateProperty.resolveWith((s) {
            final selected = s.contains(WidgetState.selected);
            return IconThemeData(color: selected ? Brand.forest : Brand.mute, size: 24);
          }),
          labelTextStyle: WidgetStateProperty.resolveWith((s) {
            final selected = s.contains(WidgetState.selected);
            return Type.nav().copyWith(color: selected ? Brand.forest : Brand.mute);
          }),
        ),
        filledButtonTheme: FilledButtonThemeData(
          style: FilledButton.styleFrom(
            backgroundColor: Brand.leaf,
            foregroundColor: Colors.white,
            minimumSize: const Size(64, 48),
            textStyle: Type.button(),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
          ),
        ),
        outlinedButtonTheme: OutlinedButtonThemeData(
          style: OutlinedButton.styleFrom(
            foregroundColor: Brand.forest,
            minimumSize: const Size(0, 46),
            textStyle: Type.button(),
            side: const BorderSide(color: Brand.forest, width: 1.2),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
          ),
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: Colors.white,
          isDense: true,
          contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
          labelStyle: Type.label(color: Brand.forest),
          floatingLabelStyle: Type.label(color: Brand.forest),
          hintStyle: Type.body(color: Brand.mute, size: 14),
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: const BorderSide(color: Color(0xFFD9CDB6))),
          enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: const BorderSide(color: Color(0xFFD9CDB6))),
          focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: const BorderSide(color: Brand.leaf, width: 1.6)),
        ),
        listTileTheme: const ListTileThemeData(
          dense: true,
          minLeadingWidth: 28,
          contentPadding: EdgeInsets.symmetric(horizontal: 0, vertical: 2),
          visualDensity: VisualDensity(horizontal: 0, vertical: -1),
        ),
      ),
      home: const HomePage(),
    );
  }
}
