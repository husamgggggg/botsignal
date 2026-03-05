import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../features/onboarding/screens/platform_select_screen.dart';
import '../../features/onboarding/screens/account_verify_screen.dart';
import '../../features/onboarding/screens/verify_result_screen.dart';
import '../../features/home/screens/home_screen.dart';
import '../../features/signals/screens/signal_details_screen.dart';
import '../../features/news/screens/news_screen.dart';
import '../../features/settings/screens/settings_screen.dart';

final routerProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: '/platform-select',
    routes: [
      GoRoute(
        path: '/platform-select',
        builder: (context, state) => const PlatformSelectScreen(),
      ),
      GoRoute(
        path: '/account-verify',
        builder: (context, state) {
          final platform = state.uri.queryParameters['platform'] ?? 'QUOTEX';
          return AccountVerifyScreen(platform: platform);
        },
      ),
      GoRoute(
        path: '/verify-result',
        builder: (context, state) {
          final status = state.uri.queryParameters['status'] ?? '';
          final messageAr = state.uri.queryParameters['messageAr'] ?? '';
          final messageEn = state.uri.queryParameters['messageEn'] ?? '';
          final platform = state.uri.queryParameters['platform'] ?? 'QUOTEX';
          return VerifyResultScreen(
            status: status,
            messageAr: messageAr,
            messageEn: messageEn,
            platform: platform,
          );
        },
      ),
      GoRoute(
        path: '/home',
        builder: (context, state) {
          // Check auth in builder instead of redirect
          return const HomeScreen();
        },
      ),
      GoRoute(
        path: '/signal/:id',
        builder: (context, state) {
          final signalId = state.pathParameters['id'] ?? '';
          return SignalDetailsScreen(signalId: signalId);
        },
      ),
      GoRoute(
        path: '/news',
        builder: (context, state) => const NewsScreen(),
      ),
      GoRoute(
        path: '/settings',
        builder: (context, state) => const SettingsScreen(),
      ),
    ],
    // Temporarily disable redirect to allow navigation to work
    // redirect: (context, state) => null,
    errorBuilder: (context, state) {
      // Show error page if route not found
      return Scaffold(
        appBar: AppBar(title: const Text('Error')),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Text('Route not found'),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: () => context.go('/platform-select'),
                child: const Text('Go Home'),
              ),
            ],
          ),
        ),
      );
    },
  );
});

