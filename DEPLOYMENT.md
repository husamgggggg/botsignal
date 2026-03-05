# 🚀 دليل رفع التطبيق إلى السيرفر

دليل شامل لرفع بوت OANDA Telegram Signals إلى السيرفر.

## 📋 المتطلبات الأساسية

- سيرفر Linux (Ubuntu 20.04+ أو Debian 11+ موصى به)
- Python 3.11 أو أحدث
- Git
- SSH access إلى السيرفر

---

## 🎯 الطريقة 1: النشر اليدوي (Manual Deployment)

### الخطوة 1: الاتصال بالسيرفر

```bash
ssh username@your-server-ip
```

### الخطوة 2: تثبيت المتطلبات الأساسية

```bash
# تحديث النظام
sudo apt update && sudo apt upgrade -y

# تثبيت Python و pip
sudo apt install python3.11 python3.11-venv python3-pip git -y
```

### الخطوة 3: رفع الملفات إلى السيرفر

#### أ) باستخدام Git (موصى به):

```bash
# على السيرفر
cd /opt
sudo git clone https://github.com/your-username/oanda-telegram-bot.git
cd oanda-telegram-bot
```

#### ب) باستخدام SCP (من جهازك المحلي):

```bash
# من جهازك المحلي (Windows)
scp -r C:\Users\it\ 021\Desktop\bot username@your-server-ip:/opt/oanda-telegram-bot
```

#### ج) باستخدام SFTP:

استخدم FileZilla أو WinSCP لرفع الملفات.

### الخطوة 4: إعداد البيئة الافتراضية

```bash
cd /opt/oanda-telegram-bot
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### الخطوة 5: إعداد ملف .env

```bash
# نسخ ملف المثال
cp .env.example .env

# تعديل الملف
nano .env
```

أضف جميع المتغيرات المطلوبة:
```env
OANDA_ENV=practice
OANDA_ACCESS_TOKEN=your_token_here
INSTRUMENTS=EUR_USD,GBP_USD,USD_JPY
GRANULARITY=M1
CANDLE_COUNT=200
STRATEGY_TYPE=advanced
INTERVAL_SECONDS=60
COOLDOWN_SECONDS=60
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
LOG_LEVEL=INFO
```

### الخطوة 6: اختبار التطبيق

```bash
# تشغيل التطبيق يدوياً للتأكد من عمله
python -m src.main
```

اضغط `Ctrl+C` لإيقافه بعد التأكد من عمله.

### الخطوة 7: إعداد systemd Service

إنشاء ملف خدمة:

```bash
sudo nano /etc/systemd/system/oanda-bot.service
```

أضف المحتوى التالي:

```ini
[Unit]
Description=OANDA Telegram Signals Bot
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/opt/oanda-telegram-bot
Environment="PATH=/opt/oanda-telegram-bot/venv/bin"
ExecStart=/opt/oanda-telegram-bot/venv/bin/python -m src.main
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**ملاحظة:** استبدل `your-username` باسم المستخدم الخاص بك.

### الخطوة 8: تشغيل الخدمة

```bash
# إعادة تحميل systemd
sudo systemctl daemon-reload

# تفعيل الخدمة (لتبدأ تلقائياً عند إعادة التشغيل)
sudo systemctl enable oanda-bot

# بدء الخدمة
sudo systemctl start oanda-bot

# التحقق من الحالة
sudo systemctl status oanda-bot

# عرض السجلات
sudo journalctl -u oanda-bot -f
```

---

## 🐳 الطريقة 2: النشر باستخدام Docker (موصى به للإنتاج)

### الخطوة 1: إنشاء Dockerfile

تم إنشاء `Dockerfile` في المشروع.

### الخطوة 2: بناء الصورة

```bash
docker build -t oanda-bot:latest .
```

### الخطوة 3: تشغيل الحاوية

