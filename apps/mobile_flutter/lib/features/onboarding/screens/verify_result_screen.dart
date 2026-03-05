import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../../../core/localization/app_localizations.dart';
import '../../../../core/services/platforms_service.dart';
import '../../../../core/providers/auth_provider.dart';

class VerifyResultScreen extends ConsumerStatefulWidget {
  final String status;
  final String messageAr;
  final String messageEn;
  final String platform;

  const VerifyResultScreen({
    super.key,
    required this.status,
    required this.messageAr,
    required this.messageEn,
    required this.platform,
  });

  @override
  ConsumerState<VerifyResultScreen> createState() => _VerifyResultScreenState();
}

class _VerifyResultScreenState extends ConsumerState<VerifyResultScreen> {
  @override
  void initState() {
    super.initState();
    // Auto-navigate to home if account is verified and active
    if (widget.status == 'VERIFIED_ACTIVE') {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted) {
          context.go('/home');
        }
      });
    }
  }

  Future<void> _openBroker(WidgetRef ref, String? deepLink, String? affiliateUrl) async {
    // Try deep link first
    if (deepLink != null && deepLink.isNotEmpty) {
      final uri = Uri.parse(deepLink);
      if (await canLaunchUrl(uri)) {
        await launchUrl(uri);
        return;
      }
    }

    // Fallback to affiliate URL
    if (affiliateUrl != null && affiliateUrl.isNotEmpty) {
      final uri = Uri.parse(affiliateUrl);
      if (await canLaunchUrl(uri)) {
        await launchUrl(uri, mode: LaunchMode.externalApplication);
        return;
      }
    }

    // If no URL provided, get default affiliate URL
    final apiService = ref.read(apiServiceProvider);
    final platformsService = PlatformsService(apiService);
    final defaultUrl = platformsService.getAffiliateUrl(widget.platform);
    if (defaultUrl.isNotEmpty) {
      final uri = Uri.parse(defaultUrl);
      if (await canLaunchUrl(uri)) {
        await launchUrl(uri, mode: LaunchMode.externalApplication);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context);
    final isArabic = Localizations.localeOf(context).languageCode == 'ar';
    final message = isArabic ? widget.messageAr : widget.messageEn;

    Color statusColor;
    IconData statusIcon;
    String title;

    if (widget.status == 'VERIFIED_ACTIVE') {
      statusColor = Colors.green;
      statusIcon = Icons.check_circle;
      title = localizations.verifiedActive;
    } else if (widget.status == 'VERIFIED_NO_DEPOSIT') {
      statusColor = Colors.orange;
      statusIcon = Icons.warning;
      title = localizations.verifiedNoDeposit;
    } else {
      statusColor = Colors.red;
      statusIcon = Icons.error;
      title = localizations.notUnderTeam;
    }

    return Scaffold(
      appBar: AppBar(
        title: Text(title),
      ),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Icon(
              statusIcon,
              size: 80,
              color: statusColor,
            ),
            const SizedBox(height: 24),
            Text(
              title,
              style: Theme.of(context).textTheme.displaySmall,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            Text(
              message,
              style: Theme.of(context).textTheme.bodyLarge,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 48),
            if (widget.status == 'VERIFIED_ACTIVE')
              // Show loading indicator while navigating
              const Center(
                child: CircularProgressIndicator(),
              )
            else if (widget.status == 'VERIFIED_NO_DEPOSIT')
              ElevatedButton(
                onPressed: () async {
                  // Open broker affiliate link
                  await _openBroker(ref, null, null);
                },
                child: Text(localizations.openBroker),
              )
            else
              ElevatedButton(
                onPressed: () async {
                  // Open affiliate registration link
                  await _openBroker(ref, null, null);
                },
                child: Text(localizations.registerFree),
              ),
          ],
        ),
      ),
    );
  }
}

