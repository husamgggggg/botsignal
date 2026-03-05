# حل مشكلة أمر Seed

## المشكلة

عند تشغيل `npx prisma seed`، يظهر الخطأ:
```
! Unknown command "seed"
```

## الحل

Prisma لا يدعم الأمر `seed` مباشرة. يجب استخدام `npm run` أو `ts-node` مباشرة.

### الطريقة 1: استخدام npm run (الأفضل)

```bash
cd apps/api_nest
npm run prisma:seed
```

### الطريقة 2: استخدام ts-node مباشرة

```bash
cd apps/api_nest
npx ts-node prisma/seed.ts
```

### الطريقة 3: استخدام node مع ts-node/register

```bash
cd apps/api_nest
node --loader ts-node/esm prisma/seed.ts
```

## ملاحظة

الأمر `prisma:seed` في `package.json` يعمل بشكل صحيح:
```json
"prisma:seed": "ts-node prisma/seed.ts"
```

استخدم `npm run prisma:seed` بدلاً من `npx prisma seed`.

