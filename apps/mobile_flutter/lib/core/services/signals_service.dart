import 'package:dio/dio.dart';
import 'api_service.dart';

class SignalsService {
  final ApiService _apiService;

  SignalsService(this._apiService);

  Future<List<dynamic>> getSignals({String? platform}) async {
    try {
      final queryParams = platform != null ? {'platform': platform} : null;
      final response = await _apiService.dio.get(
        '/signals',
        queryParameters: queryParams,
      );
      return response.data as List<dynamic>;
    } on DioException catch (e) {
      if (e.response?.statusCode == 403) {
        throw Exception('Account verification required');
      }
      throw Exception(e.response?.data?['message'] ?? 'Failed to fetch signals');
    }
  }
}

