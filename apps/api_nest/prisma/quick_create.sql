-- أوامر سريعة لإنشاء قاعدة البيانات والجداول
-- انسخ والصق في pgAdmin Query Tool

-- إنشاء قاعدة البيانات (شغلها من قاعدة postgres)
CREATE DATABASE botsignal_db;

-- بعد ذلك، اتصل بقاعدة botsignal_db وشغّل الأوامر التالية:

-- إنشاء الأنواع
CREATE TYPE "Platform" AS ENUM ('QUOTEX', 'POCKET_OPTION');
CREATE TYPE "Direction" AS ENUM ('CALL', 'PUT');
CREATE TYPE "NewsStatus" AS ENUM ('SAFE', 'WARNING', 'BLOCKED');
CREATE TYPE "AccountStatus" AS ENUM ('REGISTERED', 'NO_DEPOSIT', 'DEPOSITED');

-- إنشاء الجداول
CREATE TABLE "devices" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "deviceId" TEXT NOT NULL UNIQUE,
    "fcmToken" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "lastSeenAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL
);

CREATE TABLE "accounts" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "platform" "Platform" NOT NULL,
    "accountId" TEXT NOT NULL,
    "status" "AccountStatus" NOT NULL DEFAULT 'REGISTERED',
    "lastDepositAmount" DOUBLE PRECISION,
    "lastDepositAt" TIMESTAMP(3),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    UNIQUE("platform", "accountId")
);

CREATE TABLE "device_accounts" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "deviceId" TEXT NOT NULL,
    "accountId" TEXT NOT NULL,
    "linkedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE("deviceId", "accountId"),
    FOREIGN KEY ("deviceId") REFERENCES "devices"("id") ON DELETE CASCADE,
    FOREIGN KEY ("accountId") REFERENCES "accounts"("id") ON DELETE CASCADE
);

CREATE TABLE "postback_events" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "platform" "Platform" NOT NULL,
    "eventType" TEXT NOT NULL,
    "payload" JSONB NOT NULL,
    "receivedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "signals" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "platform" "Platform",
    "asset" TEXT NOT NULL,
    "direction" "Direction" NOT NULL,
    "expirySeconds" INTEGER NOT NULL,
    "confidence" INTEGER NOT NULL,
    "newsStatus" "NewsStatus" NOT NULL DEFAULT 'SAFE',
    "active" BOOLEAN NOT NULL DEFAULT true,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "notifications_log" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "signalId" TEXT NOT NULL,
    "sentAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "fcmResponse" JSONB,
    FOREIGN KEY ("signalId") REFERENCES "signals"("id") ON DELETE CASCADE
);

-- إنشاء الفهارس
CREATE INDEX "accounts_status_idx" ON "accounts"("status");
CREATE INDEX "signals_active_idx" ON "signals"("active");
CREATE INDEX "signals_createdAt_idx" ON "signals"("createdAt");

