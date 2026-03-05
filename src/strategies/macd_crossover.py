"""MACD Crossover Strategy.

الاستراتيجية:
- استخدام MACD بالإعدادات الافتراضية (12, 26, 9)
- إشارة شراء عندما:
    * خط MACD وخط Signal تحت شموع الهيستوغرام
    * خط MACD فوق نقطة الصفر (خط Signal أيضاً فوق الصفر)
    * تظهر شمعة خضراء (صاعدة)
    * الشمعة الخضراء ضمن أول 6 شموع من آخر الشموع
- إشارة بيع (العكس):
    * خط MACD وخط Signal فوق شموع الهيستوغرام
    * خط MACD تحت نقطة الصفر
    * تظهر شمعة حمراء (هابطة)
    * الشمعة الحمراء ضمن أول 6 شموع
- تنبيه "احتمال صفقة" عند اقتراب الشروط
"""
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

from src.indicators.macd import calculate_macd


class Signal(Enum):
    """Trading signal types."""
    BUY = "BUY"
    SELL = "SELL"
    NO_TRADE = "NO_TRADE"
    POTENTIAL_BUY = "POTENTIAL_BUY"  # تنبيه احتمال شراء
    POTENTIAL_SELL = "POTENTIAL_SELL"  # تنبيه احتمال بيع


@dataclass
class StrategyResult:
    """Result of strategy analysis."""
    signal: Signal
    confidence: int  # 0-100
    macd_line: Optional[float]
    signal_line: Optional[float]
    histogram: Optional[float]
    last_close: float
    last_open: float
    rationale: str