```bash
docker run -d \
  --name oanda-bot \
  --restart unless-stopped \
  --env-file .env \
  -v $(pwd)/state.json:/app/state.json \
  oanda-bot:latest
```

### الخطوة 4: إدارة الحاوية

```bash
# عرض السجلات
docker logs -f oanda-bot

# إيقاف الحاوية
docker stop oanda-bot

# بدء الحاوية
docker start oanda-bot

# إعادة تشغيل الحاوية
docker restart oanda-bot
```

---

## 🔄 التحديثات المستقبلية

### عند وجود تحديثات جديدة:

```bash
# 1. إيقاف الخدمة
sudo systemctl stop oanda-bot

# 2. سحب التحديثات (إذا كنت تستخدم Git)
cd /opt/oanda-telegram-bot
git pull

# أو رفع الملفات الجديدة يدوياً

# 3. تحديث التبعيات (إذا تغيرت)
source venv/bin/activate
pip install -r requirements.txt

# 4. إعادة تشغيل الخدمة
sudo systemctl start oanda-bot
```

---

## 📊 مراقبة التطبيق

### عرض السجلات:

```bash
# systemd
sudo journalctl -u oanda-bot -f --lines=100

# Docker
docker logs -f oanda-bot
```

### التحقق من الحالة:

```bash
# systemd
sudo systemctl status oanda-bot

# Docker
docker ps | grep oanda-bot
```

---

## 🛠️ استكشاف الأخطاء

### المشكلة: التطبيق لا يبدأ

```bash
# تحقق من السجلات
sudo journalctl -u oanda-bot -n 50

# تحقق من ملف .env
cat /opt/oanda-telegram-bot/.env

# تحقق من Python
which python3.11
python3.11 --version
```

### المشكلة: خطأ في الاتصال بـ OANDA

- تحقق من `OANDA_ACCESS_TOKEN` في ملف `.env`
- تحقق من `OANDA_ENV` (يجب أن يكون `practice` أو `live`)
- تحقق من اتصال الإنترنت

### المشكلة: خطأ في Telegram

- تحقق من `TELEGRAM_BOT_TOKEN`
- تحقق من `TELEGRAM_CHAT_ID`
- تأكد من أن البوت نشط على Telegram

---

## 🔒 الأمان

### 1. حماية ملف .env

```bash
chmod 600 /opt/oanda-telegram-bot/.env
```

### 2. استخدام مستخدم غير root

```bash
# إنشاء مستخدم جديد
sudo adduser oanda-bot

# نقل الملفات
sudo chown -R oanda-bot:oanda-bot /opt/oanda-telegram-bot
```

### 3. جدار الحماية

```bash
# السماح فقط بـ SSH
sudo ufw allow 22/tcp
sudo ufw enable
```

---

## 📝 ملاحظات مهمة

1. **لا ترفع ملف `.env` إلى Git** - احرص على إضافته إلى `.gitignore`
2. **احفظ نسخة احتياطية من `state.json`** - يحتوي على حالة التطبيق
3. **راقب استخدام الذاكرة** - التطبيق يعمل بشكل مستمر
4. **استخدم `screen` أو `tmux`** إذا كنت تريد تشغيله يدوياً بدون systemd

---

## ✅ قائمة التحقق قبل النشر

- [ ] Python 3.11+ مثبت
- [ ] جميع التبعيات مثبتة
- [ ] ملف `.env` مكتمل وصحيح
- [ ] تم اختبار التطبيق محلياً
- [ ] تم إعداد systemd service أو Docker
- [ ] الخدمة تعمل بشكل صحيح
- [ ] السجلات تظهر بدون أخطاء
- [ ] تم إرسال رسالة اختبار على Telegram

---

## 🆘 الدعم

إذا واجهت مشاكل، تحقق من:
1. السجلات (`journalctl` أو `docker logs`)
2. ملف `.env`
3. اتصال الإنترنت
4. حالة الخدمة (`systemctl status`)

