# واجهة برمجة تطبيقات إشارات الخيارات الثنائية

واجهة برمجة تطبيقات NestJS الخلفية لتطبيق إشارات الخيارات الثنائية للهاتف المحمول.

## الإعداد

1. **تثبيت المكتبات:**
   ```bash
   npm install
   ```

2. **تكوين البيئة:**
   ```bash
   cp env.example .env
   # عدّل .env بقيمك
   ```

3. **إعداد قاعدة البيانات:**
   ```bash
   # تأكد من تشغيل PostgreSQL (عبر Docker Compose)
   npm run prisma:generate
   npm run prisma:migrate
   npm run prisma:seed
   ```

4. **تشغيل خادم التطوير:**
   ```bash
   npm run start:dev
   ```

الواجهة ستكون متاحة على: http://localhost:3000
وثائق Swagger: http://localhost:3000/docs

## متغيرات البيئة

راجع `env.example` لجميع المتغيرات المطلوبة.

المتغيرات الرئيسية:
- `DATABASE_URL` - سلسلة اتصال PostgreSQL
- `JWT_SECRET` - سر لرموز JWT
- `ADMIN_API_KEY` - مفتاح API لنقاط نهاية Admin
- `POSTBACK_SECRET` - سر للتحقق من postback
- `FIREBASE_*` - بيانات اعتماد Firebase للإشعارات الفورية

## نقاط نهاية API

### عام
- `POST /api/auth/register` - تسجيل الجهاز
- `POST /api/verify` - التحقق من الحساب
- `GET /api/platforms` - الحصول على معلومات المنصات

### مصادق (رمز Bearer)
- `GET /api/signals` - الحصول على الإشارات (يتطلب حساب نشط verified)
- `POST /api/auth/fcm-token` - تحديث رمز FCM

### Admin (رأس X-Admin-Api-Key)
- `POST /api/admin/signals` - إنشاء إشارة

### Postback
- `GET /api/postback/quotex` - نقطة نهاية postback Quotex
- `GET /api/postback/pocket-option` - نقطة نهاية postback Pocket Option

## اختبار Postback

يمكنك اختبار نقطة نهاية postback باستخدام curl:

```bash
# حدث التسجيل
curl "http://localhost:3000/api/postback/quotex?event_type=registration&click_id=TEST_123&secret=your-postback-secret"

# حدث الإيداع
curl "http://localhost:3000/api/postback/quotex?event_type=deposit&click_id=TEST_123&deposit_amount=100&secret=your-postback-secret"
```

## الحسابات التجريبية

بعد تشغيل `npm run prisma:seed`، ستكون الحسابات التالية متاحة:
- `TEST_ACTIVE_123` (QUOTEX) - DEPOSITED
- `TEST_NO_DEPOSIT_456` (QUOTEX) - NO_DEPOSIT

## الأوامر المتاحة

- `npm run start:dev` - تشغيل خادم التطوير
- `npm run build` - بناء للإنتاج
- `npm run start:prod` - تشغيل الإنتاج
- `npm run prisma:generate` - إنشاء Prisma client
- `npm run prisma:migrate` - تشغيل migrations
- `npm run prisma:seed` - ملء قاعدة البيانات ببيانات تجريبية

