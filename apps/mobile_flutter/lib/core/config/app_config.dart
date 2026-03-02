import 'package:flutter/foundation.dart';

class AppConfig {
  static String apiBaseUrl = 'http://localhost:3000';
  
  static String get apiUrl => '$apiBaseUrl/api';
  
  // Get API URL based on platform
  static String getApiUrl() {
    if (kIsWeb) {
      // For web, use the same origin or configured URL
      // In production, this should be your actual API domain
      return apiUrl;
    } else {
      // For mobile, use the configured URL
      return apiUrl;
    }
  }
}

