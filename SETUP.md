# Complete Setup Guide

This guide will help you set up and run the entire Binary Options Signals app locally.

## Prerequisites

- Node.js 18+ installed
- Flutter 3.0+ installed
- Docker & Docker Compose installed
- PostgreSQL (or use Docker Compose)

## Step 1: Start Database

```bash
docker-compose up -d postgres
```

Wait a few seconds for PostgreSQL to be ready.

## Step 2: Setup Backend

```bash
cd apps/api_nest

# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Edit .env and set:
# - DATABASE_URL (should match docker-compose.yml)
# - JWT_SECRET (generate a random string)
# - ADMIN_API_KEY (generate a random string)
# - POSTBACK_SECRET (generate a random string)
# - Firebase credentials (optional for MVP)

# Generate Prisma client
npm run prisma:generate

# Run migrations
npm run prisma:migrate

# Seed database with test data
npm run prisma:seed

# Start development server
npm run start:dev
```

Backend should now be running at: http://localhost:3000
Swagger docs: http://localhost:3000/docs

## Step 3: Setup Flutter App

```bash
cd apps/mobile_flutter

# Install dependencies
flutter pub get

# For Android: Configure API base URL
# Edit lib/main.dart or use SharedPreferences to set API URL
# For Android emulator: http://10.0.2.2:3000
# For iOS simulator: http://localhost:3000
# For physical device: http://YOUR_COMPUTER_IP:3000

# Run the app
flutter run
```

## Step 4: Test the Flow

1. **Open the app** - It should show platform selection
2. **Select a platform** (e.g., Quotex)
3. **Enter test account ID**: `TEST_ACTIVE_123`
4. **Verify** - Should show "VERIFIED_ACTIVE" and unlock signals
5. **View signals** - Should see seeded signals

### Test Different Statuses

- `TEST_ACTIVE_123` → VERIFIED_ACTIVE (full access)
- `TEST_NO_DEPOSIT_456` → VERIFIED_NO_DEPOSIT (deposit required)
- Any other ID → NOT_UNDER_TEAM (register required)

## Step 5: Test Postback (Optional)

Simulate a postback event:

```bash
# Registration event
curl "http://localhost:3000/api/postback/quotex?event_type=registration&click_id=NEW_USER_789&secret=your-postback-secret"

# Deposit event
curl "http://localhost:3000/api/postback/quotex?event_type=deposit&click_id=NEW_USER_789&deposit_amount=50&secret=your-postback-secret"
```

Then verify the account in the app with `NEW_USER_789`.

## Step 6: Create Signal (Admin)

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

This will create a signal and send push notifications to all verified active devices.

## Troubleshooting

### Database Connection Issues
- Make sure Docker Compose is running: `docker-compose ps`
- Check PostgreSQL logs: `docker-compose logs postgres`
- Verify DATABASE_URL in `.env` matches docker-compose.yml

### Flutter API Connection Issues
- **Android Emulator**: Use `http://10.0.2.2:3000` instead of `localhost`
- **iOS Simulator**: `http://localhost:3000` should work
- **Physical Device**: Use your computer's local IP (e.g., `http://192.168.1.100:3000`)
- Check backend is running: `curl http://localhost:3000/api/platforms`

### Push Notifications Not Working
- Firebase setup is optional for MVP
- If not configured, notifications will be logged but not sent
- Check backend logs for FCM errors

## Environment Variables Reference

### Backend (.env)
```env
DATABASE_URL="postgresql://botsignal:botsignal_dev_password@localhost:5432/botsignal_db?schema=public"
JWT_SECRET="your-super-secret-jwt-key"
JWT_EXPIRES_IN="30d"
PORT=3000
NODE_ENV=development
ADMIN_API_KEY="your-admin-api-key"
POSTBACK_SECRET="your-postback-secret"
POSTBACK_ALLOWED_IPS="127.0.0.1,::1"
FIREBASE_PROJECT_ID=""
FIREBASE_PRIVATE_KEY=""
FIREBASE_CLIENT_EMAIL=""
QUOTEX_AFFILIATE_URL="https://broker.quotex.io/register?affiliate_id=YOUR_ID"
POCKET_OPTION_AFFILIATE_URL="https://pocketoption.com/register?affiliate_id=YOUR_ID"
QUOTEX_DEEP_LINK="quotex://"
POCKET_OPTION_DEEP_LINK="pocketoption://"
```

### Flutter
No `.env` file needed. API base URL is configured in code or via SharedPreferences.

## Next Steps

1. Configure Firebase for push notifications
2. Set up production database
3. Configure affiliate links
4. Deploy backend to production
5. Build and deploy mobile app

