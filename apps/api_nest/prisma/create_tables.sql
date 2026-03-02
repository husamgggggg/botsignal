-- ============================================
-- إنشاء قاعدة البيانات والجداول يدوياً
-- ============================================

-- 1. إنشاء قاعدة البيانات (إذا لم تكن موجودة)
-- قم بتشغيل هذا الأمر من قاعدة بيانات postgres أو أي قاعدة بيانات أخرى
-- CREATE DATABASE botsignal_db;

-- 2. الاتصال بقاعدة البيانات botsignal_db
-- \c botsignal_db;

-- ============================================
-- إنشاء الأنواع (Enums)
-- ============================================

-- نوع المنصة
CREATE TYPE "Platform" AS ENUM ('QUOTEX', 'POCKET_OPTION');

-- نوع الاتجاه
CREATE TYPE "Direction" AS ENUM ('CALL', 'PUT');

-- نوع حالة الأخبار
CREATE TYPE "NewsStatus" AS ENUM ('SAFE', 'WARNING', 'BLOCKED');

-- نوع حالة الحساب
CREATE TYPE "AccountStatus" AS ENUM ('REGISTERED', 'NO_DEPOSIT', 'DEPOSITED');

-- ============================================
-- إنشاء الجداول
-- ============================================

-- جدول الأجهزة
CREATE TABLE "devices" (
    "id" TEXT NOT NULL,
    "deviceId" TEXT NOT NULL,
    "fcmToken" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "lastSeenAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "devices_pkey" PRIMARY KEY ("id")
);

-- جدول الحسابات
CREATE TABLE "accounts" (
    "id" TEXT NOT NULL,
    "platform" "Platform" NOT NULL,
    "accountId" TEXT NOT NULL,
    "status" "AccountStatus" NOT NULL DEFAULT 'REGISTERED',
    "lastDepositAmount" DOUBLE PRECISION,
    "lastDepositAt" TIMESTAMP(3),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "accounts_pkey" PRIMARY KEY ("id")
);

-- جدول ربط الأجهزة بالحسابات
CREATE TABLE "device_accounts" (
    "id" TEXT NOT NULL,
    "deviceId" TEXT NOT NULL,
    "accountId" TEXT NOT NULL,
    "linkedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "device_accounts_pkey" PRIMARY KEY ("id")
);

-- جدول أحداث Postback
CREATE TABLE "postback_events" (
    "id" TEXT NOT NULL,
    "platform" "Platform" NOT NULL,
    "eventType" TEXT NOT NULL,
    "payload" JSONB NOT NULL,
    "receivedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "postback_events_pkey" PRIMARY KEY ("id")
);

-- جدول الإشارات
CREATE TABLE "signals" (
    "id" TEXT NOT NULL,
    "platform" "Platform",
    "asset" TEXT NOT NULL,
    "direction" "Direction" NOT NULL,
    "expirySeconds" INTEGER NOT NULL,
    "confidence" INTEGER NOT NULL,
    "newsStatus" "NewsStatus" NOT NULL DEFAULT 'SAFE',
    "active" BOOLEAN NOT NULL DEFAULT true,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "signals_pkey" PRIMARY KEY ("id")
);

-- جدول سجل الإشعارات
CREATE TABLE "notifications_log" (
    "id" TEXT NOT NULL,
    "signalId" TEXT NOT NULL,
    "sentAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "fcmResponse" JSONB,

    CONSTRAINT "notifications_log_pkey" PRIMARY KEY ("id")
);

-- ============================================
-- إنشاء الفهارس الفريدة (Unique Indexes)
-- ============================================

CREATE UNIQUE INDEX "devices_deviceId_key" ON "devices"("deviceId");

CREATE UNIQUE INDEX "accounts_platform_accountId_key" ON "accounts"("platform", "accountId");

CREATE UNIQUE INDEX "device_accounts_deviceId_accountId_key" ON "device_accounts"("deviceId", "accountId");

-- ============================================
-- إنشاء المفاتيح الخارجية (Foreign Keys)
-- ============================================

ALTER TABLE "device_accounts" ADD CONSTRAINT "device_accounts_deviceId_fkey" FOREIGN KEY ("deviceId") REFERENCES "devices"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "device_accounts" ADD CONSTRAINT "device_accounts_accountId_fkey" FOREIGN KEY ("accountId") REFERENCES "accounts"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "notifications_log" ADD CONSTRAINT "notifications_log_signalId_fkey" FOREIGN KEY ("signalId") REFERENCES "signals"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- ============================================
-- إنشاء الفهارس للأداء (Indexes)
-- ============================================

CREATE INDEX "devices_deviceId_idx" ON "devices"("deviceId");
CREATE INDEX "accounts_platform_accountId_idx" ON "accounts"("platform", "accountId");
CREATE INDEX "accounts_status_idx" ON "accounts"("status");
CREATE INDEX "signals_active_idx" ON "signals"("active");
CREATE INDEX "signals_createdAt_idx" ON "signals"("createdAt");
CREATE INDEX "postback_events_receivedAt_idx" ON "postback_events"("receivedAt");

-- ============================================
-- تم الانتهاء
-- ============================================
-- الآن يمكنك تشغيل Prisma migrations أو seed البيانات
-- ============================================

