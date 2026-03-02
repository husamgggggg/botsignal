# دليل إعداد الموقع الإلكتروني

هذا الدليل يشرح كيفية تشغيل التطبيق كموقع ويب.

## المتطلبات الأساسية

- Flutter SDK 3.0+
- Node.js 18+ (لخادم API)
- متصفح ويب حديث (Chrome, Firefox, Edge, Safari)

## الخطوة 1: تشغيل خادم API

قبل تشغيل الموقع، تأكد من أن خادم API يعمل:

```bash
cd apps/api_nest
npm install
npm run start:dev
```

الخادم سيعمل على: `http://localhost:3000`

## الخطوة 2: تشغيل الموقع في وضع التطوير

```bash
cd apps/mobile_flutter
flutter pub get
flutter run -d chrome
```

أو لتشغيله على متصفح معين:

```bash
# Chrome
flutter run -d chrome

# Edge
flutter run -d edge

# Firefox
flutter run -d web-server --web-port=8080
```

## الخطوة 3: بناء الموقع للإنتاج

لإنشاء نسخة إنتاج من الموقع:

```bash
cd apps/mobile_flutter
flutter build web
```

الملفات المبنية ستكون في: `build/web/`

## الخطوة 4: نشر الموقع

### خيار 1: استخدام Flutter Web Server

```bash
cd build/web
python -m http.server 8080
```

ثم افتح: `http://localhost:8080`

### خيار 2: استخدام Node.js serve

```bash
npm install -g serve
cd build/web
serve -s .
```

### خيار 3: نشر على GitHub Pages

1. ادفع مجلد `build/web` إلى GitHub
2. فعّل GitHub Pages في إعدادات المستودع
3. اختر مجلد `build/web` كمصدر

### خيار 4: نشر على Firebase Hosting

```bash
npm install -g firebase-tools
firebase login
firebase init hosting
# اختر build/web كمجلد النشر
firebase deploy
```

### خيار 5: نشر على Netlify

1. اسحب مجلد `build/web` إلى Netlify
2. أو استخدم Netlify CLI:

```bash
npm install -g netlify-cli
cd build/web
netlify deploy --prod
```

## الخطوة 5: تكوين عنوان API للإنتاج

قبل النشر، تأكد من تحديث عنوان API في `lib/core/config/app_config.dart`:

```dart
static String apiBaseUrl = 'https://your-api-domain.com';
```

أو استخدم متغيرات البيئة:

```dart
static String apiBaseUrl = 
    const String.fromEnvironment('API_URL', defaultValue: 'http://localhost:3000');
```

ثم عند البناء:

```bash
flutter build web --dart-define=API_URL=https://your-api-domain.com
```

## الميزات المدعومة على الويب

✅ جميع الميزات الأساسية تعمل
✅ دعم العربية RTL
✅ التصميم الداكن
✅ اختيار المنصة
✅ التحقق من الحساب
✅ عرض الإشارات
✅ حاسبة المخاطر
✅ الإعدادات

## ملاحظات مهمة

1. **CORS**: تأكد من أن خادم API يدعم CORS للطلبات من الويب
2. **HTTPS**: في الإنتاج، استخدم HTTPS دائماً
3. **PWA**: الموقع يدعم PWA ويمكن تثبيته كتطبيق
4. **التخزين**: يستخدم LocalStorage على الويب بدلاً من SharedPreferences

## استكشاف الأخطاء

### المشكلة: لا تظهر الأزرار
- تأكد من إعادة تحميل الصفحة (Ctrl+R)
- تحقق من Console للأخطاء

### المشكلة: لا يتصل بالـ API
- تحقق من أن API يعمل على `http://localhost:3000`
- تحقق من إعدادات CORS في API
- في الإنتاج، تأكد من تحديث `apiBaseUrl`

### المشكلة: الأخطاء في Console
- افتح DevTools (F12)
- تحقق من تبويب Console
- تحقق من تبويب Network للطلبات الفاشلة

## التحويل إلى تطبيق لاحقاً

بعد التأكد من عمل الموقع بشكل صحيح، يمكنك:

1. **Android**: `flutter build apk` أو `flutter build appbundle`
2. **iOS**: `flutter build ios`
3. **Windows**: `flutter build windows`
4. **macOS**: `flutter build macos`

جميع الميزات ستعمل بنفس الطريقة!

