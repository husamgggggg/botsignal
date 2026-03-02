# Web Setup Guide

This guide explains how to run the app as a website.

## Prerequisites

- Flutter SDK 3.0+
- Node.js 18+ (for API server)
- Modern web browser (Chrome, Firefox, Edge, Safari)

## Step 1: Start API Server

Before running the website, make sure the API server is running:

```bash
cd apps/api_nest
npm install
npm run start:dev
```

Server will run on: `http://localhost:3000`

## Step 2: Run Website in Development Mode

```bash
cd apps/mobile_flutter
flutter pub get
flutter run -d chrome
```

Or run on a specific browser:

```bash
# Chrome
flutter run -d chrome

# Edge
flutter run -d edge

# Firefox
flutter run -d web-server --web-port=8080
```

## Step 3: Build Website for Production

To create a production build:

```bash
cd apps/mobile_flutter
flutter build web
```

Built files will be in: `build/web/`

## Step 4: Deploy Website

### Option 1: Using Flutter Web Server

```bash
cd build/web
python -m http.server 8080
```

Then open: `http://localhost:8080`

### Option 2: Using Node.js serve

```bash
npm install -g serve
cd build/web
serve -s .
```

### Option 3: Deploy to GitHub Pages

1. Push `build/web` folder to GitHub
2. Enable GitHub Pages in repository settings
3. Select `build/web` as source folder

### Option 4: Deploy to Firebase Hosting

```bash
npm install -g firebase-tools
firebase login
firebase init hosting
# Select build/web as publish directory
firebase deploy
```

### Option 5: Deploy to Netlify

1. Drag and drop `build/web` folder to Netlify
2. Or use Netlify CLI:

```bash
npm install -g netlify-cli
cd build/web
netlify deploy --prod
```

## Step 5: Configure API URL for Production

Before deploying, make sure to update the API URL in `lib/core/config/app_config.dart`:

```dart
static String apiBaseUrl = 'https://your-api-domain.com';
```

Or use environment variables:

```dart
static String apiBaseUrl = 
    const String.fromEnvironment('API_URL', defaultValue: 'http://localhost:3000');
```

Then when building:

```bash
flutter build web --dart-define=API_URL=https://your-api-domain.com
```

## Web-Supported Features

✅ All core features work
✅ Arabic RTL support
✅ Dark theme
✅ Platform selection
✅ Account verification
✅ Signals display
✅ Risk calculator
✅ Settings

## Important Notes

1. **CORS**: Make sure API server supports CORS for web requests
2. **HTTPS**: Always use HTTPS in production
3. **PWA**: Website supports PWA and can be installed as an app
4. **Storage**: Uses LocalStorage on web instead of SharedPreferences

## Troubleshooting

### Issue: Buttons don't appear
- Make sure to reload the page (Ctrl+R)
- Check Console for errors

### Issue: Can't connect to API
- Verify API is running on `http://localhost:3000`
- Check CORS settings in API
- In production, make sure to update `apiBaseUrl`

### Issue: Errors in Console
- Open DevTools (F12)
- Check Console tab
- Check Network tab for failed requests

## Converting to App Later

After confirming the website works correctly, you can:

1. **Android**: `flutter build apk` or `flutter build appbundle`
2. **iOS**: `flutter build ios`
3. **Windows**: `flutter build windows`
4. **macOS**: `flutter build macos`

All features will work the same way!

