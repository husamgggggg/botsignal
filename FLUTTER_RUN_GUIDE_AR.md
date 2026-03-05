# دليل تشغيل تطبيق Flutter

## ✅ تم تفعيل Web و Windows

تم إنشاء ملفات Web و Windows بنجاح. يمكنك الآن تشغيل التطبيق على:

## طرق التشغيل

### 1. تشغيل على Chrome (Web) - الأسهل للاختبار

```bash
cd apps/mobile_flutter
flutter run -d chrome
```

أو ببساطة:
```bash
flutter run
# ثم اختر chrome من القائمة
```

### 2. تشغيل على Windows Desktop

```bash
flutter run -d windows
```

### 3. تشغيل على محاكي Android

إذا كان لديك Android Studio:
```bash
# افتح Android Studio وابدأ محاكي
flutter run -d android
```

### 4. عرض الأجهزة المتاحة

```bash
flutter devices
```

## ملاحظات مهمة

### 1. عنوان API للـ Web

عند تشغيل على Web، تأكد من تحديث عنوان API في `lib/core/config/app_config.dart`:

```dart
static String apiBaseUrl = 'http://localhost:3000';
```

**مهم:** على Web، `localhost` يعمل بشكل صحيح.

### 2. CORS

الخادم يدعم CORS بالفعل (في `main.ts`):
```typescript
app.enableCors({
  origin: true,
  credentials: true,
});
```

### 3. Firebase على Web

إذا أردت استخدام Firebase على Web، ستحتاج إلى إضافة ملف `web/index.html` مع Firebase SDK.

### 4. SharedPreferences على Web

`shared_preferences` يعمل على Web، لكن البيانات تُحفظ في LocalStorage.

## حل المشاكل

### إذا ظهرت أخطاء CORS

تأكد من أن الخادم يعمل على `http://localhost:3000` وأن CORS مفعل.

### إذا لم يعمل API

تحقق من:
1. الخادم يعمل: `curl http://localhost:3000/api/platforms`
2. عنوان API صحيح في `app_config.dart`
3. لا توجد أخطاء في Console (F12 في المتصفح)

### إذا ظهرت أخطاء في Firebase

Firebase اختياري. التطبيق سيعمل بدون Firebase، فقط الإشعارات الفورية ستكون معطلة.

## الخطوات التالية

1. **شغّل التطبيق:**
   ```bash
   flutter run -d chrome
   ```

2. **اختبر التدفق:**
   - اختر منصة
   - أدخل `TEST_ACTIVE_123` للتحقق
   - شاهد الإشارات

3. **للإنتاج:**
   - استخدم محاكي Android/iOS
   - أو build للتطبيق: `flutter build apk` أو `flutter build ios`

