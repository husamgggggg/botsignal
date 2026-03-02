# حل مشكلة تثبيت المكتبات

## المشكلة

عند تشغيل `npm run prisma:generate` أو `npm run prisma:seed`، يظهر الخطأ:
```
'prisma' is not recognized as an internal or external command
'ts-node' is not recognized as an internal or external command
```

## الحل

المكتبات لم يتم تثبيتها بعد. يجب تثبيت جميع المكتبات أولاً.

### الخطوة 1: تثبيت المكتبات

```bash
cd apps/api_nest
npm install
```

انتظر حتى ينتهي التثبيت (قد يستغرق بضع دقائق).

### الخطوة 2: التحقق من التثبيت

بعد انتهاء `npm install`، جرب:

```bash
# التحقق من Prisma
npx prisma --version

# التحقق من ts-node
npx ts-node --version
```

### الخطوة 3: تشغيل الأوامر

الآن يمكنك تشغيل:

```bash
# إنشاء Prisma Client
npm run prisma:generate

# ملء البيانات التجريبية
npm run prisma:seed
```

## إذا استمرت المشكلة

### الحل البديل: استخدام npx

إذا لم تعمل الأوامر، استخدم `npx` مباشرة:

```bash
# بدلاً من npm run prisma:generate
npx prisma generate

# بدلاً من npm run prisma:seed
npx ts-node prisma/seed.ts
```

### التحقق من node_modules

تأكد من وجود مجلد `node_modules`:

```bash
ls node_modules
# أو على Windows
dir node_modules
```

إذا لم يكن موجوداً، قم بتشغيل `npm install` مرة أخرى.

### تنظيف وإعادة التثبيت

إذا استمرت المشكلة:

```bash
# حذف node_modules و package-lock.json
rm -rf node_modules package-lock.json

# إعادة التثبيت
npm install
```

## ملاحظات

- تأكد من أنك في المجلد الصحيح: `apps/api_nest`
- تأكد من أن Node.js مثبت: `node --version`
- تأكد من أن npm مثبت: `npm --version`

