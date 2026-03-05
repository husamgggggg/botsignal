# ⚡ دليل النشر السريع

## 🚀 النشر السريع على Linux Server

### الخطوات الأساسية:

```bash
# 1. رفع الملفات إلى السيرفر (استخدم SCP أو Git)
scp -r . username@server-ip:/opt/oanda-telegram-bot

# 2. الاتصال بالسيرفر
ssh username@server-ip

# 3. الانتقال إلى المجلد
cd /opt/oanda-telegram-bot

# 4. تشغيل سكريبت النشر
chmod +x deploy.sh
./deploy.sh

# 5. إعداد ملف .env
nano .env
# (أضف جميع المتغيرات المطلوبة)

# 6. إعداد systemd service
sudo cp oanda-bot.service /etc/systemd/system/
sudo nano /etc/systemd/system/oanda-bot.service
# (عدّل YOUR_USERNAME إلى اسم المستخدم الخاص بك)

# 7. تشغيل الخدمة
sudo systemctl daemon-reload
sudo systemctl enable oanda-bot
sudo systemctl start oanda-bot

# 8. التحقق من الحالة
sudo systemctl status oanda-bot
```

## 🐳 النشر باستخدام Docker

```bash
# 1. بناء الصورة
docker build -t oanda-bot:latest .

# 2. تشغيل الحاوية
docker-compose up -d

# 3. عرض السجلات
docker-compose logs -f
```

## 📋 قائمة التحقق

- [ ] Python 3.11+ مثبت
- [ ] ملف `.env` مكتمل
- [ ] تم تشغيل `deploy.sh`
- [ ] الخدمة تعمل (`systemctl status oanda-bot`)
- [ ] تم إرسال رسالة اختبار على Telegram

## 🔍 عرض السجلات

```bash
# systemd
sudo journalctl -u oanda-bot -f

# Docker
docker-compose logs -f
```

## 🛑 إيقاف/إعادة التشغيل

```bash
# systemd
sudo systemctl stop oanda-bot
sudo systemctl start oanda-bot
sudo systemctl restart oanda-bot

# Docker
docker-compose stop
docker-compose start
docker-compose restart
```

---

**للمزيد من التفاصيل، راجع `DEPLOYMENT.md`**

