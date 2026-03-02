# دليل استخدام pgAdmin

هذا الدليل يشرح كيفية الاتصال بقاعدة البيانات وإدارتها باستخدام pgAdmin.

## معلومات الاتصال

بعد تشغيل `docker-compose up -d postgres`، استخدم الإعدادات التالية:

### بيانات الاتصال
- **Host**: `localhost`
- **Port**: `5432`
- **Database**: `botsignal_db`
- **Username**: `botsignal`
- **Password**: `botsignal_dev_password`

## خطوات الاتصال

### 1. إضافة خادم جديد

1. افتح pgAdmin
2. في الشريط الجانبي الأيسر، انقر بزر الماوس الأيمن على **"Servers"**
3. اختر **"Create"** → **"Server..."**

### 2. إعداد الخادم

#### تبويب "General"
- **Name**: `Botsignal Local` (أو أي اسم تفضله)

#### تبويب "Connection"
- **Host name/address**: `localhost`
- **Port**: `5432`
- **Maintenance database**: `botsignal_db`
- **Username**: `botsignal`
- **Password**: `botsignal_dev_password`
- ✅ **Save password** (احفظ كلمة المرور)

#### تبويب "Advanced" (اختياري)
- **DB restriction**: اتركه فارغاً

### 3. حفظ الاتصال

انقر على **"Save"** في الأسفل.

## استخدام قاعدة البيانات

بعد الاتصال بنجاح:

1. **عرض قواعد البيانات**: 
   - قم بتوسيع `Botsignal Local` → `Databases`
   - ستجد `botsignal_db`

2. **عرض الجداول**:
   - قم بتوسيع `botsignal_db` → `Schemas` → `public` → `Tables`
   - ستجد الجداول التالية:
     - `devices` - الأجهزة المسجلة
     - `accounts` - حسابات الوسيط
     - `device_accounts` - ربط الأجهزة بالحسابات
     - `postback_events` - سجل أحداث postback
     - `signals` - الإشارات
     - `notifications_log` - سجل الإشعارات

3. **عرض البيانات**:
   - انقر بزر الماوس الأيمن على أي جدول
   - اختر **"View/Edit Data"** → **"All Rows"**

## استعلامات مفيدة

### عرض جميع الحسابات
```sql
SELECT * FROM accounts;
```

### عرض جميع الإشارات النشطة
```sql
SELECT * FROM signals WHERE active = true ORDER BY "createdAt" DESC;
```

### عرض الأجهزة المرتبطة بحساب معين
```sql
SELECT d."deviceId", a."accountId", a.platform, a.status
FROM devices d
JOIN device_accounts da ON d.id = da."deviceId"
JOIN accounts a ON da."accountId" = a.id;
```

### عرض أحداث postback الأخيرة
```sql
SELECT * FROM postback_events 
ORDER BY "receivedAt" DESC 
LIMIT 10;
```

### تحديث حالة حساب يدوياً
```sql
-- تغيير حالة حساب إلى DEPOSITED
UPDATE accounts 
SET status = 'DEPOSITED', 
    "lastDepositAmount" = 100.0,
    "lastDepositAt" = NOW()
WHERE "accountId" = 'TEST_ACTIVE_123' AND platform = 'QUOTEX';
```

### إنشاء حساب تجريبي جديد
```sql
INSERT INTO accounts (platform, "accountId", status)
VALUES ('QUOTEX', 'NEW_TEST_ACCOUNT', 'REGISTERED')
ON CONFLICT (platform, "accountId") DO NOTHING;
```

## إدارة قاعدة البيانات

### نسخ احتياطي (Backup)
1. انقر بزر الماوس الأيمن على `botsignal_db`
2. اختر **"Backup..."**
3. اختر المسار واسم الملف
4. انقر **"Backup"**

### استعادة (Restore)
1. انقر بزر الماوس الأيمن على `botsignal_db`
2. اختر **"Restore..."**
3. اختر ملف النسخة الاحتياطية
4. انقر **"Restore"**

### إعادة تعيين قاعدة البيانات
إذا أردت إعادة تعيين قاعدة البيانات بالكامل:

```sql
-- حذف جميع البيانات (احذر!)
TRUNCATE TABLE "notifications_log" CASCADE;
TRUNCATE TABLE signals CASCADE;
TRUNCATE TABLE "postback_events" CASCADE;
TRUNCATE TABLE "device_accounts" CASCADE;
TRUNCATE TABLE accounts CASCADE;
TRUNCATE TABLE devices CASCADE;
```

ثم قم بتشغيل:
```bash
cd apps/api_nest
npm run prisma:seed
```

## حل المشاكل

### لا يمكن الاتصال
- تأكد من تشغيل Docker Compose: `docker-compose ps`
- تحقق من أن PostgreSQL يعمل: `docker-compose logs postgres`
- جرب الاتصال من سطر الأوامر:
  ```bash
  docker exec -it botsignal-postgres psql -U botsignal -d botsignal_db
  ```

### كلمة المرور غير صحيحة (password authentication failed)

**الأسباب الشائعة:**
1. كلمة المرور مكتوبة بشكل خاطئ
2. Container لم يبدأ بعد
3. كلمة المرور لم يتم تعيينها بشكل صحيح

**الحلول:**

**1. تأكد من كلمة المرور الصحيحة:**
- Username: `botsignal`
- Password: `botsignal_dev_password` (بدون مسافات إضافية)

**2. تحقق من حالة Container:**
```bash
docker-compose ps
# يجب أن ترى botsignal-postgres في حالة "Up"
```

**3. إعادة تشغيل Container:**
```bash
docker-compose restart postgres
# انتظر 5-10 ثوانٍ ثم جرب الاتصال مرة أخرى
```

**4. إعادة إنشاء Container (إذا استمرت المشكلة):**
```bash
docker-compose down -v
docker-compose up -d postgres
# انتظر 10 ثوانٍ ثم جرب الاتصال
```

**5. اختبار الاتصال من Terminal:**
```bash
docker exec -it botsignal-postgres psql -U botsignal -d botsignal_db
# إذا نجح، المشكلة في إعدادات pgAdmin
```

**6. في pgAdmin:**
- تأكد من تفعيل ✅ **Save password**
- امسح حقل Password وأعد كتابته
- جرب حذف الاتصال وإنشائه من جديد

راجع `TROUBLESHOOTING_AR.md` للحلول التفصيلية.

### قاعدة البيانات غير موجودة
- قم بتشغيل migrations:
  ```bash
  cd apps/api_nest
  npm run prisma:migrate
  ```

## نصائح مفيدة

1. **استخدام Query Tool**: 
   - انقر بزر الماوس الأيمن على `botsignal_db` → **"Query Tool"**
   - اكتب استعلامات SQL مباشرة

2. **مراقبة الجداول**:
   - يمكنك مراقبة التغييرات في الجداول أثناء تشغيل التطبيق

3. **تصدير البيانات**:
   - انقر بزر الماوس الأيمن على أي جدول → **"Export/Import"** → **"Export"**

4. **استيراد البيانات**:
   - يمكنك استيراد بيانات CSV أو SQL مباشرة

## معلومات إضافية

- **المنفذ**: 5432 (افتراضي PostgreSQL)
- **النسخة**: PostgreSQL 15
- **الموقع**: Docker Container (`botsignal-postgres`)
- **حجم البيانات**: يتم حفظها في volume Docker (`postgres_data`)

