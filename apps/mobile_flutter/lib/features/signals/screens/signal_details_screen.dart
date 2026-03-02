import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../../../core/localization/app_localizations.dart';
import '../../../../core/theme/app_theme.dart';

class SignalDetailsScreen extends StatelessWidget {
  final String signalId;

  const SignalDetailsScreen({super.key, required this.signalId});

  Future<void> _openBroker() async {
    // This would load from platform service
    // For now, placeholder
    const url = 'https://broker.quotex.io';
    final uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    }
  }

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context);

    // In a real app, you'd fetch signal details by ID
    // For now, showing placeholder

    return Scaffold(
      appBar: AppBar(
        title: Text(localizations.signals),
      ),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'Signal Details',
              style: Theme.of(context).textTheme.displaySmall,
            ),
            const SizedBox(height: 24),
            Text('Signal ID: $signalId'),
            const Spacer(),
            ElevatedButton(
              onPressed: _openBroker,
              child: Text(localizations.openBroker),
            ),
          ],
        ),
      ),
    );
  }
}

