import 'package:dio/dio.dart';
import 'api_service.dart';

class NewsService {
  final ApiService _apiService;

  NewsService(this._apiService);

  /// Fetch economic news/calendar from API
  /// Returns list of news events
  Future<List<dynamic>> getNews() async {
    try {
      final response = await _apiService.dio.get('/news');
      return response.data as List<dynamic>;
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        // If endpoint doesn't exist, return empty list
        return [];
      }
      throw Exception(e.response?.data?['message'] ?? 'Failed to fetch news');
    }
  }

  /// Fetch news from external API (example: ForexFactory, Investing.com, etc.)
  /// This is a placeholder - replace with actual API integration
  Future<List<dynamic>> getNewsFromExternalAPI() async {
    // TODO: Integrate with actual news API
    // Examples:
    // - ForexFactory API
    // - Investing.com API
    // - TradingEconomics API
    // - MyFxBook Economic Calendar
    
    // For now, return mock data
    return [];
  }
}

