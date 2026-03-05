import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/localization/app_localizations.dart';
import '../../../../core/services/verify_service.dart';
import '../../../../core/providers/auth_provider.dart';
import '../../../../core/services/api_service.dart';

class AccountVerifyScreen extends ConsumerStatefulWidget {
  final String platform;

  const AccountVerifyScreen({super.key, required this.platform});

  @override
  ConsumerState<AccountVerifyScreen> createState() => _AccountVerifyScreenState();
}

class _AccountVerifyScreenState extends ConsumerState<AccountVerifyScreen> {
  final _accountIdController = TextEditingController();
  bool _verifying = false;

  @override
  void dispose() {
    _accountIdController.dispose();
    super.dispose();
  }

  Future<void> _verify() async {
    if (_accountIdController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter account ID')),
      );
      return;
    }

    setState(() {
      _verifying = true;
    });

    try {
      final apiService = ref.read(apiServiceProvider);
      final verifyService = VerifyService(apiService);
      final authNotifier = ref.read(authProvider.notifier);
      final deviceId = authNotifier.deviceId ?? '';

      final result = await verifyService.verifyAccount(
        platform: widget.platform,
        accountId: _accountIdController.text.trim(),
        deviceId: deviceId,
      );

      if (mounted) {
        context.push(
          '/verify-result?status=${result['status']}&messageAr=${Uri.encodeComponent(result['message_ar'])}&messageEn=${Uri.encodeComponent(result['message_en'])}&platform=${widget.platform}',
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _verifying = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context);

    return Scaffold(
      appBar: AppBar(
        title: Text(localizations.enterAccountId),
      ),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const SizedBox(height: 32),
            Text(
              localizations.accountIdHint,
              style: Theme.of(context).textTheme.bodyLarge,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 32),
            TextField(
              controller: _accountIdController,
              decoration: InputDecoration(
                labelText: localizations.accountIdHint,
                border: const OutlineInputBorder(),
              ),
              textInputAction: TextInputAction.done,
              onSubmitted: (_) => _verify(),
            ),
            const SizedBox(height: 32),
            ElevatedButton(
              onPressed: _verifying ? null : _verify,
              child: _verifying
                  ? const SizedBox(
                      height: 20,
                      width: 20,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : Text(localizations.verify),
            ),
          ],
        ),
      ),
    );
  }
}

