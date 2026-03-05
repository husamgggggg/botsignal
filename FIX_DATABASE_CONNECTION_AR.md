# حل مشكلة الاتصال بقاعدة البيانات

## المشكلة

```
PrismaClientInitializationError: Authentication failed against database server at `localhost`, 
the provided database credentials for `botsignal` are not valid.
```

## الحل

المشكلة أن بيانات الاعتماد في ملف `.env` لا تطابق بيانات PostgreSQL الفعلية.

### الخطوة 1: التحقق من بيانات PostgreSQL

إذا أنشأت قاعدة البيانات يدوياً في pgAdmin، على الأرجح استخدمت:
- **Username**: `postgres` (وليس `botsignal`)
- **Password**: كلمة مرور PostgreSQL الخاصة بك
- **Database**: `botsignal_db` أو `botsignal`

### الخطوة 2: تحديث ملف .env

افتح `apps/api_nest/.env` وحدّث `DATABASE_URL`:

#### إذا استخدمت مستخدم `postgres`:

```env
DATABASE_URL="postgresql://postgres:YOUR_PASSWORD@localhost:5432/botsignal_db?schema=public"
```

استبدل `YOUR_PASSWORD` بكلمة مرور PostgreSQL الخاصة بك.

#### إذا أنشأت مستخدم `botsignal`:

```env
DATABASE_URL="postgresql://botsignal:YOUR_PASSWORD@localhost:5432/botsignal_db?schema=public"
```

### الخطوة 3: إنشاء المستخدم `botsignal` (اختياري)

إذا أردت استخدام مستخدم `botsignal` بدلاً من `postgres`:

#### في pgAdmin Query Tool:

```sql
-- إنشاء المستخدم
CREATE USER botsignal WITH PASSWORD 'botsignal_dev_password';

-- منح الصلاحيات
GRANT ALL PRIVILEGES ON DATABASE botsignal_db TO botsignal;

-- منح الصلاحيات على الجداول
\c botsignal_db
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO botsignal;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO botsignal;
```

ثم استخدم في `.env`:
```env
DATABASE_URL="postgresql://botsignal:botsignal_dev_password@localhost:5432/botsignal_db?schema=public"
```

### الخطوة 4: التحقق من الاتصال

بعد تحديث `.env`، أعد تشغيل الخادم:

```bash
# إيقاف الخادم (Ctrl+C)
# ثم إعادة التشغيل
npm run start:dev
```

## الحل السريع

### إذا كنت تستخدم `postgres` كمستخدم:

1. افتح `apps/api_nest/.env`
2. غيّر `DATABASE_URL` إلى:
   ```env
   DATABASE_URL="postgresql://postgres:YOUR_POSTGRES_PASSWORD@localhost:5432/botsignal_db?schema=public"
   ```
3. أعد تشغيل الخادم

### إذا لم تكن متأكداً من كلمة المرور:

1. افتح pgAdmin
2. انقر بزر الماوس الأيمن على الخادم → **Properties**
3. ابحث عن كلمة المرور المحفوظة
4. أو جرب الاتصال من pgAdmin لمعرفة كلمة المرور الصحيحة

## التحقق من قاعدة البيانات

في pgAdmin، تأكد من:
1. ✅ قاعدة البيانات `botsignal_db` موجودة
2. ✅ الجداول موجودة (devices, accounts, signals, etc.)
3. ✅ يمكنك الاتصال بقاعدة البيانات

## ملاحظات

- تأكد من أن PostgreSQL يعمل
- تأكد من أن المنفذ 5432 مفتوح
- تأكد من أن قاعدة البيانات موجودة
- تأكد من أن المستخدم لديه الصلاحيات الكافية

