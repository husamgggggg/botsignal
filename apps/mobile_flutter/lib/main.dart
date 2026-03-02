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
  final apiBaseUrl = prefs.getString('api_base_url') ?? 'http://localhost:3000';
  AppConfig.apiBaseUrl = apiBaseUrl;

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

