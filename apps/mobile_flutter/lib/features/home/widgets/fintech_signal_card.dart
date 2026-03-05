import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/services/timezone_service.dart';
import '../../../../core/providers/timezone_provider.dart';

class FintechSignalCard extends ConsumerStatefulWidget {
  final Map<String, dynamic> signal;
  final VoidCallback onOpenPlatform;

  const FintechSignalCard({
    super.key,
    required this.signal,
    required this.onOpenPlatform,
  });

  @override
  ConsumerState<FintechSignalCard> createState() => _FintechSignalCardState();
}

class _FintechSignalCardState extends ConsumerState<FintechSignalCard> {
  String? _localTime;

  String? _lastTimezone;

  @override
  void initState() {
    super.initState();
    _convertTime();
  }

  Future<void> _convertTime() async {
    final entryTime = widget.signal['entryTime'] as String? ?? '14:30 GMT';
    final localTime = await TimezoneService.convertGmtToLocal(entryTime);
    if (mounted) {
      setState(() {
        _localTime = localTime;
      });
    }
  }

  String _formatTimeRemaining(int seconds) {
    if (seconds < 0) return '00:00';
    final minutes = seconds ~/ 60;
    final secs = seconds % 60;
    return '${minutes.toString().padLeft(2, '0')}:${secs.toString().padLeft(2, '0')}';
  }

  String _getDirectionText(String direction) {
    if (direction == 'CALL' || direction == 'UP' || direction == 'BUY') {
      return 'صعود';
    }
    return 'هبوط';
  }

  Color _getDirectionColor(String direction) {
    if (direction == 'CALL' || direction == 'UP' || direction == 'BUY') {
      return const Color(0xFF1EC876);
    }
    return const Color(0xFFE04F4F);
  }

  // Get flag emoji for currency code
  String _getCurrencyFlag(String currency) {
    final currencyFlags = {
      'USD': '🇺🇸', // United States
      'EUR': '🇪🇺', // European Union
      'GBP': '🇬🇧', // United Kingdom
      'JPY': '🇯🇵', // Japan
      'AUD': '🇦🇺', // Australia
      'CAD': '🇨🇦', // Canada
      'CHF': '🇨🇭', // Switzerland
      'NZD': '🇳🇿', // New Zealand
      'CNY': '🇨🇳', // China
      'HKD': '🇭🇰', // Hong Kong
      'SGD': '🇸🇬', // Singapore
      'SEK': '🇸🇪', // Sweden
      'NOK': '🇳🇴', // Norway
      'DKK': '🇩🇰', // Denmark
      'PLN': '🇵🇱', // Poland
      'TRY': '🇹🇷', // Turkey
      'RUB': '🇷🇺', // Russia
      'ZAR': '🇿🇦', // South Africa
      'MXN': '🇲🇽', // Mexico
      'BRL': '🇧🇷', // Brazil
      'INR': '🇮🇳', // India
      'KRW': '🇰🇷', // South Korea
      'THB': '🇹🇭', // Thailand
      'IDR': '🇮🇩', // Indonesia
      'MYR': '🇲🇾', // Malaysia
      'PHP': '🇵🇭', // Philippines
      'BDT': '🇧🇩', // Bangladesh
      'NGN': '🇳🇬', // Nigeria
      'EGP': '🇪🇬', // Egypt
      'SAR': '🇸🇦', // Saudi Arabia
      'AED': '🇦🇪', // UAE
      'KWD': '🇰🇼', // Kuwait
      'QAR': '🇶🇦', // Qatar
      'BHD': '🇧🇭', // Bahrain
      'OMR': '🇴🇲', // Oman
      'JOD': '🇯🇴', // Jordan
      'LBP': '🇱🇧', // Lebanon
      'ILS': '🇮🇱', // Israel
      'PKR': '🇵🇰', // Pakistan
    };
    return currencyFlags[currency.toUpperCase()] ?? '🏳️';
  }

  // Extract currencies from pair and get flags
  List<String> _getPairFlags(String pair) {
    final parts = pair.split('/');
    if (parts.length == 2) {
      final baseCurrency = parts[0].trim();
      final quoteCurrency = parts[1].trim();
      // Remove (OTC) or other suffixes
      final cleanQuote = quoteCurrency.split(' ')[0];
      return [
        _getCurrencyFlag(cleanQuote), // Quote currency flag (right in RTL)
        _getCurrencyFlag(baseCurrency), // Base currency flag (left in RTL)
      ];
    }
    return ['🏳️', '🏳️'];
  }

