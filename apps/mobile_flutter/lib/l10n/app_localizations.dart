import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:intl/intl.dart' as intl;

import 'app_localizations_ar.dart';
import 'app_localizations_en.dart';

// ignore_for_file: type=lint

/// Callers can lookup localized strings with an instance of AppLocalizations
/// returned by `AppLocalizations.of(context)`.
///
/// Applications need to include `AppLocalizations.delegate()` in their app's
/// `localizationDelegates` list, and the locales they support in the app's
/// `supportedLocales` list. For example:
///
/// ```dart
/// import 'l10n/app_localizations.dart';
///
/// return MaterialApp(
///   localizationsDelegates: AppLocalizations.localizationsDelegates,
///   supportedLocales: AppLocalizations.supportedLocales,
///   home: MyApplicationHome(),
/// );
/// ```
///
/// ## Update pubspec.yaml
///
/// Please make sure to update your pubspec.yaml to include the following
/// packages:
///
/// ```yaml
/// dependencies:
///   # Internationalization support.
///   flutter_localizations:
///     sdk: flutter
///   intl: any # Use the pinned version from flutter_localizations
///
///   # Rest of dependencies
/// ```
///
/// ## iOS Applications
///
/// iOS applications define key application metadata, including supported
/// locales, in an Info.plist file that is built into the application bundle.
/// To configure the locales supported by your app, you’ll need to edit this
/// file.
///
/// First, open your project’s ios/Runner.xcworkspace Xcode workspace file.
/// Then, in the Project Navigator, open the Info.plist file under the Runner
/// project’s Runner folder.
///
/// Next, select the Information Property List item, select Add Item from the
/// Editor menu, then select Localizations from the pop-up menu.
///
/// Select and expand the newly-created Localizations item then, for each
/// locale your application supports, add a new item and select the locale
/// you wish to add from the pop-up menu in the Value field. This list should
/// be consistent with the languages listed in the AppLocalizations.supportedLocales
/// property.
abstract class AppLocalizations {
  AppLocalizations(String locale)
      : localeName = intl.Intl.canonicalizedLocale(locale.toString());

  final String localeName;

