# حل مشاكل الاتصال بقاعدة البيانات

## مشكلة: فشل المصادقة (password authentication failed)

إذا ظهرت رسالة الخطأ:
```
password authentication failed for user "botsignal"
```

### الحلول:

#### 1. تأكد من تشغيل PostgreSQL Container

```bash
docker-compose ps
```

يجب أن ترى `botsignal-postgres` في حالة "Up". إذا لم يكن كذلك:

```bash
docker-compose up -d postgres
```

#### 2. تحقق من كلمة المرور الصحيحة

من ملف `docker-compose.yml`، كلمة المرور الافتراضية هي:
- **Username**: `botsignal`
- **Password**: `botsignal_dev_password`
- **Database**: `botsignal_db`

**في pgAdmin، تأكد من:**
- Username: `botsignal`
- Password: `botsignal_dev_password` (بدون مسافات إضافية)
- ✅ **Save password** مفعل

#### 3. إعادة تعيين كلمة المرور (إذا لزم الأمر)

إذا كنت متأكداً من أن كلمة المرور صحيحة ولكنها لا تزال لا تعمل:

**الطريقة 1: إعادة إنشاء Container**
```bash
# إيقاف وإزالة Container
docker-compose down -v

# إعادة التشغيل
docker-compose up -d postgres

# انتظر 5-10 ثوانٍ ثم جرب الاتصال مرة أخرى
```

**الطريقة 2: تغيير كلمة المرور يدوياً**
```bash
# الدخول إلى Container
docker exec -it botsignal-postgres psql -U botsignal -d botsignal_db

# تغيير كلمة المرور
ALTER USER botsignal WITH PASSWORD 'botsignal_dev_password';
\q
```

#### 4. التحقق من الاتصال من سطر الأوامر

جرب الاتصال مباشرة من Terminal:

```bash
# على Windows (Git Bash أو PowerShell)
docker exec -it botsignal-postgres psql -U botsignal -d botsignal_db

# إذا نجح، يجب أن ترى:
# botsignal_db=#
```

إذا نجح من سطر الأوامر ولكن لا يزال يفشل في pgAdmin، المشكلة في إعدادات pgAdmin.

#### 5. التحقق من إعدادات pgAdmin

في pgAdmin، تأكد من:

1. **Host name/address**: `localhost` (وليس `127.0.0.1`)
2. **Port**: `5432`
3. **Maintenance database**: `botsignal_db`
4. **Username**: `botsignal` (حساس لحالة الأحرف)
5. **Password**: `botsignal_dev_password` (بدون مسافات)
6. ✅ **Save password** مفعل

#### 6. حذف الاتصال القديم وإعادة إنشائه

إذا كان لديك اتصال قديم:

1. في pgAdmin، انقر بزر الماوس الأيمن على "Botsignal Local"
2. اختر "Delete/Drop"
3. أنشئ اتصالاً جديداً من الصفر

#### 7. التحقق من سجلات PostgreSQL

```bash
docker-compose logs postgres
```

ابحث عن أخطاء أو رسائل تتعلق بالمصادقة.

### حل بديل: استخدام بيانات مختلفة

إذا استمرت المشكلة، يمكنك تغيير بيانات الاعتماد في `docker-compose.yml`:

```yaml
environment:
  POSTGRES_USER: postgres
  POSTGRES_PASSWORD: postgres
  POSTGRES_DB: botsignal_db
```

ثم:
```bash
docker-compose down -v
docker-compose up -d postgres
```

وتحديث `apps/api_nest/.env`:
```
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/botsignal_db?schema=public"
```

## مشكلة: قاعدة البيانات غير موجودة

إذا ظهرت رسالة "database does not exist":

```bash
cd apps/api_nest
npm run prisma:migrate
```

## مشكلة: Port 5432 مستخدم بالفعل

إذا ظهرت رسالة "port is already allocated":

1. تحقق من التطبيقات الأخرى التي تستخدم PostgreSQL:
   ```bash
   netstat -ano | findstr :5432
   ```

2. إما أوقف التطبيق الآخر، أو غيّر المنفذ في `docker-compose.yml`:
   ```yaml
   ports:
     - "5433:5432"  # استخدم 5433 بدلاً من 5432
   ```

3. ثم حدّث `apps/api_nest/.env`:
   ```
   DATABASE_URL="postgresql://botsignal:botsignal_dev_password@localhost:5433/botsignal_db?schema=public"
   ```

## اختبار الاتصال السريع

```bash
# اختبار الاتصال
docker exec -it botsignal-postgres psql -U botsignal -d botsignal_db -c "SELECT version();"

# يجب أن ترى إصدار PostgreSQL
```

## نصائح إضافية

1. **انتظر قليلاً**: بعد تشغيل `docker-compose up -d postgres`، انتظر 5-10 ثوانٍ قبل محاولة الاتصال
2. **تحقق من الحالة**: استخدم `docker-compose ps` للتأكد من أن Container يعمل
3. **أعد المحاولة**: أحياناً pgAdmin يحتاج إلى إعادة المحاولة بعد فشل أولي

## إذا استمرت المشكلة

1. أعد تشغيل Docker Desktop
2. أعد تشغيل pgAdmin
3. تأكد من أن Docker Desktop يعمل بشكل صحيح
4. جرب الاتصال من تطبيق آخر (مثل DBeaver أو TablePlus)

