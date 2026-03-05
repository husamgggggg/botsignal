import 'package:dio/dio.dart';
import 'api_service.dart';

class PlatformsService {
  final ApiService _apiService;

  PlatformsService(this._apiService);

  Future<Map<String, dynamic>> getPlatforms() async {
    try {
      final response = await _apiService.dio.get('/platforms');
      return response.data;
    } on DioException catch (e) {
      throw Exception(e.response?.data?['message'] ?? 'Failed to fetch platforms');
    }
  }

  /// Get postback configuration for a platform
  Future<Map<String, dynamic>?> getPostbackConfig(String platformId) async {
    try {
      final response = await _apiService.dio.get('/platforms/$platformId/postback');
      return response.data;
    } on DioException {
      // Postback config is optional, return null if not found
      return null;
    }
  }

  /// Get affiliate URL for a platform
  String getAffiliateUrl(String platformId, {String? lid, String? clickId, String? siteId}) {
    // Default affiliate URLs
    if (platformId == 'QUOTEX') {
      final lidValue = lid ?? '1549667'; // Default LID
      final baseUrl = 'https://broker-qx.pro/sign-up/?lid=$lidValue';
      
      final params = <String>[];
      if (clickId != null && clickId.isNotEmpty) {
        params.add('click_id=$clickId');
      }
      if (siteId != null && siteId.isNotEmpty) {
        params.add('site_id=$siteId');
      }
      
      if (params.isNotEmpty) {
        return '$baseUrl&${params.join('&')}';
      }
      return baseUrl;
    }
    
    // Add other platforms here
    return '';
  }

  /// Extract LID from affiliate URL or return default
  String getLidFromAffiliateUrl(String platformId, {String? customLid}) {
    if (customLid != null && customLid.isNotEmpty) {
      return customLid;
    }
    
    // Default LID for Quotex
    if (platformId == 'QUOTEX') {
      return '1549667';
    }
    
    return '';
  }

  /// Get default postback URL for a platform
  /// Returns null to avoid using placeholder URLs
  String? getDefaultPostbackUrl(String platformId) {
    // Don't return placeholder URLs - they cause CORS errors
    // Real postback URLs should be configured in the API
    return null;
  }
}

