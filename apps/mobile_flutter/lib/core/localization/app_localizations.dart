import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

abstract class AppLocalizations {
  static AppLocalizations of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations) ??
        AppLocalizationsEn();
  }

  static const LocalizationsDelegate<AppLocalizations> delegate =
      _AppLocalizationsDelegate();

  String get appName;
  String get selectPlatform;
  String get enterAccountId;
  String get accountIdHint;
  String get verify;
  String get verifiedActive;
  String get verifiedActiveMessage;
  String get verifiedNoDeposit;
  String get verifiedNoDepositMessage;
  String get notUnderTeam;
  String get notUnderTeamMessage;
  String get openBroker;
  String get registerFree;
  String get signals;
  String get noSignals;
  String get lockedSignals;
  String get call;
  String get put;
  String get confidence;
  String get expiry;
  String get newsStatus;
  String get safe;
  String get warning;
  String get blocked;
  String get riskCalculator;
  String get balance;
  String get riskPercent;
  String get maxTradesPerDay;
  String get maxConsecutiveLosses;
  String get calculate;
  String get suggestedStake;
  String get settings;
  String get language;
  String get arabic;
  String get english;
  String get changePlatform;
  String get logout;
  String get loading;
  String get error;
  String get retry;
}

class _AppLocalizationsDelegate
    extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  bool isSupported(Locale locale) => ['ar', 'en'].contains(locale.languageCode);

  @override
  Future<AppLocalizations> load(Locale locale) async {
    switch (locale.languageCode) {
      case 'ar':
        return AppLocalizationsAr();
      case 'en':
      default:
        return AppLocalizationsEn();
    }
  }

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}

// English implementation
class AppLocalizationsEn extends AppLocalizations {
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

// Arabic implementation
class AppLocalizationsAr extends AppLocalizations {
  @override
  String get appName => 'تطبيق الإشارات';
  @override
  String get selectPlatform => 'اختر المنصة';
  @override
  String get enterAccountId => 'أدخل معرف الحساب';
  @override
  String get accountIdHint => 'معرف حساب الوسيط الخاص بك';
  @override
  String get verify => 'تحقق';
  @override
  String get verifiedActive => 'تم التحقق من الحساب';
  @override
  String get verifiedActiveMessage =>
      'تم التحقق من حسابك بنجاح! يمكنك الآن الوصول إلى جميع الإشارات.';
  @override
  String get verifiedNoDeposit => 'إيداع مطلوب';
  @override
  String get verifiedNoDepositMessage =>
      'تم التحقق من حسابك، لكن يلزم إيداع. يرجى إيداع الأموال للوصول إلى الإشارات.';
  @override
  String get notUnderTeam => 'التسجيل مطلوب';
  @override
  String get notUnderTeamMessage =>
      'لم يتم العثور على الحساب. يرجى التسجيل مجاناً للحصول على إشارات مجانية.';
  @override
  String get openBroker => 'افتح الوسيط';
  @override
  String get registerFree => 'سجل مجاناً';
  @override
  String get signals => 'الإشارات';
  @override
  String get noSignals => 'لا توجد إشارات متاحة';
  @override
  String get lockedSignals => 'الإشارات مقفلة. يرجى التحقق من حسابك.';
  @override
  String get call => 'شراء';
  @override
  String get put => 'بيع';
  @override
  String get confidence => 'الثقة';
  @override
  String get expiry => 'الانتهاء';
  @override
  String get newsStatus => 'حالة الأخبار';
  @override
  String get safe => 'آمن';
  @override
  String get warning => 'تحذير';
  @override
  String get blocked => 'محظور';
  @override
  String get riskCalculator => 'حاسبة المخاطر';
  @override
  String get balance => 'الرصيد';
  @override
  String get riskPercent => 'نسبة المخاطرة لكل صفقة';
  @override
  String get maxTradesPerDay => 'الحد الأقصى للصفقات في اليوم';
  @override
  String get maxConsecutiveLosses => 'الحد الأقصى للخسائر المتتالية';
  @override
  String get calculate => 'احسب';
  @override
  String get suggestedStake => 'المبلغ المقترح';
  @override
  String get settings => 'الإعدادات';
  @override
  String get language => 'اللغة';
  @override
  String get arabic => 'العربية';
  @override
  String get english => 'الإنجليزية';
  @override
  String get changePlatform => 'تغيير المنصة';
  @override
  String get logout => 'تسجيل الخروج';
  @override
  String get loading => 'جاري التحميل...';
  @override
  String get error => 'خطأ';
  @override
  String get retry => 'إعادة المحاولة';
}

