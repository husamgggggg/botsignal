# Binary Options Signals App

Production-ready "Signals Only" mobile app (Arabic-first, bold dark UI) for Binary Options signals.

## Project Structure

```
.
├── apps/
│   ├── mobile_flutter/     # Flutter mobile app
│   └── api_nest/           # NestJS backend API
├── docker-compose.yml      # Local development setup
└── README.md
```

## Tech Stack

- **Mobile**: Flutter (Dart) - Android + iOS
- **Backend**: Node.js + NestJS (TypeScript)
- **Database**: PostgreSQL with Prisma ORM
- **Push Notifications**: Firebase Cloud Messaging (FCM)
- **Auth**: Device-based authentication

## Quick Start

### Prerequisites

- Node.js 18+
- Flutter 3.0+
- Docker & Docker Compose
- PostgreSQL (or use Docker Compose)

### 1. Start Database

```bash
docker-compose up -d postgres
```

### 2. Setup Backend

```bash
cd apps/api_nest
npm install
cp .env.example .env
# Edit .env with your values
npm run prisma:generate
npm run prisma:migrate
npm run prisma:seed
npm run start:dev
```

Backend runs on: http://localhost:3000
API Docs: http://localhost:3000/docs

### 3. Setup Flutter App

```bash
cd apps/mobile_flutter
flutter pub get
# Copy .env.example to .env and configure
flutter run
```

## Environment Variables

See `.env.example` files in each app directory.

## Features

- ✅ Platform selection (Quotex, Pocket Option)
- ✅ Account verification via postback
- ✅ Signals feed (locked/unlocked based on status)
- ✅ Risk calculator
- ✅ Push notifications
- ✅ Arabic RTL support
- ✅ Dark bold theme

## Important Notes

- This app does NOT place trades
- Signals only - users must use broker apps/sites
- Monetization via affiliate tracking
- Registration verification via partner postback

## Documentation

- `SETUP.md` - Complete setup guide (English)
- `SETUP_AR.md` - دليل الإعداد الكامل (العربية)
- `PGADMIN_GUIDE_AR.md` - pgAdmin usage guide (Arabic)
- `PROJECT_SUMMARY.md` - Full feature overview (English)
- `PROJECT_SUMMARY_AR.md` - ملخص المشروع الكامل (العربية)
- `QUICK_REFERENCE.md` - Quick commands (English)
- `QUICK_REFERENCE_AR.md` - دليل المرجع السريع (العربية)

# botsignal
