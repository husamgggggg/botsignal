import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'api_service.dart';

enum VerificationStatus {
  VERIFIED_ACTIVE,
  VERIFIED_NO_DEPOSIT,
  NOT_UNDER_TEAM,
  NOT_REGISTERED,
}

class VerifyService {
  final ApiService _apiService;

  VerifyService(this._apiService);

  Future<Map<String, dynamic>> verifyAccount({
    required String platform,
    required String accountId,
    required String deviceId,
    String? postbackUrl,
    String? lid,
    String? clickId,
    String? siteId,
  }) async {
    try {
      // Always use API for verification - API will handle postback verification server-side
      // This avoids CORS issues and keeps the logic centralized
      // Don't send placeholder URLs (example.com) to API
      final Map<String, dynamic> requestData = {
        'platform': platform,
        'accountId': accountId,
        'deviceId': deviceId,
      };
      
      // Only include postback config if it's a real URL (not placeholder)
      if (postbackUrl != null && 
          postbackUrl.isNotEmpty && 
          !postbackUrl.contains('example.com')) {
        requestData['postbackUrl'] = postbackUrl;
        if (lid != null && lid.isNotEmpty) {
          requestData['lid'] = lid;
        }
        if (clickId != null && clickId.isNotEmpty) {
          requestData['clickId'] = clickId;
        }
        if (siteId != null && siteId.isNotEmpty) {
          requestData['siteId'] = siteId;
        }
      }
      
      final response = await _apiService.dio.post(
        '/verify',
        data: requestData,
      );
      return response.data;
    } on DioException catch (e) {
      throw Exception(e.response?.data?['message'] ?? 'Failed to verify account');
    }
  }
}

