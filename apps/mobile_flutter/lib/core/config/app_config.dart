import 'package:flutter/foundation.dart';

class AppConfig {
  // Get API base URL from environment variable or use default
  static String get apiBaseUrl {
    final envUrl = const String.fromEnvironment('API_URL', defaultValue: '');
    if (envUrl.isNotEmpty) {
      return envUrl;
    }
    // For web, use relative path (same origin)
    if (kIsWeb) {
      return '';
    }
    // For mobile, default to localhost
    return 'http://localhost:3000';
  }
  
  static String get apiUrl {
    final base = apiBaseUrl;
    if (base.isEmpty) {
      // Relative path for web
      return '/api';
    }
    return '$base/api';
  }
  
  // Get API URL based on platform
  static String getApiUrl() {
    return apiUrl;
  }
}

