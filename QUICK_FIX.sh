#!/bin/bash
# سكريبت سريع لإصلاح مشكلة التثبيت

echo "🔧 إصلاح مشكلة تثبيت npm..."

# الانتقال إلى مجلد api_nest
cd apps/api_nest

# حذف node_modules القديم
echo "🗑️  حذف node_modules القديم..."
rm -rf node_modules
rm -f package-lock.json

# تنظيف npm cache
echo "🧹 تنظيف npm cache..."
npm cache clean --force

# تثبيت المكتبات
echo "📦 تثبيت المكتبات..."
npm install

# التحقق من التثبيت
echo "✅ التحقق من التثبيت..."
if [ -d "node_modules" ]; then
    echo "✅ node_modules موجود"
    npx prisma --version
    npx nest --version
else
    echo "❌ فشل التثبيت"
    exit 1
fi

echo "✨ تم الانتهاء! الآن يمكنك تشغيل:"
echo "   npx prisma generate"
echo "   npx prisma migrate dev"
echo "   npx prisma seed"
echo "   npx nest start --watch"

