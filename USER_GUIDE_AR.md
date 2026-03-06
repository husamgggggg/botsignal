# دليل المستخدم: كيفية تفعيل الإشارات في التطبيق

## 📱 الخطوات المطلوبة

### 1️⃣ تسجيل الدخول (JWT Token) ✅
**يحدث تلقائياً!** عند فتح التطبيق:
- التطبيق ينشئ `deviceId` فريد تلقائياً
- يسجل الجهاز في قاعدة البيانات
- يحصل على JWT token تلقائياً
- **لا حاجة لأي إجراء يدوي**

---

### 2️⃣ ربط حساب بالجهاز 🔗

#### الطريقة 1: عبر التطبيق (للمستخدمين)

1. **افتح التطبيق** على `https://thetrading.io`
2. **اختر المنصة** (Quotex أو Pocket Option)
3. **أدخل Account ID** من حسابك في المنصة
4. **اضغط "تحقق"**
5. **النتيجة:**
   - ✅ **VERIFIED_ACTIVE**: الحساب مرتبط وله إيداع → يمكن رؤية الإشارات
   - ⚠️ **VERIFIED_NO_DEPOSIT**: الحساب مرتبط لكن بدون إيداع → لا يمكن رؤية الإشارات
   - ❌ **NOT_UNDER_TEAM**: الحساب غير موجود → يجب التسجيل أولاً

#### الطريقة 2: يدوياً عبر Admin API (للمطورين)

```bash
# على السيرفر
cd /var/www/botsignal/apps/api_nest

# الحصول على ADMIN_API_KEY من .env
cat .env | grep ADMIN_API_KEY

# إضافة حساب يدوياً
curl -X POST https://thetrading.io/api/admin/accounts \
  -H "Content-Type: application/json" \
  -H "X-Admin-Api-Key: YOUR_ADMIN_API_KEY" \
  -d '{
    "platform": "QUOTEX",
    "accountId": "TEST_ACTIVE_123",
    "status": "DEPOSITED",
    "lastDepositAmount": 100.0
  }'

# ربط حساب بجهاز (تحتاج deviceId من قاعدة البيانات)
# يمكنك الحصول عليه من Prisma Studio أو من logs
```

---

### 3️⃣ جعل الحساب بحالة DEPOSITED 💰

#### الطريقة 1: تلقائياً عبر Postback (مثالي)

عندما يقوم المستخدم بإيداع في Quotex:
- Quotex يرسل postback إلى السيرفر
- السيرفر يحدث حالة الحساب تلقائياً إلى `DEPOSITED`
- **لا حاجة لأي إجراء يدوي**

**إعداد Postback في Quotex:**
```
Postback URL: https://thetrading.io/api/postback/quotex?secret=YOUR_POSTBACK_SECRET
```

#### الطريقة 2: يدوياً عبر Admin API

```bash
# تحديث حالة الحساب إلى DEPOSITED
curl -X PUT https://thetrading.io/api/admin/accounts/QUOTEX/TEST_ACTIVE_123/status \
  -H "Content-Type: application/json" \
  -H "X-Admin-Api-Key: YOUR_ADMIN_API_KEY" \
  -d '{
    "status": "DEPOSITED",
    "lastDepositAmount": 100.0
  }'
```

#### الطريقة 3: مباشرة في قاعدة البيانات

```bash
# على السيرفر
cd /var/www/botsignal/apps/api_nest
psql $DATABASE_URL

# تحديث حالة الحساب
UPDATE accounts 
SET status = 'DEPOSITED', 
    "lastDepositAmount" = 100.0,
    "lastDepositAt" = NOW()
WHERE platform = 'QUOTEX' AND "accountId" = 'TEST_ACTIVE_123';
```

---

## 🧪 حساب تجريبي للاختبار

تم إنشاء حساب تجريبي في قاعدة البيانات:

```bash
# الحساب التجريبي
Account ID: TEST_ACTIVE_123
Platform: QUOTEX
Status: DEPOSITED
```

**للاستخدام:**
1. افتح التطبيق
2. اختر Quotex
3. أدخل `TEST_ACTIVE_123`
4. اضغط "تحقق"
5. يجب أن ترى الإشارات فوراً! ✅

---

## 🔍 التحقق من الحالة

### في التطبيق:
1. افتح Developer Console (F12)
2. ابحث عن:
   - `✅ Loaded X signals from API` → نجح التحميل
   - `⚠️ No auth token` → لم يتم تسجيل الدخول
   - `❌ Error loading signals` → خطأ في API

### في قاعدة البيانات:

```bash
# التحقق من الأجهزة
psql $DATABASE_URL -c "SELECT \"deviceId\", \"lastSeenAt\" FROM devices LIMIT 5;"

# التحقق من الحسابات
psql $DATABASE_URL -c "SELECT platform, \"accountId\", status FROM accounts;"

# التحقق من الربط بين الأجهزة والحسابات
psql $DATABASE_URL -c "SELECT d.\"deviceId\", a.\"accountId\", a.status FROM device_accounts da JOIN devices d ON da.\"deviceId\" = d.id JOIN accounts a ON da.\"accountId\" = a.id;"

# التحقق من الإشارات
psql $DATABASE_URL -c "SELECT asset, direction, confidence, active, \"createdAt\" FROM signals WHERE active = true ORDER BY \"createdAt\" DESC LIMIT 5;"
```

### عبر API:

```bash
# جميع الإشارات (بدون authentication)
curl https://thetrading.io/api/signals/debug/all

# الإشارات للمستخدم (يتطلب JWT token)
curl https://thetrading.io/api/signals \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## ❓ حل المشاكل الشائعة

### المشكلة: "Account verification required"
**الحل:**
1. تأكد من ربط الحساب بالجهاز (الخطوة 2)
2. تأكد من أن الحساب بحالة `DEPOSITED` (الخطوة 3)

### المشكلة: "Device not found"
**الحل:**
1. امسح cache المتصفح
2. افتح التطبيق مرة أخرى (سيتم تسجيل الجهاز تلقائياً)

### المشكلة: الإشارات لا تظهر
**الحل:**
1. تحقق من Developer Console (F12)
2. تأكد من أن API يعمل: `curl https://thetrading.io/api/signals/debug/all`
3. تأكد من أن الإشارات موجودة في قاعدة البيانات
4. تأكد من أن Cooldown انتهى (60 ثانية بين الإشارات)

---

## 📞 الدعم

إذا واجهت مشاكل:
1. تحقق من logs: `pm2 logs botsignal-api --lines 50`
2. تحقق من قاعدة البيانات
3. تحقق من Developer Console في المتصفح

