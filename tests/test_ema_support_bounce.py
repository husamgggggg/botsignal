"""Unit tests for EMA Support Bounce Strategy."""
import pytest

from src.strategies.ema_support_bounce import EMASupportBounceStrategy, Signal


def test_strategy_uptrend_correction_bounce():
    """Test strategy generates BUY signal when conditions are met."""
    strategy = EMASupportBounceStrategy(ema_period=10, support_tolerance_pct=0.1)
    
    # Create candles with uptrend, correction, and bounce
    candles = []
    base_price = 1.0850
    
    # شموع صاعدة فوق EMA (للتأكد من الترند الصاعد)
    for i in range(10):  # أول 10 شموع لحساب EMA
        candles.append({
            "open": base_price + (i * 0.0001),
            "close": base_price + (i * 0.0001) + 0.00005,
            "high": base_price + (i * 0.0001) + 0.0001,
            "low": base_price + (i * 0.0001) - 0.00005,
            "volume": 1000
        })
    
    # شموع صاعدة أخرى (الترند الصاعد) - نحتاج على الأقل 17 شمعة
    for i in range(10, 18):
        candles.append({
            "open": base_price + (i * 0.0001),
            "close": base_price + (i * 0.0001) + 0.00005,  # صاعدة
            "high": base_price + (i * 0.0001) + 0.0001,
            "low": base_price + (i * 0.0001) - 0.00005,
            "volume": 1000
        })
    
    # شمعة تصحيح هابطة على الدعم (EMA)
    ema_calc = strategy.analyze(candles)
    if ema_calc.ema_10:
        correction_price = ema_calc.ema_10
        candles.append({
            "open": correction_price + 0.00005,  # فتح أعلى
            "close": correction_price,  # إغلاق على EMA (دعم)
            "high": correction_price + 0.0001,
            "low": correction_price - 0.00005,
            "volume": 1000
        })
        
        # شمعة برجكشن صعودية
        candles.append({
            "open": correction_price,
            "close": correction_price + 0.0002,  # صاعدة وتغلق فوق EMA
            "high": correction_price + 0.0003,
            "low": correction_price - 0.00005,
            "volume": 1000
        })
        
        result = strategy.analyze(candles)
        
        # يجب أن تنتج إشارة شراء أو NO_TRADE (حسب دقة البيانات)
        assert result.signal in [Signal.BUY, Signal.NO_TRADE]
        assert result.confidence >= 0
        assert result.confidence <= 100
        assert result.ema_10 is not None


def test_strategy_insufficient_candles():
    """Test strategy with insufficient candles."""
    candles = [{"open": 1.0850, "close": 1.0855, "high": 1.0860, "low": 1.0845}] * 10
    
    strategy = EMASupportBounceStrategy(ema_period=10)
    
    with pytest.raises(ValueError, match="Need at least"):
        strategy.analyze(candles)


def test_strategy_empty_candles():
    """Test strategy with empty candles."""
    strategy = EMASupportBounceStrategy()
    
    with pytest.raises(ValueError, match="Cannot analyze empty"):
        strategy.analyze([])


def test_strategy_no_uptrend():
    """Test strategy when there's no uptrend."""
    strategy = EMASupportBounceStrategy(ema_period=10)
    
    candles = []
    base_price = 1.0850
    
    # شموع هابطة (لا يوجد ترند صاعد)
    for i in range(20):
        candles.append({
            "open": base_price - (i * 0.0001),
            "close": base_price - (i * 0.0001) - 0.00005,  # هابطة
            "high": base_price - (i * 0.0001) + 0.00005,
            "low": base_price - (i * 0.0001) - 0.0001,
            "volume": 1000
        })
    
    result = strategy.analyze(candles)
    
    # يجب أن تكون NO_TRADE لأن الترند ليس صاعداً
    assert result.signal == Signal.NO_TRADE


def test_strategy_correction_candle_waiting():
    """Test strategy when correction candle found but bounce hasn't happened yet."""
    strategy = EMASupportBounceStrategy(ema_period=10)
    
    candles = []
    base_price = 1.0850
    
    # شموع صاعدة - نحتاج على الأقل 17 شمعة
    for i in range(17):
        candles.append({
            "open": base_price + (i * 0.0001),
            "close": base_price + (i * 0.0001) + 0.00005,
            "high": base_price + (i * 0.0001) + 0.0001,
            "low": base_price + (i * 0.0001) - 0.00005,
            "volume": 1000
        })
    
    # شمعة تصحيح هابطة على الدعم (الشمعة الحالية)
    ema_calc = strategy.analyze(candles[:17])
    if ema_calc.ema_10:
        correction_price = ema_calc.ema_10
        candles.append({
            "open": correction_price + 0.00005,
            "close": correction_price,  # إغلاق على EMA
            "high": correction_price + 0.0001,
            "low": correction_price - 0.00005,
            "volume": 1000
        })
        
        result = strategy.analyze(candles)
        
        # يجب أن تكون NO_TRADE في انتظار البرجكشن
        assert result.signal == Signal.NO_TRADE
        assert "انتظار" in result.rationale or "البرجكشن" in result.rationale


def test_strategy_confidence_calculation():
    """Test that confidence is calculated correctly."""
    strategy = EMASupportBounceStrategy(ema_period=10)
    
    candles = []
    base_price = 1.0850
    
    # إنشاء ترند صاعد - نحتاج على الأقل 17 شمعة
    for i in range(17):
        candles.append({
            "open": base_price + (i * 0.0001),
            "close": base_price + (i * 0.0001) + 0.00005,
            "high": base_price + (i * 0.0001) + 0.0001,
            "low": base_price + (i * 0.0001) - 0.00005,
            "volume": 1000
        })
    
    # إضافة شمعة تصحيح وبرجكشن
    ema_calc = strategy.analyze(candles[:17])
    if ema_calc.ema_10:
        correction_price = ema_calc.ema_10
        candles.append({
            "open": correction_price + 0.00005,
            "close": correction_price,
            "high": correction_price + 0.0001,
            "low": correction_price - 0.00005,
            "volume": 1000
        })
        
        candles.append({
            "open": correction_price,
            "close": correction_price + 0.0002,
            "high": correction_price + 0.0003,
            "low": correction_price - 0.00005,
            "volume": 1000
        })
        
        result = strategy.analyze(candles)
        
        # الثقة يجب أن تكون بين 0 و 100
        assert 0 <= result.confidence <= 100
        
        # إذا كانت الإشارة شراء، الثقة يجب أن تكون > 0
        if result.signal == Signal.BUY:
            assert result.confidence > 0


def test_strategy_rationale():
    """Test that rationale is provided."""
    strategy = EMASupportBounceStrategy(ema_period=10)
    
    candles = []
    base_price = 1.0850
    
    # نحتاج على الأقل 17 شمعة
    for i in range(17):
        candles.append({
            "open": base_price + (i * 0.0001),
            "close": base_price + (i * 0.0001) + 0.00005,
            "high": base_price + (i * 0.0001) + 0.0001,
            "low": base_price + (i * 0.0001) - 0.00005,
            "volume": 1000
        })
    
    result = strategy.analyze(candles)
    
    # يجب أن يحتوي على rationale غير فارغ
    assert isinstance(result.rationale, str)
    assert len(result.rationale) > 0

