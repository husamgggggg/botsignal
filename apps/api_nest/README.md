# Binary Options Signals API

NestJS backend API for the Binary Options Signals mobile app.

## Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your values
   ```

3. **Setup database:**
   ```bash
   # Make sure PostgreSQL is running (via Docker Compose)
   npm run prisma:generate
   npm run prisma:migrate
   npm run prisma:seed
   ```

4. **Run development server:**
   ```bash
   npm run start:dev
   ```

API will be available at: http://localhost:3000
Swagger docs: http://localhost:3000/docs

## Environment Variables

See `.env.example` for all required variables.

Key variables:
- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET` - Secret for JWT tokens
- `ADMIN_API_KEY` - API key for admin endpoints
- `POSTBACK_SECRET` - Secret for postback validation
- `FIREBASE_*` - Firebase credentials for push notifications

## API Endpoints

### Public
- `POST /api/auth/register` - Register device
- `POST /api/verify` - Verify account
- `GET /api/platforms` - Get platforms info

### Authenticated (Bearer token)
- `GET /api/signals` - Get signals (requires verified active account)
- `POST /api/auth/fcm-token` - Update FCM token

### Admin (X-Admin-Api-Key header)
- `POST /api/admin/signals` - Create signal

### Postback
- `GET /api/postback/quotex` - Quotex postback endpoint
- `GET /api/postback/pocket-option` - Pocket Option postback endpoint

## Testing Postback

You can test the postback endpoint with curl:

```bash
# Registration event
curl "http://localhost:3000/api/postback/quotex?event_type=registration&click_id=TEST_123&secret=your-postback-secret"

# Deposit event
curl "http://localhost:3000/api/postback/quotex?event_type=deposit&click_id=TEST_123&deposit_amount=100&secret=your-postback-secret"
```

