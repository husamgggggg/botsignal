import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
// import 'package:firebase_core/firebase_core.dart'; // Disabled for web compatibility
import 'package:shared_preferences/shared_preferences.dart';
import 'package:uuid/uuid.dart';

import 'core/config/app_config.dart';
import 'core/routing/app_router.dart';
import 'core/theme/app_theme.dart';
import 'core/localization/app_localizations.dart';
import 'core/localization/arabic_material_localizations.dart';
import 'core/providers/auth_provider.dart';
import 'core/providers/locale_provider.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize Firebase (disabled for now - enable when needed for mobile)
  // if (!kIsWeb) {
  //   try {
  //     await Firebase.initializeApp();
  //   } catch (e) {
  //     print('Firebase initialization error: $e');
  //   }
  // }

  // Initialize device ID
  final prefs = await SharedPreferences.getInstance();
  String? deviceId = prefs.getString('device_id');
  if (deviceId == null || deviceId.isEmpty) {
    deviceId = const Uuid().v4();
    await prefs.setString('device_id', deviceId);
  }

  // Initialize API base URL
  // Check if API_URL was set at compile time via --dart-define
  final envApiUrl = const String.fromEnvironment('API_URL', defaultValue: '');
  if (envApiUrl.isNotEmpty) {
    // Use compile-time value (already set in AppConfig)
    // No need to change it
  } else {
    // Fallback to SharedPreferences or default
    final savedApiUrl = prefs.getString('api_base_url');
    if (savedApiUrl != null && savedApiUrl.isNotEmpty) {
      // Note: Can't change const at runtime, but for web we use relative paths
      // This is mainly for mobile apps
    }
  }

  runApp(
    ProviderScope(
      child: MyApp(deviceId: deviceId),
    ),
  );
}

class MyApp extends ConsumerWidget {
  final String deviceId;

  const MyApp({super.key, required this.deviceId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(routerProvider);
    final locale = ref.watch(localeProvider);

    // Initialize auth on startup
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(authProvider.notifier).initialize(deviceId);
    });

    return MaterialApp.router(
      title: 'Signal App',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.darkTheme,
      locale: locale,
      supportedLocales: const [
        Locale('ar'),
        Locale('en'),
      ],
      localizationsDelegates: const [
        AppLocalizations.delegate,
        // Use custom delegates that handle Arabic gracefully
        ArabicMaterialLocalizationsDelegate(),
        ArabicWidgetsLocalizationsDelegate(),
        GlobalCupertinoLocalizations.delegate,
      ],
      routerConfig: router,
    );
  }
}

