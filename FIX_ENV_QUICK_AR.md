# حل سريع: تحديث ملف .env

## المشكلة

```
Authentication failed against database server at `localhost`, 
the provided database credentials for `botsignal` are not valid.
```

## الحل السريع

### الخطوة 1: افتح ملف .env

```bash
cd apps/api_nest
# افتح ملف .env في محرر النصوص
```

### الخطوة 2: حدّث DATABASE_URL

**إذا كنت تستخدم `postgres` كمستخدم (الأكثر شيوعاً):**

```env
DATABASE_URL="postgresql://postgres:YOUR_PASSWORD@localhost:5432/botsignal_db?schema=public"
```

استبدل `YOUR_PASSWORD` بكلمة مرور PostgreSQL الخاصة بك.

**كيف تعرف كلمة المرور؟**
1. افتح pgAdmin
2. انقر بزر الماوس الأيمن على الخادم → **Properties**
3. ابحث عن كلمة المرور المحفوظة
4. أو جرب الاتصال من pgAdmin لمعرفة البيانات الصحيحة

### الخطوة 3: أعد تشغيل Seed

```bash
npm run prisma:seed
```

## مثال

إذا كانت كلمة مرور PostgreSQL هي `mypassword123`:

```env
DATABASE_URL="postgresql://postgres:mypassword123@localhost:5432/botsignal_db?schema=public"
```

## إذا لم تكن تعرف كلمة المرور

### الطريقة 1: إعادة تعيين كلمة المرور في PostgreSQL

```sql
-- في pgAdmin Query Tool
ALTER USER postgres WITH PASSWORD 'new_password';
```

ثم استخدم `new_password` في `.env`.

### الطريقة 2: إنشاء مستخدم جديد

```sql
-- في pgAdmin Query Tool
CREATE USER botsignal WITH PASSWORD 'botsignal_dev_password';
GRANT ALL PRIVILEGES ON DATABASE botsignal_db TO botsignal;
\c botsignal_db
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO botsignal;
```

ثم استخدم في `.env`:
```env
DATABASE_URL="postgresql://botsignal:botsignal_dev_password@localhost:5432/botsignal_db?schema=public"
```

## التحقق

بعد تحديث `.env`، جرب:

```bash
# اختبار الاتصال
npx prisma db pull

# إذا نجح، شغّل seed
npm run prisma:seed
```

