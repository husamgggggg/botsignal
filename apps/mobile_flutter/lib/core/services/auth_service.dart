import 'package:dio/dio.dart';
import 'api_service.dart';
import 'package:shared_preferences/shared_preferences.dart';

class AuthService {
  final ApiService _apiService;
  final SharedPreferences _prefs;

  AuthService(this._apiService, this._prefs);

  Future<Map<String, dynamic>> registerDevice(String deviceId, {String? fcmToken}) async {
    try {
      final response = await _apiService.dio.post(
        '/auth/register',
        data: {
          'deviceId': deviceId,
          if (fcmToken != null) 'fcmToken': fcmToken,
        },
      );
      return response.data;
    } on DioException catch (e) {
      throw Exception(e.response?.data?['message'] ?? 'Failed to register device');
    }
  }

  Future<void> updateFcmToken(String token, String fcmToken) async {
    try {
      _apiService.setAuthToken(token);
      await _apiService.dio.post(
        '/auth/fcm-token',
        data: {'fcmToken': fcmToken},
      );
    } on DioException catch (e) {
      throw Exception(e.response?.data?['message'] ?? 'Failed to update FCM token');
    }
  }

  Future<void> saveToken(String token) async {
    await _prefs.setString('auth_token', token);
  }

  String? getToken() {
    return _prefs.getString('auth_token');
  }

  Future<void> clearToken() async {
    await _prefs.remove('auth_token');
    _apiService.clearAuthToken();
  }

  Future<void> savePlatform(String platform) async {
    await _prefs.setString('selected_platform', platform);
  }

  String? getPlatform() {
    return _prefs.getString('selected_platform');
  }
}

