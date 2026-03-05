import 'package:shared_preferences/shared_preferences.dart';

class TimezoneService {
  static const String _countryKey = 'selected_country';
  static const String _timezoneKey = 'selected_timezone';

  // Country to timezone mapping
  static final Map<String, String> _countryTimezones = {
    'Turkey': 'Europe/Istanbul', // UTC+3
    'Saudi Arabia': 'Asia/Riyadh', // UTC+3
    'UAE': 'Asia/Dubai', // UTC+4
    'Egypt': 'Africa/Cairo', // UTC+2
    'Jordan': 'Asia/Amman', // UTC+2
    'Lebanon': 'Asia/Beirut', // UTC+2
    'Kuwait': 'Asia/Kuwait', // UTC+3
    'Qatar': 'Asia/Qatar', // UTC+3
    'Bahrain': 'Asia/Bahrain', // UTC+3
    'Oman': 'Asia/Muscat', // UTC+4
    'Yemen': 'Asia/Aden', // UTC+3
    'Iraq': 'Asia/Baghdad', // UTC+3
    'Syria': 'Asia/Damascus', // UTC+2
    'Palestine': 'Asia/Gaza', // UTC+2
    'Morocco': 'Africa/Casablanca', // UTC+1
    'Tunisia': 'Africa/Tunis', // UTC+1
    'Algeria': 'Africa/Algiers', // UTC+1
    'Libya': 'Africa/Tripoli', // UTC+2
    'Sudan': 'Africa/Khartoum', // UTC+2
    'Default': 'UTC', // GMT/UTC
  };

  // Get list of available countries
  static List<String> getAvailableCountries() {
    return _countryTimezones.keys.toList();
  }

  // Get timezone for a country
  static String? getTimezoneForCountry(String country) {
    return _countryTimezones[country];
  }

  // Save selected country
  static Future<void> saveCountry(String country) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_countryKey, country);
    final timezone = _countryTimezones[country];
    if (timezone != null && country != 'Default') {
      await prefs.setString(_timezoneKey, timezone);
    } else if (country == 'Default') {
      // Clear timezone to use device timezone
      await prefs.remove(_timezoneKey);
    }
  }

  // Get selected country
  static Future<String?> getSelectedCountry() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_countryKey);
  }

  // Get selected timezone
  static Future<String?> getSelectedTimezone() async {
    final prefs = await SharedPreferences.getInstance();
    final timezone = prefs.getString(_timezoneKey);
    // If no timezone saved or 'Default', return null to use device timezone
    if (timezone == null || timezone == 'UTC' || timezone == 'Default') {
      return null; // Will use device timezone
    }
    return timezone;
  }

  // Convert GMT time to local time
  // Input format: "14:30 GMT" or "14:30"
  // Output format: "17:30" (for Turkey UTC+3) or device timezone
  static Future<String> convertGmtToLocal(String gmtTime) async {
    try {
      // Extract time from "14:30 GMT" or "14:30"
      final timeMatch = RegExp(r'(\d{1,2}):(\d{2})').firstMatch(gmtTime);
      if (timeMatch == null) return gmtTime;

      final hour = int.parse(timeMatch.group(1)!);
      final minute = int.parse(timeMatch.group(2)!);

      // Get timezone offset
      final timezone = await getSelectedTimezone();
      final offset = _getTimezoneOffset(timezone); // Will use device timezone if null

      // Calculate local time
      final localHour = (hour + offset) % 24;
      final localMinute = minute;

      // Format time
      return '${localHour.toString().padLeft(2, '0')}:${localMinute.toString().padLeft(2, '0')}';
    } catch (e) {
      return gmtTime;
    }
  }

  // Get device timezone offset in hours from UTC
  static int getDeviceTimezoneOffset() {
    final now = DateTime.now();
    final offset = now.timeZoneOffset;
    // Convert Duration to hours
    return offset.inHours;
  }

  // Get timezone offset in hours from UTC
  static int _getTimezoneOffset(String? timezone) {
    // If timezone is null or 'Default', use device timezone
    if (timezone == null || timezone == 'UTC' || timezone == 'Default') {
      return getDeviceTimezoneOffset();
    }

    // This is a simplified version - in production, use timezone package
    final offsets = {
      'Europe/Istanbul': 3, // Turkey
      'Asia/Riyadh': 3, // Saudi Arabia
      'Asia/Dubai': 4, // UAE
      'Africa/Cairo': 2, // Egypt
      'Asia/Amman': 2, // Jordan
      'Asia/Beirut': 2, // Lebanon
      'Asia/Kuwait': 3, // Kuwait
      'Asia/Qatar': 3, // Qatar
      'Asia/Bahrain': 3, // Bahrain
      'Asia/Muscat': 4, // Oman
      'Asia/Aden': 3, // Yemen
      'Asia/Baghdad': 3, // Iraq
      'Asia/Damascus': 2, // Syria
      'Asia/Gaza': 2, // Palestine
      'Africa/Casablanca': 1, // Morocco
      'Africa/Tunis': 1, // Tunisia
      'Africa/Algiers': 1, // Algeria
      'Africa/Tripoli': 2, // Libya
      'Africa/Khartoum': 2, // Sudan
    };

    return offsets[timezone] ?? getDeviceTimezoneOffset();
  }

  // Format time with country name
  static Future<String> formatTimeWithCountry(String gmtTime) async {
    final country = await getSelectedCountry();
    final localTime = await convertGmtToLocal(gmtTime);
    
    if (country == null || country == 'Default') {
      // Use device timezone name or offset
      final offset = getDeviceTimezoneOffset();
      final offsetStr = offset >= 0 ? '+$offset' : '$offset';
      return '$localTime (UTC$offsetStr)';
    }

    return '$localTime ($country)';
  }
}

