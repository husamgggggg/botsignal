# إشارات OANDA عبر التلجرام (OANDA Telegram Signals)

مشروع Python جاهز للإنتاج لسحب بيانات السوق من OANDA v20 وإرسال تحليلات التداول كتنبيهات عبر Telegram، باستخدام عدة استراتيجيات تحليل فني (EMA, MACD, Price Action, Advanced Multi-Indicator).

## 📋 نظرة عامة

هذا البوت يجلب بيانات الشموع (OHLC candles) بشكل دوري من OANDA v20 REST API، يحللها وفق الاستراتيجية المختارة، ثم يرسل إشارات التداول (BUY / SELL / NO_TRADE) إلى Telegram.

**مهم:** البوت لا ينفّذ أي صفقات، بل يرسل إشارات فقط. قرار الدخول مسؤوليتك بالكامل.

## 🏗️ هيكلة المشروع (داخل مجلد `bot`)

```text
bot/
├── src/
│   ├── main.py              # نقطة الدخول الرئيسية
│   ├── config.py            # إعدادات OANDA والاستراتيجية
│   ├── clients/
│   │   └── oanda.py         # عميل OANDA API
│   ├── indicators/          # المؤشرات (EMA, RSI, MACD, Support/Resistance, Price Action)
│   ├── strategies/          # الاستراتيجيات (EMA Bounce, MACD, Price Action, Advanced)
│   ├── engine/
│   │   ├── runner.py        # محرك التحليل الرئيسي
│   │   └── state.py         # إدارة الحالة
│   ├── notifier/
│   │   └── telegram.py      # إرسال التنبيهات عبر Telegram
│   └── utils/
│       ├── logging.py       # إعدادات السجلات
│       └── retry.py         # منطق إعادة المحاولة
├── tests/                   # اختبارات المؤشرات والاستراتيجيات
├── requirements.txt         # مكتبات Python
├── .env.example             # مثال ملف الإعدادات
├── Dockerfile               # لتشغيل البوت داخل Docker
├── docker-compose.yml       # لتشغيل البوت عبر docker-compose
└── README.md                # هذا الملف
```

## 📦 المتطلبات

- Python 3.11 أو أحدث
- حساب OANDA (practice أو live)
- Bot على Telegram + Chat ID

## 🚀 التثبيت والتشغيل محلياً

```bash
cd bot
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env  # أو copy على Windows
```

حرّر ملف `.env` وضع بياناتك:

```env
OANDA_ENV=practice
OANDA_ACCESS_TOKEN=your_oanda_token_here
INSTRUMENTS=EUR_USD,AUD_JPY,USD_JPY,EUR_JPY,AUD_CAD
GRANULARITY=M1
CANDLE_COUNT=200
STRATEGY_TYPE=advanced  # advanced, ema_bounce, macd, price_action

INTERVAL_SECONDS=60
COOLDOWN_SECONDS=60

TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
LOG_LEVEL=INFO
```

ثم شغّل البوت:

```bash
python -m src.main
```

## 🐳 تشغيل عبر Docker

```bash
docker build -t oanda-bot:latest .
docker-compose up -d
```

سيعمل البوت في الخلفية ويرسل إشارات إلى Telegram.

## 🧠 الاستراتيجيات باختصار

- **Advanced Multi-Indicator** (الافتراضية): تجمع بين MACD + RSI + EMA10/20/50 + دعم/مقاومة + Price Action، وتتطلب 4 مؤشرات على الأقل لتوليد إشارة، مع درجة ثقة 75–100٪.
- **EMA Support Bounce**: دخول عند ارتداد السعر من دعم EMA10 في ترند صاعد، مع فلتر EMA50 و RSI.
- **MACD Crossover**: دخول عند اكتمال شروط MACD (فوق/تحت خط الصفر + اتجاه الهيستوجرام + شمعة تأكيد).
- **Price Action + Support/Resistance**: دخول عند ظهور نمط شمعة قوي عند مستوى دعم/مقاومة مهم.

يمكن اختيار الاستراتيجية عبر متغير `STRATEGY_TYPE` في `.env`.

## 🧪 الاختبارات

```bash
pytest tests/
```

## 🔐 ملاحظات أمان

- لا ترفع ملف `.env` إلى Git.
- جرّب دائماً على حساب practice قبل الانتقال للحساب الحقيقي.


