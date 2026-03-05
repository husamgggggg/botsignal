# حل مشكلة تثبيت npm

## المشكلة

عند تشغيل `npm install` في `apps/api_nest`، يظهر الخطأ:
```
EEXIST: file already exists, symlink
```

والمكتبات لا تُثبت في المجلد الصحيح.

## الحل السريع

### الخطوة 1: حذف symlink الموجود

```bash
# من المجلد الجذر
cd ~/Desktop/botsignal

# حذف symlink الموجود
rm -rf node_modules/api-nest

# أو على Windows PowerShell
Remove-Item -Recurse -Force node_modules\api-nest
```

### الخطوة 2: حذف node_modules في الجذر (اختياري)

إذا كنت لا تحتاج workspaces:

```bash
# من المجلد الجذر
rm -rf node_modules
rm -f package-lock.json
```

### الخطوة 3: تثبيت المكتبات في apps/api_nest

```bash
cd apps/api_nest

# حذف node_modules القديم إن وجد
rm -rf node_modules
rm -f package-lock.json

# تثبيت المكتبات
npm install
```

### الخطوة 4: استخدام npx بدلاً من npm run

إذا استمرت المشكلة، استخدم `npx` مباشرة:

```bash
cd apps/api_nest

# بدلاً من npm run prisma:generate
npx prisma generate

# بدلاً من npm run prisma:migrate
npx prisma migrate dev

# بدلاً من npm run prisma:seed
npx ts-node prisma/seed.ts

# بدلاً من npm run start:dev
npx nest start --watch
```

## الحل البديل: تحديث package.json scripts

يمكنك تحديث `apps/api_nest/package.json` لاستخدام `npx`:

```json
{
  "scripts": {
    "prisma:generate": "npx prisma generate",
    "prisma:migrate": "npx prisma migrate dev",
    "prisma:seed": "npx ts-node prisma/seed.ts",
    "start:dev": "npx nest start --watch"
  }
}
```

## التحقق من التثبيت

بعد `npm install`، تحقق من:

```bash
# التحقق من وجود node_modules
ls node_modules | head -5

# التحقق من Prisma
npx prisma --version

# التحقق من NestJS
npx nest --version
```

## إذا استمرت المشكلة

### 1. تنظيف كامل وإعادة تثبيت

```bash
cd apps/api_nest

# حذف كل شيء
rm -rf node_modules package-lock.json

# تنظيف npm cache
npm cache clean --force

# إعادة التثبيت
npm install
```

### 2. استخدام yarn بدلاً من npm

```bash
cd apps/api_nest

# تثبيت yarn (إذا لم يكن مثبتاً)
npm install -g yarn

# تثبيت المكتبات
yarn install

# تشغيل الأوامر
yarn prisma:generate
yarn prisma:seed
yarn start:dev
```

### 3. التحقق من Node.js و npm

```bash
# التحقق من الإصدارات
node --version  # يجب أن يكون 18+
npm --version   # يجب أن يكون 9+

# إذا كانت الإصدارات قديمة، قم بتحديثها
```

## ملاحظات مهمة

- تأكد من أنك في المجلد الصحيح: `apps/api_nest`
- لا تستخدم workspaces إذا لم تكن بحاجة إليها
- استخدم `npx` إذا كانت الأوامر لا تعمل مع `npm run`

