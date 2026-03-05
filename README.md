# إشارات OANDA عبر التلجرام (OANDA Telegram Signals)

مشروع Python جاهز للإنتاج لسحب بيانات السوق من OANDA v20 وإرسال تحليلات التداول كتنبيهات عبر Telegram.

## 📋 نظرة عامة

هذا البوت يجلب بيانات الشموع (OHLC candles) بشكل دوري من OANDA v20 REST API، ويقوم بتحليلها باستخدام استراتيجية تقاطع EMA/RSI لتوليد إشارات تداول (BUY/SELL/NO_TRADE)، ثم يرسل تنبيهات عبر Telegram عند ظهور إشارة جديدة أو تغيير الإشارة.

**⚠️ تنبيه مهم:** هذا البوت **لا يقوم بتنفيذ أي أوامر تداول**. إنه يرسل إشارات تحليلية فقط للإعلام. يجب عليك اتخاذ قرارات التداول بنفسك.

## 🏗️ البنية المعمارية

```
oanda_telegram_signals/
├── src/
│   ├── main.py              # نقطة الدخول الرئيسية
│   ├── config.py            # إدارة الإعدادات
│   ├── clients/
│   │   └── oanda.py         # عميل OANDA API
│   ├── indicators/
│   │   ├── ema.py           # مؤشر المتوسط المتحرك الأسي (EMA)
│   │   └── rsi.py           # مؤشر القوة النسبية (RSI)
│   ├── strategies/
│   │   └── ema_rsi.py       # استراتيجية تقاطع EMA/RSI
│   ├── engine/
│   │   ├── runner.py        # محرك التحليل الرئيسي
│   │   └── state.py         # إدارة الحالة المستمرة
│   ├── notifier/
│   │   └── telegram.py      # إرسال التنبيهات عبر Telegram
│   └── utils/
│       ├── logging.py       # إعدادات السجلات
│       └── retry.py         # منطق إعادة المحاولة مع الانتظار التدريجي
├── tests/
│   ├── test_ema.py          # اختبارات EMA
│   ├── test_rsi.py          # اختبارات RSI
│   └── test_strategy.py     # اختبارات الاستراتيجية
├── requirements.txt         # التبعيات
├── .env.example            # مثال على ملف الإعدادات
└── README.md               # هذا الملف
```

## 📦 المتطلبات

- Python 3.11 أو أحدث
- حساب OANDA (practice أو live)
- Bot على Telegram
- Chat ID على Telegram

## 🚀 التثبيت

### 1. استنساخ المشروع

```bash
cd oanda_telegram_signals
```

### 2. إنشاء بيئة افتراضية (موصى به)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. تثبيت التبعيات

```bash
pip install -r requirements.txt
```

### 4. إعداد ملف الإعدادات

انسخ ملف `.env.example` إلى `.env` وقم بتعديل القيم:

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

## ⚙️ الإعداد

### 1. الحصول على رمز OANDA API

