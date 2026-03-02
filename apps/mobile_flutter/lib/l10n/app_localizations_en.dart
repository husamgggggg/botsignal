// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for English (`en`).
class AppLocalizationsEn extends AppLocalizations {
  AppLocalizationsEn([String locale = 'en']) : super(locale);

  @override
  String get appName => 'Signal App';

  @override
  String get selectPlatform => 'Select Platform';

  @override
  String get enterAccountId => 'Enter Account ID';

  @override
  String get accountIdHint => 'Your broker account ID';

  @override
  String get verify => 'Verify';

  @override
  String get verifiedActive => 'Account Verified';

  @override
  String get verifiedActiveMessage =>
      'Your account has been verified successfully! You can now access all signals.';

  @override
  String get verifiedNoDeposit => 'Deposit Required';

  @override
  String get verifiedNoDepositMessage =>
      'Your account is verified, but a deposit is required. Please deposit funds to access signals.';

  @override
  String get notUnderTeam => 'Register Required';

  @override
  String get notUnderTeamMessage =>
      'Account not found. Please register for free to get free signals.';

  @override
  String get openBroker => 'Open Broker';

  @override
  String get registerFree => 'Register for Free';

  @override
  String get signals => 'Signals';

  @override
  String get noSignals => 'No signals available';

  @override
  String get lockedSignals => 'Signals are locked. Please verify your account.';

  @override
  String get call => 'CALL';

  @override
  String get put => 'PUT';

  @override
  String get confidence => 'Confidence';

  @override
  String get expiry => 'Expiry';

  @override
  String get newsStatus => 'News Status';

  @override
  String get safe => 'Safe';

  @override
  String get warning => 'Warning';

  @override
  String get blocked => 'Blocked';

  @override
  String get riskCalculator => 'Risk Calculator';

  @override
  String get balance => 'Balance';

  @override
  String get riskPercent => 'Risk % per Trade';

  @override
  String get maxTradesPerDay => 'Max Trades per Day';

  @override
  String get maxConsecutiveLosses => 'Max Consecutive Losses';

  @override
  String get calculate => 'Calculate';

  @override
  String get suggestedStake => 'Suggested Stake';

  @override
  String get settings => 'Settings';

  @override
  String get language => 'Language';

  @override
  String get arabic => 'Arabic';

  @override
  String get english => 'English';

  @override
  String get changePlatform => 'Change Platform';

  @override
  String get logout => 'Logout';

  @override
  String get loading => 'Loading...';

  @override
  String get error => 'Error';

  @override
  String get retry => 'Retry';
}
