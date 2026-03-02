import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/timezone_service.dart';

final timezoneProvider = StateNotifierProvider<TimezoneNotifier, String?>((ref) {
  return TimezoneNotifier();
});

class TimezoneNotifier extends StateNotifier<String?> {
  TimezoneNotifier() : super(null) {
    _loadCountry();
  }

  Future<void> _loadCountry() async {
    final country = await TimezoneService.getSelectedCountry();
    state = country;
  }

  Future<void> setCountry(String country) async {
    await TimezoneService.saveCountry(country);
    state = country;
  }
  
  // Public method to load country (for external access)
  Future<void> loadCountry() async {
    await _loadCountry();
  }
}

