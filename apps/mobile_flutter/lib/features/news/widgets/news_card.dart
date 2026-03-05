import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/services/timezone_service.dart';
import '../../../../core/providers/timezone_provider.dart';

class NewsCard extends ConsumerStatefulWidget {
  final Map<String, dynamic> news;

  const NewsCard({
    super.key,
    required this.news,
  });

  @override
  ConsumerState<NewsCard> createState() => _NewsCardState();
}

class _NewsCardState extends ConsumerState<NewsCard> {
  String? _localTime;

  String? _lastTimezone;

  @override
  void initState() {
    super.initState();
    _convertTime();
  }

  Future<void> _convertTime() async {
    final timeGmt = widget.news['time'] as String? ?? 'N/A';
    if (timeGmt != 'N/A') {
      final localTime = await TimezoneService.convertGmtToLocal(timeGmt);
      if (mounted) {
        setState(() {
          _localTime = localTime;
        });
      }
    }
  }

  Color _getImpactColor(int impact) {
    switch (impact) {
      case 3:
        return const Color(0xFFE04F4F); // Red for high impact
      case 2:
        return const Color(0xFFFFA500); // Orange for medium impact
      case 1:
        return const Color(0xFF1EC876); // Green for low impact
      default:
        return const Color(0xFF8A9099); // Gray for no impact
    }
  }

  Widget _buildStars(int impact) {
    return Row(
      children: List.generate(3, (index) {
        return Icon(
          index < impact ? Icons.star : Icons.star_border,
          size: 16,
          color: index < impact ? _getImpactColor(impact) : const Color(0xFF8A9099),
        );
      }),
    );
  }

  Color _getActualColor(dynamic actual, dynamic forecast) {
    if (actual == null) return const Color(0xFF8A9099); // Not released yet
    
    // Compare actual with forecast
    if (actual is String && forecast is String) {
      // Try to parse as numbers
      try {
        final actualNum = double.parse(actual.replaceAll('%', '').replaceAll('K', '000'));
        final forecastNum = double.parse(forecast.replaceAll('%', '').replaceAll('K', '000'));
        
        if (actualNum > forecastNum) {
          return const Color(0xFF1EC876); // Green (better than expected)
        } else if (actualNum < forecastNum) {
          return const Color(0xFFE04F4F); // Red (worse than expected)
        } else {
          return const Color(0xFFB0B7C3); // Gray (as expected)
        }
      } catch (e) {
        return const Color(0xFFB0B7C3);
      }
    }
    
    return const Color(0xFFB0B7C3);
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

    final name = widget.news['nameAr'] as String? ?? widget.news['name'] as String? ?? 'خبر اقتصادي';
    final impact = widget.news['impact'] as int? ?? 1;
    final timeGmt = widget.news['time'] as String? ?? 'N/A';
    final time = _localTime ?? timeGmt; // Use converted time or fallback to GMT
    final previous = widget.news['previous'] as String? ?? 'N/A';
    final forecast = widget.news['forecast'] as String? ?? 'N/A';
    final actual = widget.news['actual'];
    final currency = widget.news['currency'] as String? ?? '';

    final impactColor = _getImpactColor(impact);
    final actualColor = _getActualColor(actual, forecast);

    return Container(
      width: double.infinity,
      margin: const EdgeInsets.symmetric(horizontal: 16),
      decoration: BoxDecoration(
        color: const Color(0xFF151922),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: const Color.fromRGBO(255, 255, 255, 0.05),
          width: 1,
        ),
      ),
      child: Stack(
        children: [
          // Right edge accent bar (based on impact)
          Positioned(
            right: 0,
            top: 0,
            bottom: 0,
            child: Container(
              width: 4,
              decoration: BoxDecoration(
                color: impactColor,
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
                // Top Row: News name and Impact stars
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    // Impact stars (right side in RTL)
                    _buildStars(impact),
                    
                    // News name (left side in RTL)
                    Expanded(
                      child: Text(
                        name,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                        textAlign: TextAlign.end,
                      ),
                    ),
                  ],
                ),
                
                const SizedBox(height: 20),
                
                // Time row
                Row(
                  children: [
                    const Icon(
                      Icons.access_time,
                      size: 16,
                      color: Color(0xFF8A9099),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      time,
                      style: const TextStyle(
                        color: Color(0xFFB0B7C3),
                        fontSize: 13,
                      ),
                    ),
                    if (currency.isNotEmpty) ...[
                      const SizedBox(width: 16),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: const Color(0xFF2A3442),
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Text(
                          currency,
                          style: const TextStyle(
                            color: Color(0xFFB0B7C3),
                            fontSize: 12,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ),
                    ],
                  ],
                ),
                
                const SizedBox(height: 16),
                
                // Data Grid: Previous, Forecast, Actual
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    // Column 1 (Rightmost): Previous
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'السابق',
                            style: TextStyle(
                              color: Color(0xFF8A9099),
                              fontSize: 12,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            previous,
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 14,
                              fontWeight: FontWeight.w500,
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
                    
                    // Column 2: Forecast
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.center,
                        children: [
                          const Text(
                            'التقدير',
                            style: TextStyle(
                              color: Color(0xFF8A9099),
                              fontSize: 12,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            forecast,
                            style: const TextStyle(
                              color: Color(0xFFB0B7C3),
                              fontSize: 14,
                              fontWeight: FontWeight.w500,
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
                    
                    // Column 3 (Leftmost): Actual
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.end,
                        children: [
                          const Text(
                            'الفعلي',
                            style: TextStyle(
                              color: Color(0xFF8A9099),
                              fontSize: 12,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            actual?.toString() ?? 'لم يصدر',
                            style: TextStyle(
                              color: actualColor,
                              fontSize: 14,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

