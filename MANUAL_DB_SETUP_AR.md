# دليل إنشاء قاعدة البيانات يدوياً

هذا الدليل يشرح كيفية إنشاء قاعدة البيانات والجداول يدوياً باستخدام pgAdmin أو سطر الأوامر.

## الطريقة 1: استخدام pgAdmin

### الخطوة 1: إنشاء قاعدة البيانات

1. افتح pgAdmin
2. قم بتوسيع الخادم (PostgreSQL 18)
3. انقر بزر الماوس الأيمن على **"Databases"**
4. اختر **"Create"** → **"Database..."**
5. في تبويب "General":
   - **Database**: `botsignal_db`
6. انقر **"Save"**

### الخطوة 2: إنشاء الجداول

1. قم بتوسيع قاعدة البيانات `botsignal_db`
2. انقر بزر الماوس الأيمن على `botsignal_db`
3. اختر **"Query Tool"**
4. افتح ملف `apps/api_nest/prisma/create_tables.sql`
5. انسخ جميع محتويات الملف والصقها في Query Tool
6. انقر على زر **Execute** (▶) أو اضغط `F5`

### الخطوة 3: التحقق من الجداول

1. قم بتوسيع `botsignal_db` → `Schemas` → `public` → `Tables`
2. يجب أن ترى الجداول التالية:
   - `devices`
   - `accounts`
   - `device_accounts`
   - `postback_events`
   - `signals`
   - `notifications_log`

## الطريقة 2: استخدام سطر الأوامر (psql)

### الخطوة 1: الاتصال بـ PostgreSQL

```bash
# على Windows (PowerShell أو Git Bash)
psql -U postgres -h localhost

# أو إذا كان لديك كلمة مرور
psql -U postgres -h localhost -d postgres
```

### الخطوة 2: إنشاء قاعدة البيانات

```sql
CREATE DATABASE botsignal_db;
\q
```

### الخطوة 3: الاتصال بقاعدة البيانات الجديدة

```bash
psql -U postgres -h localhost -d botsignal_db
```

### الخطوة 4: تشغيل ملف SQL

```bash
# من سطر الأوامر
psql -U postgres -h localhost -d botsignal_db -f apps/api_nest/prisma/create_tables.sql

# أو من داخل psql
\i apps/api_nest/prisma/create_tables.sql
```

## الطريقة 3: نسخ ولصق الأوامر مباشرة

إذا كنت تفضل نسخ الأوامر مباشرة، افتح ملف `apps/api_nest/prisma/create_tables.sql` وانسخ المحتوى.

## ملء البيانات التجريبية (Seed Data)

بعد إنشاء الجداول، يمكنك ملء البيانات التجريبية:

### الطريقة 1: استخدام Prisma Seed

```bash
cd apps/api_nest
npm run prisma:seed
```

### الطريقة 2: يدوياً عبر SQL

```sql
-- إدراج حسابات تجريبية
INSERT INTO accounts (id, platform, "accountId", status, "lastDepositAmount", "lastDepositAt", "createdAt", "updatedAt")
VALUES 
  (gen_random_uuid()::text, 'QUOTEX', 'TEST_ACTIVE_123', 'DEPOSITED', 100.0, NOW(), NOW(), NOW()),
  (gen_random_uuid()::text, 'QUOTEX', 'TEST_NO_DEPOSIT_456', 'NO_DEPOSIT', NULL, NULL, NOW(), NOW())
ON CONFLICT (platform, "accountId") DO NOTHING;

-- إدراج إشارات تجريبية
INSERT INTO signals (id, platform, asset, direction, "expirySeconds", confidence, "newsStatus", active, "createdAt")
VALUES 
  (gen_random_uuid()::text, 'QUOTEX', 'EUR/USD', 'CALL', 60, 75, 'SAFE', true, NOW()),
  (gen_random_uuid()::text, 'QUOTEX', 'GBP/USD', 'PUT', 300, 80, 'WARNING', true, NOW()),
  (gen_random_uuid()::text, 'POCKET_OPTION', 'BTC/USD', 'CALL', 180, 70, 'SAFE', true, NOW());
```

## تحديث ملف .env

بعد إنشاء قاعدة البيانات يدوياً، تأكد من تحديث `apps/api_nest/.env`:

```env
DATABASE_URL="postgresql://postgres:YOUR_PASSWORD@localhost:5432/botsignal_db?schema=public"
```

استبدل `YOUR_PASSWORD` بكلمة مرور المستخدم `postgres` في PostgreSQL.

## التحقق من الإعداد

### 1. التحقق من الجداول

```sql
-- في pgAdmin Query Tool أو psql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';
```

يجب أن ترى 6 جداول.

### 2. التحقق من الأنواع (Enums)

```sql
SELECT typname 
FROM pg_type 
WHERE typtype = 'e';
```

يجب أن ترى:
- Platform
- Direction
- NewsStatus
- AccountStatus

### 3. التحقق من البيانات

```sql
SELECT * FROM accounts;
SELECT * FROM signals;
```

## حل المشاكل

### خطأ: "relation already exists"
إذا ظهر هذا الخطأ، الجدول موجود بالفعل. يمكنك:
- حذف الجدول وإعادة إنشائه
- أو تجاهل الخطأ إذا كان الجدول صحيحاً

### خطأ: "type already exists"
الأنواع موجودة بالفعل. يمكنك تجاهل هذا الخطأ.

### حذف وإعادة إنشاء كل شيء

```sql
-- حذف الجداول
DROP TABLE IF EXISTS "notifications_log" CASCADE;
DROP TABLE IF EXISTS "signals" CASCADE;
DROP TABLE IF EXISTS "postback_events" CASCADE;
DROP TABLE IF EXISTS "device_accounts" CASCADE;
DROP TABLE IF EXISTS "accounts" CASCADE;
DROP TABLE IF EXISTS "devices" CASCADE;

-- حذف الأنواع
DROP TYPE IF EXISTS "AccountStatus" CASCADE;
DROP TYPE IF EXISTS "NewsStatus" CASCADE;
DROP TYPE IF EXISTS "Direction" CASCADE;
DROP TYPE IF EXISTS "Platform" CASCADE;
```

ثم قم بتشغيل `create_tables.sql` مرة أخرى.

## الخطوات التالية

بعد إنشاء الجداول:

1. ✅ تحديث `apps/api_nest/.env` بـ DATABASE_URL الصحيح
2. ✅ تشغيل `npm run prisma:generate` في `apps/api_nest`
3. ✅ ملء البيانات التجريبية: `npm run prisma:seed`
4. ✅ تشغيل الخادم: `npm run start:dev`

## ملاحظات مهمة

- تأكد من أن PostgreSQL يعمل قبل إنشاء قاعدة البيانات
- استخدم نفس بيانات الاتصال في `DATABASE_URL`
- إذا استخدمت مستخدم مختلف عن `postgres`، حدّث `DATABASE_URL` accordingly

