// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Arabic (`ar`).
class AppLocalizationsAr extends AppLocalizations {
  AppLocalizationsAr([String locale = 'ar']) : super(locale);

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
