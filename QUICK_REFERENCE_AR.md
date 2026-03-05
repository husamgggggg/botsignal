# دليل المرجع السريع

## 🚀 الأوامر السريعة

### تشغيل كل شيء
```bash
# 1. قاعدة البيانات
docker-compose up -d postgres

# 2. الخادم (في apps/api_nest)
npm install && npm run prisma:generate && npm run prisma:migrate && npm run prisma:seed && npm run start:dev

# 3. Flutter (في apps/mobile_flutter)
flutter pub get && flutter run
```

### ملء البيانات (Seed)
```bash
# استخدم npm run (وليس npx prisma seed)
npm run prisma:seed

# أو مباشرة
npx ts-node prisma/seed.ts
```

## 🧪 معرفات الحسابات التجريبية

- `TEST_ACTIVE_123` → وصول كامل (VERIFIED_ACTIVE)
- `TEST_NO_DEPOSIT_456` → إيداع مطلوب (VERIFIED_NO_DEPOSIT)
- أي معرف آخر → تسجيل مطلوب (NOT_UNDER_TEAM)

## 📡 عناوين API الأساسية

- **محاكي Android**: `http://10.0.2.2:3000`
- **محاكي iOS**: `http://localhost:3000`
- **جهاز فعلي**: `http://IP_الكمبيوتر:3000`

## 🔑 اختبار Admin API

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

## 📨 اختبار Postback

```bash
# التسجيل
curl "http://localhost:3000/api/postback/quotex?event_type=registration&click_id=NEW_USER&secret=your-postback-secret"

# الإيداع
curl "http://localhost:3000/api/postback/quotex?event_type=deposit&click_id=NEW_USER&deposit_amount=100&secret=your-postback-secret"
```

## 🔍 التحقق من الحالة

- **الخادم يعمل**: `curl http://localhost:3000/api/platforms`
- **قاعدة البيانات**: `docker-compose ps`
- **Swagger**: http://localhost:3000/docs

## 🗄️ الاتصال بـ pgAdmin

**بيانات الاتصال:**
- Host: `localhost`
- Port: `5432`
- Database: `botsignal_db`
- Username: `botsignal`
- Password: `botsignal_dev_password`

راجع `PGADMIN_GUIDE_AR.md` للدليل الكامل.

## 📱 مسارات التطبيق

- `/platform-select` - اختر المنصة
- `/account-verify` - أدخل معرف الحساب
- `/verify-result` - حالة التحقق
- `/home` - خلاصة الإشارات
- `/signal/:id` - تفاصيل الإشارة
- `/risk-calculator` - حاسبة المخاطر
- `/settings` - الإعدادات

## 🎨 ألوان التصميم

- الأسود الأساسي: `#000000`
- الأخضر النيون: `#00FF41`
- الأزرق النيون: `#00D9FF`
- الرمادي الداكن: `#1A1A1A`

## 🌐 اللغات

- العربية (ar) - الافتراضي، RTL
- الإنجليزية (en) - LTR

## ⚙️ الملفات الرئيسية

- تكوين الخادم: `apps/api_nest/.env`
- مخطط قاعدة البيانات: `apps/api_nest/prisma/schema.prisma`
- تصميم Flutter: `apps/mobile_flutter/lib/core/theme/app_theme.dart`
- مسارات التطبيق: `apps/mobile_flutter/lib/core/routing/app_router.dart`

## 📝 حالات التحقق

1. **VERIFIED_ACTIVE** - حساب نشط مع إيداع → وصول كامل للإشارات
2. **VERIFIED_NO_DEPOSIT** - حساب مسجل بدون إيداع → يطلب الإيداع
3. **NOT_UNDER_TEAM** - حساب غير موجود → يطلب التسجيل

## 🔔 الإشعارات الفورية

- يتم إرسال الإشعارات تلقائياً عند إنشاء إشارة جديدة
- تُرسل فقط للأجهزة ذات الحسابات النشطة (VERIFIED_ACTIVE)
- إشعارات ثنائية اللغة (عربي/إنجليزي)

## 🛠️ حل المشاكل السريع

### الخادم لا يعمل
```bash
cd apps/api_nest
npm run start:dev
```

### قاعدة البيانات لا تعمل
```bash
docker-compose up -d postgres
docker-compose logs postgres
```

### Flutter لا يتصل بالخادم
- تحقق من عنوان API في `lib/core/config/app_config.dart`
- لمحاكي Android: استخدم `10.0.2.2` بدلاً من `localhost`
- للجهاز الفعلي: استخدم IP الكمبيوتر

### الإشعارات لا تعمل
- Firebase اختياري للإصدار الأولي
- تحقق من بيانات Firebase في `.env`
- راجع سجلات الخادم

