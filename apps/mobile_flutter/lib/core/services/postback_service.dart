import 'package:dio/dio.dart';
import 'api_service.dart';

/// Service to handle postback verification for Quotex
class PostbackService {
  final Dio _dio;

  PostbackService(ApiService apiService) : _dio = Dio();

  /// Verify account via postback
  /// Returns true if user is registered and has balance
  Future<Map<String, dynamic>> verifyPostback({
    required String accountId,
    required String postbackUrl,
    String? lid,
    String? clickId,
    String? siteId,
  }) async {
    try {
      // Build postback URL with parameters
      // Format: https://example.com/postback.php?status={status}&{status}=true&eid={event_id}&cid={click_id}&sid={site_id}&lid={lid}&uid={trader_id}...
      final uri = Uri.parse(postbackUrl);
      final queryParams = <String, String>{
        'uid': accountId, // trader_id - هذا هو Account ID الذي يدخله المستخدم
        if (lid != null && lid.isNotEmpty) 'lid': lid,
        if (clickId != null && clickId.isNotEmpty) 'cid': clickId,
        if (siteId != null && siteId.isNotEmpty) 'sid': siteId,
      };

      final postbackUri = uri.replace(queryParameters: queryParams);

      // Call postback URL to check status
      // Use separate Dio instance for external URLs
      final response = await _dio.get(
        postbackUri.toString(),
        options: Options(
          validateStatus: (status) => status! < 500, // Accept any status < 500
          followRedirects: true,
        ),
      );

      // Parse response - postback may return JSON, XML, or plain text
      dynamic data;
      try {
        data = response.data;
        // If response is a string, try to parse as JSON
        if (data is String) {
          try {
            data = response.data; // Dio should auto-parse JSON
          } catch (e) {
            // If not JSON, parse query parameters from response
            final responseUri = Uri.tryParse(data);
            if (responseUri != null) {
              data = responseUri.queryParameters;
            } else {
              data = {'raw': data};
            }
          }
        }
      } catch (e) {
        // If parsing fails, use query parameters from URL
        data = postbackUri.queryParameters;
      }
      
      // Check if user is registered (reg or conf status)
      final isRegistered = _checkRegistrationStatus(data);
      
      // Check if user has balance (ftd or dep status)
      final hasBalance = _checkBalanceStatus(data);

      return {
        'isRegistered': isRegistered,
        'hasBalance': hasBalance,
        'status': _determineStatus(isRegistered, hasBalance),
        'postbackData': data,
      };
    } on DioException catch (e) {
      throw Exception('Postback verification failed: ${e.message}');
    }
  }

  /// Check if user is registered (reg or conf status)
  bool _checkRegistrationStatus(dynamic postbackData) {
    if (postbackData is Map) {
      // Check if status indicates registration
      final status = postbackData['status']?.toString().toLowerCase();
      final reg = postbackData['reg']?.toString().toLowerCase();
      final conf = postbackData['conf']?.toString().toLowerCase();

      return (status == 'reg' || status == 'conf') ||
          (reg == 'true' || reg == '1') ||
          (conf == 'true' || conf == '1');
    }
    return false;
  }

  /// Check if user has balance (ftd or dep status)
  bool _checkBalanceStatus(dynamic postbackData) {
    if (postbackData is Map) {
      final status = postbackData['status']?.toString().toLowerCase();
      final ftd = postbackData['ftd']?.toString().toLowerCase();
      final dep = postbackData['dep']?.toString().toLowerCase();
      
      // Check if user has made first deposit or any deposit
      return (status == 'ftd' || status == 'dep') ||
          (ftd == 'true' || ftd == '1') ||
          (dep == 'true' || dep == '1');
    }
    return false;
  }

  /// Determine verification status based on registration and balance
  String _determineStatus(bool isRegistered, bool hasBalance) {
    if (!isRegistered) {
      return 'NOT_REGISTERED';
    }
    if (!hasBalance) {
      return 'VERIFIED_NO_DEPOSIT';
    }
    return 'VERIFIED_ACTIVE';
  }

  /// Get default postback URL for a platform
  String? getDefaultPostbackUrl(String platform) {
    if (platform == 'QUOTEX') {
      return 'https://example.com/postback.php';
    }
    return null;
  }
}

