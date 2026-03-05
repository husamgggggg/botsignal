# حل مشكلة Flutter pub get - 429 Too Many Requests

## المشكلة

```
429 Too Many Requests trying to find package ffi at https://pub.flutter-io.cn.
```

هذا يعني أن Flutter يحاول استخدام mirror صيني وهناك حد للطلبات.

## الحلول

### الحل 1: الانتظار وإعادة المحاولة

```bash
# انتظر دقيقة ثم جرب مرة أخرى
flutter pub get
```

### الحل 2: تغيير Flutter Mirror

```bash
# إلغاء استخدام Mirror الصيني
export PUB_HOSTED_URL=https://pub.dev
export FLUTTER_STORAGE_BASE_URL=https://storage.googleapis.com

# ثم جرب مرة أخرى
flutter pub get
```

### الحل 3: على Windows (PowerShell)

```powershell
$env:PUB_HOSTED_URL="https://pub.dev"
$env:FLUTTER_STORAGE_BASE_URL="https://storage.googleapis.com"
flutter pub get
```

### الحل 4: على Windows (CMD)

```cmd
set PUB_HOSTED_URL=https://pub.dev
set FLUTTER_STORAGE_BASE_URL=https://storage.googleapis.com
flutter pub get
```

### الحل 5: استخدام VPN أو تغيير DNS

إذا كنت في منطقة محظورة، قد تحتاج VPN.

### الحل 6: تنظيف وإعادة المحاولة

```bash
# تنظيف cache
flutter clean
flutter pub cache repair

# ثم جرب مرة أخرى
flutter pub get
```

## الحل الدائم

أضف هذه المتغيرات إلى ملف `.bashrc` أو `.zshrc`:

```bash
export PUB_HOSTED_URL=https://pub.dev
export FLUTTER_STORAGE_BASE_URL=https://storage.googleapis.com
```

ثم:
```bash
source ~/.bashrc  # أو source ~/.zshrc
```

## ملاحظة

أنت بالفعل في `apps/mobile_flutter`، لا حاجة لـ `cd apps/mobile_flutter` مرة أخرى.

