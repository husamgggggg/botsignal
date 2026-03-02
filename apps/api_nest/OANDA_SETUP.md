# إعداد OANDA API للتحليل الفني

## نظرة عامة

تم إنشاء نظام تحليل فني متقدم يستخدم OANDA API لجلب بيانات الأسعار وتحليلها باستخدام مؤشرات فنية متعددة.

## المتطلبات

1. حساب OANDA (Practice أو Live)
2. API Key من OANDA
3. Account ID من OANDA

## خطوات الإعداد

### 1. إنشاء حساب OANDA

1. اذهب إلى [OANDA](https://www.oanda.com/)
2. سجل حساب جديد (Practice Account مجاني)
3. بعد التسجيل، اذهب إلى **Manage API Access**

### 2. الحصول على API Key

1. بعد تسجيل الدخول، اذهب إلى **Manage API Access** من القائمة الرئيسية
2. انقر على **Generate API Key** أو **Create API Token**
3. اختر **Practice** أو **Live** حسب نوع الحساب
4. انسخ الـ API Key فوراً (لن تتمكن من رؤيته مرة أخرى)
5. احفظ الـ API Key في مكان آمن

**ملاحظة مهمة**: 
- Practice API Key يبدأ عادة بـ `fxtpractice-`
- Live API Key يبدأ عادة بـ `fxtrade-`

### 3. الحصول على Account ID

1. في لوحة التحكم، اذهب إلى **Account Summary** أو **Trade** > **Account**
2. ابحث عن **Account ID** (عادة يبدأ بـ `101-` للـ Practice Account)
3. انسخ Account ID

**ملاحظة**: Account ID ليس مطلوباً لجلب بيانات الشموع، لكن قد يكون مفيداً لعمليات أخرى

### 4. إضافة المتغيرات إلى `.env`

أضف المتغيرات التالية إلى ملف `.env` في `apps/api_nest/`:

```env
# OANDA API
OANDA_API_KEY="your-oanda-api-key-here"
OANDA_ACCOUNT_ID="your-oanda-account-id-here"
OANDA_ENVIRONMENT="practice" # 'practice' or 'live'
```

## المؤشرات الفنية المستخدمة

### 1. EMA (Exponential Moving Average)
- الفترات: 10، 20، 50
- الاستخدام: تحديد الاتجاه

### 2. RSI (Relative Strength Index)
- الفترة: 14
- النطاقات:
  - للشراء: 45-70
  - للبيع: 30-55

### 3. MACD (Moving Average Convergence Divergence)
- الإعدادات: Fast=12، Slow=26، Signal=9
- الاستخدام: تحديد الاتجاه والقوة

### 4. Support/Resistance
- Lookback: 50 شمعة
- Min Touches: 2
- Tolerance: 0.15%

### 5. Price Action
- الأنماط المكتشفة:
  - صاعدة: Bullish Engulfing، Pin Bar Bullish، Hammer
  - هابطة: Bearish Engulfing， Pin Bar Bearish، Shooting Star

## الاستراتيجية المستخدمة

### Advanced Multi-Indicator Strategy (الافتراضية)

- **المؤشرات**: MACD + RSI + EMA (10, 20, 50) + Support/Resistance + Price Action
- **الحد الأدنى للتأكيد**: 4 مؤشرات من 5
- **درجة الثقة**: 75%-100%
- **الإطار الزمني**: M1 (دقيقة واحدة)

## كيفية العمل

1. النظام يجلب بيانات الأسعار من OANDA كل دقيقة
2. يحسب المؤشرات الفنية للشموع السابقة (500 شمعة)
3. يحلل الإشارات باستخدام الاستراتيجية المتقدمة
4. ينشئ إشارات تلقائياً عند توفر شروط الشراء/البيع
5. يحفظ الإشارات في قاعدة البيانات ويرسل إشعارات للمستخدمين

## الأزواج المدعومة

- EUR/USD
- GBP/USD
- USD/JPY
- AUD/USD
- USD/CAD
- USD/CHF
- NZD/USD
- وأكثر...

## ملاحظات مهمة

1. **Practice Account**: مجاني ومثالي للاختبار
2. **Rate Limits**: OANDA يحد من عدد الطلبات في الدقيقة
3. **Data Quality**: تأكد من جودة الاتصال بالإنترنت
4. **Testing**: اختبر النظام أولاً على Practice Account قبل الانتقال إلى Live

## استكشاف الأخطاء

### خطأ: "Request failed with status code 400"
**السبب الأكثر شيوعاً**: API Key غير صحيح أو غير موجود

**الحلول**:
1. تحقق من أن `OANDA_API_KEY` موجود في ملف `.env`
2. تأكد من نسخ API Key بشكل كامل (بدون مسافات إضافية)
3. تحقق من أن API Key يبدأ بـ `fxtpractice-` للـ Practice Account
4. تأكد من تفعيل API Access في حساب OANDA
5. جرب إنشاء API Key جديد من OANDA

**للتحقق من API Key**:
```bash
# في ملف .env
OANDA_API_KEY="fxtpractice-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

### خطأ: "OANDA_API_KEY is not configured"
- أضف `OANDA_API_KEY` إلى ملف `.env`
- أعد تشغيل الخادم بعد إضافة المتغيرات

### خطأ: "Not enough candles"
- النظام يحتاج على الأقل 100 شمعة للتحليل
- تأكد من أن الزوج متاح في OANDA Practice Account
- بعض الأزواج مثل USD/BDT و USD/NGN قد لا تكون متاحة في Practice Account

### خطأ: "Failed to get candles"
- تحقق من اسم الزوج (يجب أن يكون بالصيغة: EUR/USD)
- تحقق من الاتصال بالإنترنت
- تحقق من Rate Limits (OANDA يحد من عدد الطلبات)
- بعض الأزواج غير متاحة في Practice Account

### خطأ: "OANDA features will be disabled"
- هذا تحذير وليس خطأ
- النظام سيعمل بدون OANDA لكن لن يتم توليد إشارات تلقائياً
- أضف `OANDA_API_KEY` لتفعيل الميزة

## الدعم

للمزيد من المعلومات، راجع [OANDA API Documentation](https://developer.oanda.com/)