  @override
  Widget build(BuildContext context) {
    // Watch timezone changes and update time if changed
    final currentTimezone = ref.watch(timezoneProvider);
    if (currentTimezone != _lastTimezone) {
      _lastTimezone = currentTimezone;
      WidgetsBinding.instance.addPostFrameCallback((_) {
        _convertTime();
      });
    }

    final asset = widget.signal['asset'] as String? ?? 'EUR/USD';
    final direction = widget.signal['direction'] as String? ?? 'CALL';
    final probability = widget.signal['probability'] as int? ?? 88;
    final expirySeconds = widget.signal['expirySeconds'] as int? ?? 105;
    final entryTimeGmt = widget.signal['entryTime'] as String? ?? '14:30 GMT';
    final entryTime = _localTime ?? entryTimeGmt; // Use converted time or fallback to GMT
    final contractDuration = widget.signal['contractDuration'] as String? ?? 'M5';
    final suggestedRiskPercent = widget.signal['suggestedRiskPercent'] as int? ?? 2;

    final directionColor = _getDirectionColor(direction);
    final directionText = _getDirectionText(direction);

    return Container(
      width: double.infinity,
      margin: const EdgeInsets.symmetric(horizontal: 16),
      decoration: BoxDecoration(
        color: const Color(0xFF151922),
        borderRadius: const BorderRadius.only(
          topRight: Radius.circular(16),
          bottomRight: Radius.circular(16),
          topLeft: Radius.circular(16),
          bottomLeft: Radius.circular(16),
        ),
        border: Border.all(
          color: const Color.fromRGBO(255, 255, 255, 0.05),
          width: 1,
        ),
      ),
      child: Stack(
        children: [
          // Right edge accent bar
          Positioned(
            right: 0,
            top: 0,
            bottom: 0,
            child: Container(
              width: 4,
              decoration: BoxDecoration(
                color: directionColor,
                borderRadius: const BorderRadius.only(
                  topRight: Radius.circular(16),
                  bottomRight: Radius.circular(16),
                ),
              ),
            ),
          ),
          
          // Content
          Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Top Row: Probability badge and Pair name
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    // Probability badge (right side in RTL)
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 10,
                        vertical: 6,
                      ),
                      decoration: BoxDecoration(
                        color: const Color(0xFF1EC876).withOpacity(0.15),
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Text(
                        '$probability% احتمالية',
                        style: const TextStyle(
                          color: Color(0xFF1EC876),
                          fontSize: 13,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                    
                    // Pair name with flags (left side in RTL)
                    Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        ..._getPairFlags(asset).map((flag) => Container(
                          margin: const EdgeInsets.symmetric(horizontal: 2),
                          width: 24,
                          height: 24,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            border: Border.all(
                              color: const Color.fromRGBO(255, 255, 255, 0.1),
                              width: 1,
                            ),
                          ),
                          child: Center(
                            child: Text(
                              flag,
                              style: const TextStyle(fontSize: 16),
                            ),
                          ),
                        )),
                        const SizedBox(width: 8),
                        Text(
                          asset,
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
                
                const SizedBox(height: 20),
                
                // Middle Grid: 3 columns
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    // Column 1 (Rightmost): Time
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'الوقت',
                            style: TextStyle(
                              color: Color(0xFF8A9099),
                              fontSize: 12,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            contractDuration,
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 15,
                            ),
                          ),
                        ],
                      ),
                    ),
                    
                    // Vertical divider
                    Container(
                      width: 1,
                      height: 40,
                      color: const Color.fromRGBO(255, 255, 255, 0.06),
                    ),
                    
                    // Column 2: Entry Time
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.center,
                        children: [
                          const Text(
                            'وقت الدخول',
                            style: TextStyle(
                              color: Color(0xFF8A9099),
                              fontSize: 12,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            entryTime,
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 15,
                            ),
                          ),
                        ],
                      ),
                    ),
                    
                    // Vertical divider
                    Container(
                      width: 1,
                      height: 40,
                      color: const Color.fromRGBO(255, 255, 255, 0.06),
                    ),
                    
                    // Column 3 (Leftmost): Direction
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.end,
                        children: [
                          const Text(
                            'التوصية',
                            style: TextStyle(
                              color: Color(0xFF8A9099),
                              fontSize: 12,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            directionText,
                            style: TextStyle(
                              color: directionColor,
                              fontSize: 15,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                
                const SizedBox(height: 20),
                
                // Bottom Row: Remaining time and Suggested risk
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    // Remaining time (right side in RTL)
                    Text(
                      'المتبقي: ${_formatTimeRemaining(expirySeconds)}',
                      style: const TextStyle(
                        color: Color(0xFFB0B7C3),
                        fontSize: 13,
                      ),
                    ),
                    
                    // Suggested risk (left side in RTL)
                    Text(
                      'حجم المقترح: $suggestedRiskPercent%',
                      style: const TextStyle(
                        color: Color(0xFFB0B7C3),
                        fontSize: 13,
                      ),
                    ),
                  ],
                ),
                
                const SizedBox(height: 16),
                
                // Action Button
                SizedBox(
                  width: double.infinity,
                    child: TextButton(
                    onPressed: widget.onOpenPlatform,
                    style: TextButton.styleFrom(
                      backgroundColor: const Color(0xFF2A3442),
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 10),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                    child: const Text(
                      'فتح المنصة',
                      style: TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

