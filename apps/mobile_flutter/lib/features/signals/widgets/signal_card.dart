import 'package:flutter/material.dart';
import '../../../../core/localization/app_localizations.dart';
import '../../../../core/theme/app_theme.dart';

class SignalCard extends StatelessWidget {
  final Map<String, dynamic> signal;
  final VoidCallback onTap;

  const SignalCard({
    super.key,
    required this.signal,
    required this.onTap,
  });

  String _formatExpiry(int seconds) {
    if (seconds < 60) return '${seconds}s';
    if (seconds < 3600) return '${seconds ~/ 60}m';
    return '${seconds ~/ 3600}h';
  }

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context);
    final isArabic = Localizations.localeOf(context).languageCode == 'ar';
    final direction = signal['direction'] as String;
    final isCall = direction == 'CALL';

    Color directionColor = isCall ? AppTheme.neonGreen : Colors.red;
    String directionText = isCall ? localizations.call : localizations.put;

    Color newsColor = AppTheme.textGray;
    String newsText = localizations.safe;
    if (signal['newsStatus'] == 'WARNING') {
      newsColor = Colors.orange;
      newsText = localizations.warning;
    } else if (signal['newsStatus'] == 'BLOCKED') {
      newsColor = Colors.red;
      newsText = localizations.blocked;
    }

    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    signal['asset'] as String? ?? 'N/A',
                    style: Theme.of(context).textTheme.headlineMedium,
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: directionColor.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: directionColor),
                    ),
                    child: Text(
                      directionText,
                      style: TextStyle(
                        color: directionColor,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Icon(Icons.timer, size: 16, color: AppTheme.textGray),
                  const SizedBox(width: 4),
                  Text(
                    '${localizations.expiry}: ${_formatExpiry(signal['expirySeconds'] as int? ?? 0)}',
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                  const SizedBox(width: 16),
                  Icon(Icons.trending_up, size: 16, color: AppTheme.textGray),
                  const SizedBox(width: 4),
                  Text(
                    '${localizations.confidence}: ${signal['confidence']}%',
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  Icon(Icons.info_outline, size: 16, color: newsColor),
                  const SizedBox(width: 4),
                  Text(
                    '${localizations.newsStatus}: $newsText',
                    style: TextStyle(color: newsColor),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

