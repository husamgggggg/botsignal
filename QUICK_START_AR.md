# البدء السريع - تشغيل التطبيق

## ✅ تم إعداد كل شيء!

### الخادم (Backend)
- ✅ يعمل على: http://localhost:3000
- ✅ Swagger: http://localhost:3000/docs

### تطبيق Flutter
- ✅ المكتبات مثبتة
- ✅ Web و Windows مفعلان

## 🚀 تشغيل التطبيق

### الطريقة 1: على Chrome (Web) - الأسهل

```bash
cd apps/mobile_flutter
flutter run -d chrome
```

### الطريقة 2: على Windows Desktop

```bash
cd apps/mobile_flutter
flutter run -d windows
```

### الطريقة 3: عرض جميع الأجهزة

```bash
flutter devices
```

ثم اختر الجهاز المطلوب.

## 📱 اختبار التطبيق

بعد تشغيل التطبيق:

1. **اختر منصة** (Quotex أو Pocket Option)
2. **أدخل معرف حساب تجريبي:**
   - `TEST_ACTIVE_123` → وصول كامل
   - `TEST_NO_DEPOSIT_456` → إيداع مطلوب
3. **شاهد النتيجة** واختبر التدفق

## ⚙️ إعدادات مهمة

### عنوان API

التطبيق يستخدم `http://localhost:3000` افتراضياً. إذا كان الخادم على عنوان آخر، حدّث `lib/core/config/app_config.dart`.

### CORS

الخادم يدعم CORS بالفعل، لا حاجة لتعديلات إضافية.

## 🔧 حل المشاكل

### التطبيق لا يتصل بالخادم

1. تأكد من أن الخادم يعمل: `curl http://localhost:3000/api/platforms`
2. افتح Developer Tools (F12) في المتصفح وابحث عن أخطاء
3. تحقق من Console للأخطاء

### أخطاء Firebase

Firebase اختياري. التطبيق سيعمل بدون Firebase، فقط الإشعارات الفورية ستكون معطلة.

## 📚 الملفات المفيدة

- `FLUTTER_RUN_GUIDE_AR.md` - دليل تفصيلي لتشغيل Flutter
- `SUCCESS_AR.md` - دليل الخادم
- `QUICK_REFERENCE_AR.md` - مرجع سريع

## 🎉 جاهز!

شغّل `flutter run -d chrome` وابدأ الاختبار!

