import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';

/// A custom delegate that provides Arabic support for Material localizations
/// This prevents warnings about unsupported locales
class ArabicMaterialLocalizationsDelegate
    extends LocalizationsDelegate<MaterialLocalizations> {
  const ArabicMaterialLocalizationsDelegate();

  @override
  bool isSupported(Locale locale) {
    // Support both Arabic and English
    return locale.languageCode == 'ar' || locale.languageCode == 'en';
  }

  @override
  Future<MaterialLocalizations> load(Locale locale) async {
    // For Arabic, fall back to English Material localizations
    // This prevents warnings while still providing functionality
    final fallbackLocale = locale.languageCode == 'ar' 
        ? const Locale('en') 
        : locale;
    return GlobalMaterialLocalizations.delegate.load(fallbackLocale);
  }

  @override
  bool shouldReload(ArabicMaterialLocalizationsDelegate old) => false;
}

/// A custom delegate that provides Arabic support for Widgets localizations
class ArabicWidgetsLocalizationsDelegate
    extends LocalizationsDelegate<WidgetsLocalizations> {
  const ArabicWidgetsLocalizationsDelegate();

  @override
  bool isSupported(Locale locale) {
    return locale.languageCode == 'ar' || locale.languageCode == 'en';
  }

  @override
  Future<WidgetsLocalizations> load(Locale locale) async {
    final fallbackLocale = locale.languageCode == 'ar' 
        ? const Locale('en') 
        : locale;
    return GlobalWidgetsLocalizations.delegate.load(fallbackLocale);
  }

  @override
  bool shouldReload(ArabicWidgetsLocalizationsDelegate old) => false;
}