  static AppLocalizations? of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations);
  }

  static const LocalizationsDelegate<AppLocalizations> delegate =
      _AppLocalizationsDelegate();

  /// A list of this localizations delegate along with the default localizations
  /// delegates.
  ///
  /// Returns a list of localizations delegates containing this delegate along with
  /// GlobalMaterialLocalizations.delegate, GlobalCupertinoLocalizations.delegate,
  /// and GlobalWidgetsLocalizations.delegate.
  ///
  /// Additional delegates can be added by appending to this list in
  /// MaterialApp. This list does not have to be used at all if a custom list
  /// of delegates is preferred or required.
  static const List<LocalizationsDelegate<dynamic>> localizationsDelegates =
      <LocalizationsDelegate<dynamic>>[
    delegate,
    GlobalMaterialLocalizations.delegate,
    GlobalCupertinoLocalizations.delegate,
    GlobalWidgetsLocalizations.delegate,
  ];

  /// A list of this localizations delegate's supported locales.
  static const List<Locale> supportedLocales = <Locale>[
    Locale('ar'),
    Locale('en')
  ];

  /// No description provided for @appName.
  ///
  /// In en, this message translates to:
  /// **'Signal App'**
  String get appName;

  /// No description provided for @selectPlatform.
  ///
  /// In en, this message translates to:
  /// **'Select Platform'**
  String get selectPlatform;

  /// No description provided for @enterAccountId.
  ///
  /// In en, this message translates to:
  /// **'Enter Account ID'**
  String get enterAccountId;

  /// No description provided for @accountIdHint.
  ///
  /// In en, this message translates to:
  /// **'Your broker account ID'**
  String get accountIdHint;

  /// No description provided for @verify.
  ///
  /// In en, this message translates to:
  /// **'Verify'**
  String get verify;

  /// No description provided for @verifiedActive.
  ///
  /// In en, this message translates to:
  /// **'Account Verified'**
  String get verifiedActive;

  /// No description provided for @verifiedActiveMessage.
  ///
  /// In en, this message translates to:
  /// **'Your account has been verified successfully! You can now access all signals.'**
  String get verifiedActiveMessage;

  /// No description provided for @verifiedNoDeposit.
  ///
  /// In en, this message translates to:
  /// **'Deposit Required'**
  String get verifiedNoDeposit;

  /// No description provided for @verifiedNoDepositMessage.
  ///
  /// In en, this message translates to:
  /// **'Your account is verified, but a deposit is required. Please deposit funds to access signals.'**
  String get verifiedNoDepositMessage;

  /// No description provided for @notUnderTeam.
  ///
  /// In en, this message translates to:
  /// **'Register Required'**
  String get notUnderTeam;

  /// No description provided for @notUnderTeamMessage.
  ///
  /// In en, this message translates to:
  /// **'Account not found. Please register for free to get free signals.'**
  String get notUnderTeamMessage;

  /// No description provided for @openBroker.
  ///
  /// In en, this message translates to:
  /// **'Open Broker'**
  String get openBroker;

  /// No description provided for @registerFree.
  ///
  /// In en, this message translates to:
  /// **'Register for Free'**
  String get registerFree;

  /// No description provided for @signals.
  ///
  /// In en, this message translates to:
  /// **'Signals'**
  String get signals;

  /// No description provided for @noSignals.
  ///
  /// In en, this message translates to:
  /// **'No signals available'**
  String get noSignals;

  /// No description provided for @lockedSignals.
  ///
  /// In en, this message translates to:
  /// **'Signals are locked. Please verify your account.'**
  String get lockedSignals;

  /// No description provided for @call.
  ///
  /// In en, this message translates to:
  /// **'CALL'**
  String get call;

  /// No description provided for @put.
  ///
  /// In en, this message translates to:
  /// **'PUT'**
  String get put;

  /// No description provided for @confidence.
  ///
  /// In en, this message translates to:
  /// **'Confidence'**
  String get confidence;

  /// No description provided for @expiry.
  ///
  /// In en, this message translates to:
  /// **'Expiry'**
  String get expiry;

  /// No description provided for @newsStatus.
  ///
  /// In en, this message translates to:
  /// **'News Status'**
  String get newsStatus;

  /// No description provided for @safe.
  ///
  /// In en, this message translates to:
  /// **'Safe'**
  String get safe;

  /// No description provided for @warning.
  ///
  /// In en, this message translates to:
  /// **'Warning'**
  String get warning;

  /// No description provided for @blocked.
  ///
  /// In en, this message translates to:
  /// **'Blocked'**
  String get blocked;

  /// No description provided for @riskCalculator.
  ///
  /// In en, this message translates to:
  /// **'Risk Calculator'**
  String get riskCalculator;

  /// No description provided for @balance.
  ///
  /// In en, this message translates to:
  /// **'Balance'**
  String get balance;

  /// No description provided for @riskPercent.
  ///
  /// In en, this message translates to:
  /// **'Risk % per Trade'**
  String get riskPercent;

  /// No description provided for @maxTradesPerDay.
  ///
  /// In en, this message translates to:
  /// **'Max Trades per Day'**
  String get maxTradesPerDay;

  /// No description provided for @maxConsecutiveLosses.
  ///
  /// In en, this message translates to:
  /// **'Max Consecutive Losses'**
  String get maxConsecutiveLosses;

  /// No description provided for @calculate.
  ///
  /// In en, this message translates to:
  /// **'Calculate'**
  String get calculate;

  /// No description provided for @suggestedStake.
  ///
  /// In en, this message translates to:
  /// **'Suggested Stake'**
  String get suggestedStake;

  /// No description provided for @settings.
  ///
  /// In en, this message translates to:
  /// **'Settings'**
  String get settings;

  /// No description provided for @language.
  ///
  /// In en, this message translates to:
  /// **'Language'**
  String get language;

  /// No description provided for @arabic.
  ///
  /// In en, this message translates to:
  /// **'Arabic'**
  String get arabic;

  /// No description provided for @english.
  ///
  /// In en, this message translates to:
  /// **'English'**
  String get english;

  /// No description provided for @changePlatform.
  ///
  /// In en, this message translates to:
  /// **'Change Platform'**
  String get changePlatform;

  /// No description provided for @logout.
  ///
  /// In en, this message translates to:
  /// **'Logout'**
  String get logout;

  /// No description provided for @loading.
  ///
  /// In en, this message translates to:
  /// **'Loading...'**
  String get loading;

  /// No description provided for @error.
  ///
  /// In en, this message translates to:
  /// **'Error'**
  String get error;

  /// No description provided for @retry.
  ///
  /// In en, this message translates to:
  /// **'Retry'**
  String get retry;
}

class _AppLocalizationsDelegate
    extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  Future<AppLocalizations> load(Locale locale) {
    return SynchronousFuture<AppLocalizations>(lookupAppLocalizations(locale));
  }

  @override
  bool isSupported(Locale locale) =>
      <String>['ar', 'en'].contains(locale.languageCode);

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}

AppLocalizations lookupAppLocalizations(Locale locale) {
  // Lookup logic when only language code is specified.
  switch (locale.languageCode) {
    case 'ar':
      return AppLocalizationsAr();
    case 'en':
      return AppLocalizationsEn();
  }

  throw FlutterError(
      'AppLocalizations.delegate failed to load unsupported locale "$locale". This is likely '
      'an issue with the localizations generation tool. Please file an issue '
      'on GitHub with a reproducible sample app and the gen-l10n configuration '
      'that was used.');
}