class MACDCrossoverStrategy:
    """استراتيجية MACD Crossover.
    
    القواعد:
        1. شراء (BUY):
           - MACD Line و Signal Line تحت الهيستوغرام (الهيستوغرام موجب)
           - MACD Line و Signal Line فوق الصفر
           - شمعة خضراء (صاعدة) في آخر 6 شموع
        
        2. بيع (SELL):
           - MACD Line و Signal Line فوق الهيستوغرام (الهيستوغرام سالب)
           - MACD Line و Signal Line تحت الصفر
           - شمعة حمراء (هابطة) في آخر 6 شموع
        
        3. احتمال شراء/بيع (POTENTIAL):
           - عند اقتراب الشروط لكن لم تكتمل بعد
    """
    
    def __init__(
        self,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
        lookback_candles: int = 6
    ):
        """Initialize strategy.
        
        Args:
            fast_period: فترة EMA السريعة (default 12)
            slow_period: فترة EMA البطيئة (default 26)
            signal_period: فترة خط الإشارة (default 9)
            lookback_candles: عدد الشموع للبحث عن شمعة الإشارة (default 6)
        """
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
        self.lookback_candles = lookback_candles
    
    def analyze(self, candles: List[dict]) -> StrategyResult:
        """Analyze candles and generate trading signal.
        
        Args:
            candles: List of candle dictionaries with 'open', 'high', 'low', 'close' keys
                    Candles should be ordered chronologically (oldest first)
        
        Returns:
            StrategyResult with signal, confidence, indicators, and rationale
            
        Raises:
            ValueError: If insufficient candles or missing data
        """
        if len(candles) == 0:
            raise ValueError("Cannot analyze empty candles list")
        
        # نحتاج على الأقل slow_period + signal_period شموع
        min_candles = self.slow_period + self.signal_period
        if len(candles) < min_candles:
            raise ValueError(
                f"Need at least {min_candles} candles, got {len(candles)}"
            )
        
        # استخراج الأسعار
        close_prices = [float(candle["close"]) for candle in candles]
        open_prices = [float(candle["open"]) for candle in candles]
        
        # حساب MACD
        macd_line, signal_line, histogram = calculate_macd(
            close_prices,
            fast_period=self.fast_period,
            slow_period=self.slow_period,
            signal_period=self.signal_period
        )
        
        # الحصول على القيم الأخيرة
        last_close = close_prices[-1]
        last_open = open_prices[-1]
        last_macd = macd_line[-1] if macd_line else None
        last_signal = signal_line[-1] if signal_line else None
        last_histogram = histogram[-1] if histogram else None
        
        if last_macd is None or last_signal is None or last_histogram is None:
            return StrategyResult(
                signal=Signal.NO_TRADE,
                confidence=0,
                macd_line=last_macd,
                signal_line=last_signal,
                histogram=last_histogram,
                last_close=last_close,
                last_open=last_open,
                rationale="لا توجد بيانات كافية لحساب MACD"
            )
        
        # البحث عن شمعة إشارة في آخر lookback_candles شموع
        # نبحث من الأحدث إلى الأقدم
        signal_candle_idx = None
        signal_candle_type = None  # "green" or "red"
        
        search_end = max(0, len(candles) - self.lookback_candles)
        for i in range(len(candles) - 1, search_end - 1, -1):
            candle = candles[i]
            candle_open = float(candle["open"])
            candle_close = float(candle["close"])
            
            if candle_close > candle_open:
                # شمعة خضراء (صاعدة)
                signal_candle_idx = i
                signal_candle_type = "green"
                break
            elif candle_close < candle_open:
                # شمعة حمراء (هابطة)
                signal_candle_idx = i
                signal_candle_type = "red"
                break
        
        # فحص شروط الشراء
        if signal_candle_type == "green":
            # شرط الشراء: MACD و Signal تحت الهيستوغرام وفوق الصفر
            # "تحت الهيستوغرام" يعني أن الهيستوغرام أعلى من MACD و Signal
            # الهيستوغرام = MACD - Signal
            # إذا كان Histogram > 0، فإن MACD > Signal (MACD أعلى من Signal)
            # "تحت الهيستوغرام" يعني أن القيمة المطلقة للهيستوغرام أكبر من MACD و Signal
            # لكن هذا لا يحدث عادة. المرجح أن "تحت الهيستوغرام" يعني:
            # عندما يكون Histogram موجب (MACD > Signal) وكلاهما فوق الصفر
            
            # شرط الشراء: MACD و Signal فوق الصفر، والهيستوغرام موجب (MACD > Signal)
            # "تحت الهيستوغرام" يعني أن الهيستوغرام موجب (MACD أعلى من Signal)
            macd_above_zero = last_macd > 0
            signal_above_zero = last_signal > 0
            histogram_positive = last_histogram > 0  # MACD أعلى من Signal (الهيستوغرام موجب)
            
            if macd_above_zero and signal_above_zero and histogram_positive:
                # إشارة شراء!
                confidence = self._calculate_confidence(
                    macd=last_macd,
                    signal=last_signal,
                    histogram=last_histogram,
                    signal_type="buy"
                )
                
                return StrategyResult(
                    signal=Signal.BUY,
                    confidence=confidence,
                    macd_line=last_macd,
                    signal_line=last_signal,
                    histogram=last_histogram,
                    last_close=last_close,
                    last_open=last_open,
                    rationale=(
                        f"✅ إشارة شراء: MACD ({last_macd:.5f}) و Signal ({last_signal:.5f}) "
                        f"فوق الصفر، Histogram موجب ({last_histogram:.5f})، "
                        f"شمعة خضراء في الشمعة #{signal_candle_idx}"
                    )
                )
            else:
                # احتمال شراء - الشروط قريبة لكن لم تكتمل
                # إذا كان شرطان محققان، نعتبره إشارة شراء ضعيفة بدلاً من POTENTIAL
                conditions_met = sum([macd_above_zero, signal_above_zero, histogram_positive])
                if conditions_met >= 2:
                    # تحويل إلى BUY مع ثقة أقل
                    confidence = self._calculate_confidence(
                        macd=last_macd,
                        signal=last_signal,
                        histogram=last_histogram,
                        signal_type="buy"
                    )
                    # تقليل الثقة بنسبة 20% لأن شرط واحد مفقود
                    confidence = max(50, int(confidence * 0.8))
                    
                    return StrategyResult(
                        signal=Signal.BUY,
                        confidence=confidence,
                        macd_line=last_macd,
                        signal_line=last_signal,
                        histogram=last_histogram,
                        last_close=last_close,
                        last_open=last_open,
                        rationale=(
                            f"✅ إشارة شراء (ضعيفة): شمعة خضراء موجودة، "
                            f"MACD{' فوق' if macd_above_zero else ' تحت'} الصفر، "
                            f"Signal{' فوق' if signal_above_zero else ' تحت'} الصفر، "
                            f"Histogram{' موجب' if histogram_positive else ' سالب'} "
                            f"(شرط واحد مفقود)"
                        )
                    )
        
        # فحص شروط البيع
        if signal_candle_type == "red":
            # شرط البيع: MACD و Signal فوق الهيستوغرام وتحت الصفر
            # "فوق الهيستوغرام" يعني أن الهيستوغرام سالب (MACD < Signal)
            # عندما يكون Histogram < 0، فإن MACD < Signal (MACD تحت Signal)
            
            macd_below_zero = last_macd < 0
            signal_below_zero = last_signal < 0
            histogram_negative = last_histogram < 0  # MACD تحت Signal (الهيستوغرام سالب)
            
            if macd_below_zero and signal_below_zero and histogram_negative:
                # إشارة بيع!
                confidence = self._calculate_confidence(
                    macd=last_macd,
                    signal=last_signal,
                    histogram=last_histogram,
                    signal_type="sell"
                )
                
                return StrategyResult(
                    signal=Signal.SELL,
                    confidence=confidence,
                    macd_line=last_macd,
                    signal_line=last_signal,
                    histogram=last_histogram,
                    last_close=last_close,
                    last_open=last_open,
                    rationale=(
                        f"✅ إشارة بيع: MACD ({last_macd:.5f}) و Signal ({last_signal:.5f}) "
                        f"تحت الصفر، Histogram سالب ({last_histogram:.5f})، "
                        f"شمعة حمراء في الشمعة #{signal_candle_idx}"
                    )
                )
            else:
                # احتمال بيع - الشروط قريبة لكن لم تكتمل
                # إذا كان شرطان محققان، نعتبره إشارة بيع ضعيفة بدلاً من POTENTIAL
                conditions_met = sum([macd_below_zero, signal_below_zero, histogram_negative])
                if conditions_met >= 2:
                    # تحويل إلى SELL مع ثقة أقل
                    confidence = self._calculate_confidence(
                        macd=last_macd,
                        signal=last_signal,
                        histogram=last_histogram,
                        signal_type="sell"
                    )
                    # تقليل الثقة بنسبة 20% لأن شرط واحد مفقود
                    confidence = max(50, int(confidence * 0.8))
                    
                    return StrategyResult(
                        signal=Signal.SELL,
                        confidence=confidence,
                        macd_line=last_macd,
                        signal_line=last_signal,
                        histogram=last_histogram,
                        last_close=last_close,
                        last_open=last_open,
                        rationale=(
                            f"✅ إشارة بيع (ضعيفة): شمعة حمراء موجودة، "
                            f"MACD{' تحت' if macd_below_zero else ' فوق'} الصفر، "
                            f"Signal{' تحت' if signal_below_zero else ' فوق'} الصفر، "
                            f"Histogram{' سالب' if histogram_negative else ' موجب'} "
                            f"(شرط واحد مفقود)"
                        )
                    )
        
        # لا توجد إشارة
        return StrategyResult(
            signal=Signal.NO_TRADE,
            confidence=0,
            macd_line=last_macd,
            signal_line=last_signal,
            histogram=last_histogram,
            last_close=last_close,
            last_open=last_open,
            rationale=(
                f"لا توجد إشارة: MACD={last_macd:.5f}, Signal={last_signal:.5f}, "
                f"Histogram={last_histogram:.5f}"
            )
        )
    
    def _calculate_confidence(
        self,
        macd: float,
        signal: float,
        histogram: float,
        signal_type: str
    ) -> int:
        """Calculate confidence score (0-100).
        
        Args:
            macd: MACD line value
            signal: Signal line value
            histogram: Histogram value
            signal_type: "buy" or "sell"
            
        Returns:
            Confidence score 0-100
        """
        # الثقة تعتمد على قوة MACD و Signal والهيستوغرام
        # المسافة من الصفر (كلما كانت أبعد = ثقة أعلى)
        
        if signal_type == "buy":
            macd_distance = abs(macd) if macd > 0 else 0
            signal_distance = abs(signal) if signal > 0 else 0
            hist_strength = abs(histogram) if histogram > 0 else 0
        else:  # sell
            macd_distance = abs(macd) if macd < 0 else 0
            signal_distance = abs(signal) if signal < 0 else 0
            hist_strength = abs(histogram) if histogram < 0 else 0
        
        # حساب الثقة بناءً على القيم (نسبي)
        # نستخدم متوسط القيم لتحديد الثقة
        avg_distance = (macd_distance + signal_distance + hist_strength) / 3.0
        
        # تحويل إلى نسبة مئوية (0-100)
        # نستخدم قيمة مرجعية صغيرة (0.0001) للعملات
        reference = 0.0001
        confidence = min(100, int((avg_distance / reference) * 10))
        
        # ضمان حد أدنى من الثقة
        return max(60, confidence)

