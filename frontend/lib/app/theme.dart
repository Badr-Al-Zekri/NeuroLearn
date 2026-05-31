import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

const surface = Color(0xFF111416);
const panel = Color(0xFF171B1D);
const border = Color(0xFF293136);
const accent = Color(0xFF6DDEC9);
const accentBlue = Color(0xFF89B8E8);
const danger = Color(0xFFF87171);

ThemeData buildNeuroLearnTheme() {
  final base = ThemeData.dark(useMaterial3: true);
  return base.copyWith(
    scaffoldBackgroundColor: const Color(0xFF0B0E10),
    colorScheme: const ColorScheme.dark(
      primary: accent,
      secondary: accentBlue,
      surface: surface,
      error: danger,
    ),
    textTheme: GoogleFonts.interTextTheme(base.textTheme).apply(
      bodyColor: const Color(0xFFE5ECFF),
      displayColor: Colors.white,
    ),
    cardTheme: CardThemeData(
      color: panel,
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(8),
        side: const BorderSide(color: border),
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: const Color(0xFF121719),
      border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: const BorderSide(color: border),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: const BorderSide(color: accent),
      ),
    ),
    navigationBarTheme: const NavigationBarThemeData(
      backgroundColor: surface,
      indicatorColor: Color(0x226DDEC9),
      labelTextStyle: WidgetStatePropertyAll(TextStyle(fontSize: 12, fontWeight: FontWeight.w700)),
    ),
  );
}
