# دليل الإعداد الكامل

هذا الدليل سيساعدك في إعداد وتشغيل تطبيق إشارات الخيارات الثنائية بالكامل محلياً.

## المتطلبات الأساسية

- Node.js 18+ مثبت
- Flutter 3.0+ مثبت
- Docker & Docker Compose مثبت
- PostgreSQL (أو استخدم Docker Compose)

## الخطوة 1: تشغيل قاعدة البيانات

```bash
docker-compose up -d postgres
```

انتظر بضع ثوانٍ حتى يكون PostgreSQL جاهزاً.

### الاتصال بقاعدة البيانات باستخدام pgAdmin

إذا كنت تستخدم pgAdmin لإدارة قاعدة البيانات، استخدم الإعدادات التالية:

**إعدادات الاتصال:**
- **Host**: `localhost`
- **Port**: `5432`
- **Database**: `botsignal_db`
- **Username**: `botsignal`
- **Password**: `botsignal_dev_password`

**خطوات الاتصال:**
1. افتح pgAdmin
2. انقر بزر الماوس الأيمن على "Servers" → "Create" → "Server"
3. في تبويب "General":
   - **Name**: `Botsignal Local`
4. في تبويب "Connection":
   - **Host name/address**: `localhost`
   - **Port**: `5432`
   - **Maintenance database**: `botsignal_db`
   - **Username**: `botsignal`
   - **Password**: `botsignal_dev_password` ⚠️ **تأكد من كتابتها بشكل صحيح**
   - ✅ **Save password** (احفظ كلمة المرور)
5. انقر "Save"

**⚠️ إذا ظهرت رسالة خطأ "password authentication failed":**
- تأكد من أن PostgreSQL Container يعمل: `docker-compose ps`
- تأكد من كتابة كلمة المرور بشكل صحيح: `botsignal_dev_password`
- راجع `TROUBLESHOOTING_AR.md` للحلول التفصيلية

بعد الاتصال، ستجد قاعدة البيانات `botsignal_db` في قائمة قواعد البيانات.

## الخطوة 2: إعداد الخادم (Backend)

```bash
cd apps/api_nest

# تثبيت المكتبات
npm install

# نسخ ملف البيئة
cp env.example .env

# عدّل ملف .env وحدد:
# - DATABASE_URL (يجب أن يطابق docker-compose.yml)
# - JWT_SECRET (أنشئ سلسلة عشوائية)
# - ADMIN_API_KEY (أنشئ سلسلة عشوائية)
# - POSTBACK_SECRET (أنشئ سلسلة عشوائية)
# - بيانات Firebase (اختياري للإصدار الأولي)

# إنشاء Prisma client
npm run prisma:generate

# تشغيل migrations
npm run prisma:migrate

# ملء قاعدة البيانات ببيانات تجريبية
npm run prisma:seed
# أو: npx ts-node prisma/seed.ts

# تشغيل خادم التطوير
npm run start:dev
```

الخادم يجب أن يعمل الآن على: http://localhost:3000
وثائق Swagger: http://localhost:3000/docs

## الخطوة 3: إعداد تطبيق Flutter

```bash
cd apps/mobile_flutter

# تثبيت المكتبات
flutter pub get

# لـ Android: حدد عنوان API الأساسي
# عدّل lib/main.dart أو استخدم SharedPreferences لتعيين عنوان API
# لمحاكي Android: http://10.0.2.2:3000
# لمحاكي iOS: http://localhost:3000
# للجهاز الفعلي: http://IP_الكمبيوتر:3000

# تشغيل التطبيق
flutter run
```

## الخطوة 4: اختبار التدفق

1. **افتح التطبيق** - يجب أن يظهر اختيار المنصة
2. **اختر منصة** (مثلاً، Quotex)
3. **أدخل معرف حساب تجريبي**: `TEST_ACTIVE_123`
4. **تحقق** - يجب أن يظهر "VERIFIED_ACTIVE" ويفتح الإشارات
5. **عرض الإشارات** - يجب أن ترى الإشارات المملوءة

### اختبار حالات مختلفة

- `TEST_ACTIVE_123` → VERIFIED_ACTIVE (وصول كامل)
- `TEST_NO_DEPOSIT_456` → VERIFIED_NO_DEPOSIT (إيداع مطلوب)
- أي معرف آخر → NOT_UNDER_TEAM (تسجيل مطلوب)

## الخطوة 5: اختبار Postback (اختياري)

محاكاة حدث postback:

```bash
# حدث التسجيل
curl "http://localhost:3000/api/postback/quotex?event_type=registration&click_id=NEW_USER_789&secret=your-postback-secret"

# حدث الإيداع
curl "http://localhost:3000/api/postback/quotex?event_type=deposit&click_id=NEW_USER_789&deposit_amount=50&secret=your-postback-secret"
```

ثم تحقق من الحساب في التطبيق باستخدام `NEW_USER_789`.

## الخطوة 6: إنشاء إشارة (Admin)

