# تطبيق إشارات الخيارات الثنائية

تطبيق جاهز للإنتاج "إشارات فقط" للهاتف المحمول (واجهة عربية أولاً، تصميم داكن جريء) لإشارات الخيارات الثنائية.

## هيكل المشروع

```
.
├── apps/
│   ├── mobile_flutter/     # تطبيق Flutter للهاتف المحمول
│   └── api_nest/           # واجهة برمجة تطبيقات NestJS الخلفية
├── docker-compose.yml      # إعداد التطوير المحلي
└── README.md
```

## التقنيات المستخدمة

- **الهاتف المحمول**: Flutter (Dart) - Android + iOS
- **الخادم**: Node.js + NestJS (TypeScript)
- **قاعدة البيانات**: PostgreSQL مع Prisma ORM
- **الإشعارات الفورية**: Firebase Cloud Messaging (FCM)
- **المصادقة**: مصادقة قائمة على الجهاز

## البدء السريع

### المتطلبات الأساسية

- Node.js 18+
- Flutter 3.0+
- Docker & Docker Compose
- PostgreSQL (أو استخدم Docker Compose)

### 1. تشغيل قاعدة البيانات

```bash
docker-compose up -d postgres
```

### 2. إعداد الخادم

```bash
cd apps/api_nest
npm install
cp env.example .env
# عدّل .env بقيمك
npm run prisma:generate
npm run prisma:migrate
npm run prisma:seed
npm run start:dev
```

الخادم يعمل على: http://localhost:3000
وثائق API: http://localhost:3000/docs

### 3. إعداد تطبيق Flutter

```bash
cd apps/mobile_flutter
flutter pub get
# انسخ .env.example إلى .env وقم بالتكوين
flutter run
```

## متغيرات البيئة

راجع ملفات `.env.example` في كل مجلد تطبيق.

## الميزات

- ✅ اختيار المنصة (Quotex، Pocket Option)
- ✅ التحقق من الحساب عبر postback
- ✅ خلاصة الإشارات (مقفلة/مفتوحة حسب الحالة)
- ✅ حاسبة المخاطر
- ✅ الإشعارات الفورية
- ✅ دعم العربية RTL
- ✅ تصميم داكن جريء

## ملاحظات مهمة

- هذا التطبيق لا يضع صفقات
- إشارات فقط - يجب على المستخدمين استخدام تطبيقات/مواقع الوسطاء
- الربح من خلال تتبع الإحالة
- التحقق من التسجيل عبر postback الشريك

## الحسابات التجريبية

استخدم معرفات الحسابات التجريبية من البيانات المملوءة:
- `TEST_ACTIVE_123` (QUOTEX) - VERIFIED_ACTIVE
- `TEST_NO_DEPOSIT_456` (QUOTEX) - VERIFIED_NO_DEPOSIT

## الوثائق

- `SETUP_AR.md` - دليل الإعداد الكامل بالعربية
- `SETUP.md` - دليل الإعداد الكامل بالإنجليزية
- `PGADMIN_GUIDE_AR.md` - دليل استخدام pgAdmin بالعربية
- `MANUAL_DB_SETUP_AR.md` - دليل إنشاء قاعدة البيانات يدوياً
- `TROUBLESHOOTING_AR.md` - حل مشاكل الاتصال بقاعدة البيانات
- `PROJECT_SUMMARY.md` - قائمة الميزات الكاملة
- `QUICK_REFERENCE.md` - الأوامر السريعة

## الدعم

للحصول على مساعدة، راجع:
- `SETUP_AR.md` - دليل الإعداد التفصيلي
- `QUICK_REFERENCE.md` - مرجع سريع للأوامر

