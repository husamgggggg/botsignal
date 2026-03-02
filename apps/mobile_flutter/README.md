# Binary Options Signals Mobile App

Flutter mobile app for Binary Options signals (Arabic-first, dark UI).

## Setup

1. **Install Flutter dependencies:**
   ```bash
   flutter pub get
   ```

2. **Configure Firebase:**
   - Add `google-services.json` (Android) to `android/app/`
   - Add `GoogleService-Info.plist` (iOS) to `ios/Runner/`
   - Or configure Firebase manually

3. **Configure API base URL:**
   - The app uses `http://localhost:3000` by default
   - For Android emulator, use `http://10.0.2.2:3000`
   - For iOS simulator, use `http://localhost:3000`
   - For physical device, use your computer's IP address

4. **Run the app:**
   ```bash
   flutter run
   ```

## Features

- ✅ Arabic RTL support (default language)
- ✅ Dark bold theme with neon accents
- ✅ Platform selection (Quotex, Pocket Option)
- ✅ Account verification flow
- ✅ Signals feed (locked/unlocked based on status)
- ✅ Risk calculator
- ✅ Push notifications (FCM)
- ✅ Settings (language, platform change, logout)

## Project Structure

```
lib/
├── core/
│   ├── config/          # App configuration
│   ├── localization/    # Arabic/English translations
│   ├── providers/       # Riverpod providers
│   ├── routing/         # GoRouter configuration
│   ├── services/        # API services
│   └── theme/           # Dark theme
├── features/
│   ├── home/           # Home screen with signals
│   ├── onboarding/     # Platform select, verify screens
│   ├── risk/           # Risk calculator
│   ├── settings/       # Settings screen
│   └── signals/        # Signal details
└── main.dart           # App entry point
```

## Testing

Use these test account IDs from the seeded data:
- `TEST_ACTIVE_123` (QUOTEX) - VERIFIED_ACTIVE
- `TEST_NO_DEPOSIT_456` (QUOTEX) - VERIFIED_NO_DEPOSIT