```bash
curl -X POST http://localhost:3000/api/admin/signals \
  -H "Content-Type: application/json" \
  -H "X-Admin-Api-Key: your-admin-api-key" \
  -d '{
    "platform": "QUOTEX",
    "asset": "EUR/USD",
    "direction": "CALL",
    "expirySeconds": 60,
    "confidence": 75,
    "newsStatus": "SAFE"
  }'
```

سيؤدي هذا إلى إنشاء إشارة وإرسال إشعارات push لجميع الأجهزة النشطة الم verified.

## البناء للإنتاج (Production Build)

### بناء الخادم

```bash
cd apps/api_nest

# البناء (سيقوم تلقائياً بنسخ ملفات Prisma وإنشاء Prisma Client)
npm run build

# تطبيق migrations على قاعدة البيانات (للإنتاج)
npm run prisma:migrate:deploy

# تشغيل الخادم في وضع الإنتاج
npm run start:prod
```

**ملاحظات مهمة:**
- ✅ عملية البناء (`npm run build`) تقوم تلقائياً بـ:
  - بناء الكود TypeScript إلى JavaScript في مجلد `dist/`
  - إنشاء Prisma Client
  - نسخ ملفات Prisma (schema.prisma و migrations) إلى `dist/prisma/`
- ✅ تأكد من أن ملف `.env` موجود ويحتوي على جميع المتغيرات المطلوبة
- ✅ في الإنتاج، استخدم `prisma:migrate:deploy` بدلاً من `prisma:migrate dev`
- ✅ مسار تشغيل API بعد البناء: `node dist/main` (يتم تنفيذه عبر `npm run start:prod`)

### التحقق من البناء

```bash
# التحقق من وجود مجلد dist
ls -la dist/

# التحقق من وجود Prisma Client
ls -la node_modules/.prisma/client/

# التحقق من وجود migrations في dist
ls -la dist/prisma/migrations/
```

## حل المشاكل

### مشاكل اتصال قاعدة البيانات
- تأكد من تشغيل Docker Compose: `docker-compose ps`
- تحقق من سجلات PostgreSQL: `docker-compose logs postgres`
- تحقق من DATABASE_URL في `.env` يطابق docker-compose.yml
- **إذا كنت تستخدم pgAdmin**: تأكد من استخدام نفس بيانات الاتصال (localhost:5432, botsignal, botsignal_dev_password)

### مشاكل اتصال Flutter API
- **محاكي Android**: استخدم `http://10.0.2.2:3000` بدلاً من `localhost`
- **محاكي iOS**: `http://localhost:3000` يجب أن يعمل
- **جهاز فعلي**: استخدم IP المحلي لجهازك (مثلاً، `http://192.168.1.100:3000`)
- تحقق من أن الخادم يعمل: `curl http://localhost:3000/api/platforms`

### الإشعارات الفورية لا تعمل
- إعداد Firebase اختياري للإصدار الأولي
- إذا لم يتم التكوين، سيتم تسجيل الإشعارات ولكن لن يتم إرسالها
- تحقق من سجلات الخادم لأخطاء FCM

### مشاكل البناء والإنتاج
- **لا توجد migrations**: تأكد من أن مجلد `prisma/migrations/` موجود ويحتوي على migrations. إذا كان فارغاً، قم بتشغيل `npm run prisma:migrate` أولاً
- **مسار تشغيل API خاطئ**: تأكد من تشغيل `npm run build` قبل `npm run start:prod`. المسار الصحيح هو `node dist/main`
- **Prisma Client غير موجود**: بعد البناء، تأكد من تشغيل `npm run prisma:generate` أو أن عملية البناء قامت بذلك تلقائياً
- **خطأ في نسخ ملفات Prisma**: تأكد من وجود ملف `scripts/copy-prisma.js` وأنه يعمل بشكل صحيح

## مرجع متغيرات البيئة

### الخادم (.env)
```env
DATABASE_URL="postgresql://botsignal:botsignal_dev_password@localhost:5432/botsignal_db?schema=public"
JWT_SECRET="your-super-secret-jwt-key"
JWT_EXPIRES_IN="30d"
PORT=3000
NODE_ENV=development
ADMIN_API_KEY="your-admin-api-key"
POSTBACK_SECRET="your-postback-secret"
POSTBACK_ALLOWED_IPS="127.0.0.1,::1"
FIREBASE_PROJECT_ID=""
FIREBASE_PRIVATE_KEY=""
FIREBASE_CLIENT_EMAIL=""
QUOTEX_AFFILIATE_URL="https://broker.quotex.io/register?affiliate_id=YOUR_ID"
POCKET_OPTION_AFFILIATE_URL="https://pocketoption.com/register?affiliate_id=YOUR_ID"
QUOTEX_DEEP_LINK="quotex://"
POCKET_OPTION_DEEP_LINK="pocketoption://"
```

### Flutter
لا حاجة لملف `.env`. عنوان API الأساسي يتم تكوينه في الكود أو عبر SharedPreferences.

## الخطوات التالية

1. تكوين Firebase للإشعارات الفورية
2. إعداد قاعدة بيانات الإنتاج
3. تكوين روابط الإحالة
4. نشر الخادم للإنتاج
5. بناء ونشر تطبيق الهاتف المحمول