#### أ) إنشاء حساب OANDA:
1. انتقل إلى [OANDA](https://www.oanda.com/)
2. قم بإنشاء حساب جديد (يمكنك البدء بحساب practice مجاني)
3. قم بتسجيل الدخول إلى حسابك

#### ب) إنشاء API Token:
1. انتقل إلى قسم "Manage API Access" في إعدادات الحساب
2. انقر على "Generate API Token"
3. اختر الحساب (Practice أو Live) والفترة الزمنية
4. انسخ الرمز المولد وأضفه إلى `.env` كقيمة `OANDA_ACCESS_TOKEN`

**ملاحظة:** 
- للحساب التجريبي (Practice): استخدم `OANDA_ENV=practice`
- للحساب الحقيقي (Live): استخدم `OANDA_ENV=live` (⚠️ احذر: سيستخدم أموال حقيقية!)

### 2. إنشاء Bot على Telegram

#### أ) إنشاء Bot جديد:
1. افتح Telegram وابحث عن `@BotFather`
2. أرسل الأمر `/newbot`
3. اتبع التعليمات لإعطاء البوت اسم واسم مستخدم
4. احفظ الرمز المولد الذي يبدو مثل: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`

#### ب) الحصول على Chat ID:
1. ابحث عن `@userinfobot` على Telegram
2. أرسل رسالة إلى البوت
3. ستحصل على Chat ID الخاص بك (رقم مثل: `123456789`)
4. بدلاً من ذلك، يمكنك إرسال رسالة إلى البوت الخاص بك ثم زيارة:
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```
   ابحث عن `"chat":{"id":` للحصول على Chat ID

#### ج) إضافة القيم إلى `.env`:
```env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

### 3. تكوين ملف `.env`

عدّل ملف `.env` بالإعدادات المناسبة:

```env
# إعدادات OANDA
OANDA_ENV=practice
OANDA_ACCESS_TOKEN=your_oanda_token_here

# إعدادات التداول
INSTRUMENTS=EUR_USD,AUD_JPY,USD_JPY,EUR_JPY,AUD_CAD
GRANULARITY=M1
CANDLE_COUNT=200
STRATEGY_TYPE=advanced  # advanced (الأقوى), ema_bounce, macd, price_action

# إعدادات المحرك
INTERVAL_SECONDS=60
COOLDOWN_SECONDS=60
FORCE_DAILY_SUMMARY=false

# إعدادات Telegram
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

# مستوى السجلات
LOG_LEVEL=INFO
```

#### شرح المتغيرات:

- **OANDA_ENV**: البيئة (`practice` أو `live`)
- **OANDA_ACCESS_TOKEN**: رمز OANDA API
- **INSTRUMENTS**: أزواج العملات مفصولة بفواصل (مثال: `EUR_USD,GBP_USD,USD_JPY,EUR_JPY,AUD_CAD`)
- **GRANULARITY**: الإطار الزمني للشموع (يجب أن يكون `M1` فقط - البوت يعمل فقط على 1 دقيقة)
- **CANDLE_COUNT**: عدد الشموع المسترجعة للتحليل (200 موصى به - مطلوب 200 على الأقل للاستراتيجية المتقدمة)
- **STRATEGY_TYPE**: نوع الاستراتيجية (`advanced` - الافتراضي والأقوى, `ema_bounce`, `macd`, `price_action`)
- **INTERVAL_SECONDS**: الفترة الزمنية بين دورات التحليل (بالثواني) - الافتراضي: 60 (دقيقة واحدة)
- **COOLDOWN_SECONDS**: فترة الانتظار بين التنبيهات (بالثواني) - الافتراضي: 60 (دقيقة واحدة بين كل رسالة)
- **FORCE_DAILY_SUMMARY**: إرسال ملخص يومي (true/false)
- **TELEGRAM_BOT_TOKEN**: رمز البوت من BotFather
- **TELEGRAM_CHAT_ID**: معرف المحادثة على Telegram
- **LOG_LEVEL**: مستوى السجلات (`DEBUG`, `INFO`, `WARNING`, `ERROR`)

## ▶️ التشغيل

### تشغيل البوت محلياً:

```bash
python -m src.main
```

أو:

```bash
python src/main.py
```

### 🚀 رفع التطبيق إلى السيرفر:

لرفع التطبيق إلى السيرفر، راجع:
- **`QUICK_DEPLOY.md`** - دليل النشر السريع
- **`DEPLOYMENT.md`** - دليل النشر الشامل مع جميع التفاصيل

**الطرق المتاحة:**
1. النشر اليدوي باستخدام systemd (موصى به)
2. النشر باستخدام Docker
3. النشر باستخدام سكريبتات النشر المرفقة

### تشغيل الاختبارات:

```bash
pytest tests/
```

أو لاختبار وحدة معينة:

```bash
pytest tests/test_ema.py
pytest tests/test_rsi.py
pytest tests/test_strategy.py
```

## 📊 الاستراتيجيات المتاحة

### 🚀 استراتيجية متقدمة متعددة المؤشرات (Advanced Multi-Indicator) - **الأقوى والأكثر دقة**

هذه هي الاستراتيجية الافتراضية الجديدة التي تجمع بين أقوى المؤشرات الفنية لزيادة نسبة النجاح:

#### المؤشرات المستخدمة:

1. **MACD (12, 26, 9)**: لتحديد الاتجاه والقوة
2. **RSI (14)**: لتجنب الذروات (تجنب الشراء في ذروة الشراء والبيع في ذروة البيع)
3. **EMA (10, 20, 50)**: للاتجاهات متعددة الأطر الزمنية
4. **Support/Resistance**: للمستويات المهمة
5. **Price Action**: للتحقق من أنماط الشموع

#### قواعد الإشارات:

**الاستراتيجية تتطلب تأكيد من 4 مؤشرات على الأقل قبل إعطاء إشارة:**

- **BUY (شراء)** - يتطلب:
  - MACD: MACD Line > Signal Line AND MACD Line > 0 AND Histogram > 0
  - RSI: بين 45-70 (تجنب الذروة)
  - EMA: السعر > EMA10 > EMA20 > EMA50 (ترند صاعد قوي)
  - Support/Resistance: السعر قريب من دعم أو ارتداد من دعم
  - Price Action: نمط شمعة صاعد (Bullish Engulfing, Hammer, etc.)

- **SELL (بيع)** - يتطلب:
  - MACD: MACD Line < Signal Line AND MACD Line < 0 AND Histogram < 0
  - RSI: بين 30-55 (تجنب الذروة)
  - EMA: السعر < EMA10 < EMA20 < EMA50 (ترند هابط قوي)
  - Support/Resistance: السعر قريب من مقاومة أو ارتداد من مقاومة
  - Price Action: نمط شمعة هابط (Bearish Engulfing, Shooting Star, etc.)

- **NO_TRADE (لا تداول)**: إذا لم يتم تأكيد 4 مؤشرات على الأقل

#### درجة الثقة:

- الحد الأدنى: **75%** (عند تأكيد 4 مؤشرات)
- الحد الأقصى: **100%** (عند تأكيد جميع المؤشرات الخمسة)
- الثقة تعتمد على:
  - عدد المؤشرات المؤكدة (20 نقطة لكل مؤشر)
  - قوة كل مؤشر (MACD, RSI, EMA, Support/Resistance, Price Action)

### استراتيجيات أخرى متاحة:

#### 1. استراتيجية EMA Support Bounce:
- **EMA10** و **EMA50**: المتوسطات المتحركة الأسية
- **RSI(14)**: مؤشر القوة النسبية
- إشارة شراء عند الارتداد من دعم EMA في ترند صاعد

#### 2. استراتيجية MACD Crossover:
- **MACD (12, 26, 9)**: لتحديد الاتجاه
- إشارة عند تقاطع MACD مع Signal Line

#### 3. استراتيجية Price Action + Support/Resistance:
- تحديد مستويات الدعم والمقاومة تلقائياً
- استخدام أنماط الشموع (Price Action patterns)

### متى يتم إرسال التنبيه:

يتم إرسال تنبيه عبر Telegram فقط عند:

1. **تغيير الإشارة**: عندما تتغير الإشارة من BUY إلى SELL أو العكس
2. **انتهاء فترة الانتظار**: عندما تنتهي فترة COOLDOWN_SECONDS
3. **إشارة جديدة**: عند ظهور أول إشارة لأداة مالية

## 📝 مثال على رسالة Telegram

```
*EUR_USD M5 Signal*

*Signal:* `BUY`
*Confidence:* 75%

*Indicators:*
  EMA20: `1.08523`
  EMA50: `1.08498`
  RSI: `65.42`

*Last Close:* `1.08550`

*Rationale:*
_EMA20 (1.08523) > EMA50 (1.08498) and RSI (65.42) > 50_

`2024-01-15 14:30:00 UTC`
```

## 🛡️ السلامة والمخاطر

### ⚠️ تحذيرات مهمة:

1. **لا يوجد تنفيذ تلقائي**: هذا البوت **لا يقوم بتنفيذ أي أوامر تداول**. إنه يرسل إشارات تحليلية فقط.

2. **لا ضمانات**: الإشارات المولدة هي للاستخدام التعليمي والإعلامي فقط. لا يوجد ضمان للربح.

3. **استخدم حساب Practice أولاً**: تأكد من اختبار البوت على حساب Practice قبل التفكير في استخدام حساب Live.

4. **إدارة المخاطر**: إذا قررت استخدام هذه الإشارات في التداول الفعلي، استخدم إدارة مخاطر مناسبة (stop-loss، position sizing، إلخ).

5. **لا مسؤولية**: المطورون ليسوا مسؤولين عن أي خسائر قد تحدث نتيجة استخدام هذا البرنامج.

## 🔧 استكشاف الأخطاء

### البوت لا يرسل رسائل:

1. تأكد من صحة `TELEGRAM_BOT_TOKEN` و `TELEGRAM_CHAT_ID`
2. تأكد من إرسال رسالة إلى البوت أولاً (لتجنب حظر Telegram)
3. تحقق من السجلات للأخطاء

### خطأ في الاتصال بـ OANDA:

1. تأكد من صحة `OANDA_ACCESS_TOKEN`
2. تأكد من أن الحساب نشط
3. تحقق من أن البيئة صحيحة (`practice` أو `live`)
4. تحقق من اتصال الإنترنت

### عدم وجود بيانات كافية:

1. تأكد من أن `CANDLE_COUNT` كبير بدرجة كافية (200 على الأقل)
2. تحقق من أن الأداة المالية متاحة في OANDA
3. تأكد من أن `GRANULARITY` صحيح

## 📚 الوثائق التقنية

### البنية المعمارية:

- **Async-first**: جميع العمليات غير متزامنة باستخدام `asyncio` و `httpx.AsyncClient`
- **Retry Logic**: إعادة محاولة تلقائية مع انتظار تدريجي للتعامل مع أخطاء الشبكة
- **State Persistence**: حفظ الحالة في ملف JSON لتجنب إرسال تنبيهات متكررة عند إعادة التشغيل
- **Error Handling**: معالجة شاملة للأخطاء مع سجلات واضحة

### الاختبارات:

تم تضمين اختبارات وحدة شاملة لـ:
- حساب EMA
- حساب RSI
- منطق الاستراتيجية

قم بتشغيل الاختبارات للتأكد من أن كل شيء يعمل بشكل صحيح.

## 📄 الرخصة

هذا المشروع مقدم "كما هو" للأغراض التعليمية فقط.

## 🤝 المساهمة

للمساهمة في تحسين المشروع:
1. قم بإنشاء Fork للمشروع
2. أنشئ فرعاً للميزة الجديدة
3. أضف التغييرات والاختبارات
4. أرسل Pull Request

## 📞 الدعم

للأسئلة والمشاكل:
1. تحقق من قسم استكشاف الأخطاء أعلاه
2. راجع السجلات (logs) للأخطاء
3. تأكد من أن جميع المتغيرات البيئية صحيحة

---

**تذكر**: التداول ينطوي على مخاطر. استخدم هذا البرنامج بحذر ومسؤولية.

