# Quick Reference Guide

## 🚀 Quick Commands

### Start Everything
```bash
# 1. Database
docker-compose up -d postgres

# 2. Backend (in apps/api_nest)
npm install && npm run prisma:generate && npm run prisma:migrate && npm run prisma:seed && npm run start:dev

# 3. Flutter (in apps/mobile_flutter)
flutter pub get && flutter run
```

## 🧪 Test Account IDs

- `TEST_ACTIVE_123` → Full access (VERIFIED_ACTIVE)
- `TEST_NO_DEPOSIT_456` → Deposit required (VERIFIED_NO_DEPOSIT)
- Any other → Register required (NOT_UNDER_TEAM)

## 📡 API Base URLs

- **Android Emulator**: `http://10.0.2.2:3000`
- **iOS Simulator**: `http://localhost:3000`
- **Physical Device**: `http://YOUR_COMPUTER_IP:3000`

## 🔑 Admin API Test

```bash
curl -X POST http://localhost:3000/api/admin/signals \
  -H "Content-Type: application/json" \
  -H "X-Admin-Api-Key: your-admin-api-key" \
  -d '{
    "platform": "QUOTEX",
    "asset": "EUR/USD",
    "direction": "CALL",
    "expirySeconds": 60,
    "confidence": 75,
    "newsStatus": "SAFE"
  }'
```

## 📨 Postback Test

```bash
# Registration
curl "http://localhost:3000/api/postback/quotex?event_type=registration&click_id=NEW_USER&secret=your-postback-secret"

# Deposit
curl "http://localhost:3000/api/postback/quotex?event_type=deposit&click_id=NEW_USER&deposit_amount=100&secret=your-postback-secret"
```

## 🔍 Check Status

- **Backend running**: `curl http://localhost:3000/api/platforms`
- **Database**: `docker-compose ps`
- **Swagger**: http://localhost:3000/docs

## 📱 App Routes

- `/platform-select` - Choose platform
- `/account-verify` - Enter account ID
- `/verify-result` - Verification status
- `/home` - Signals feed
- `/signal/:id` - Signal details
- `/risk-calculator` - Risk calculator
- `/settings` - Settings

## 🎨 Theme Colors

- Primary Black: `#000000`
- Neon Green: `#00FF41`
- Neon Blue: `#00D9FF`
- Dark Gray: `#1A1A1A`

## 🌐 Languages

- Arabic (ar) - Default, RTL
- English (en) - LTR

## ⚙️ Key Files

- Backend config: `apps/api_nest/.env`
- Database schema: `apps/api_nest/prisma/schema.prisma`
- Flutter theme: `apps/mobile_flutter/lib/core/theme/app_theme.dart`
- App router: `apps/mobile_flutter/lib/core/routing/app_router.dart`

