"""EMA/RSI crossover strategy."""
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

from src.indicators.ema import calculate_ema
from src.indicators.rsi import calculate_rsi


class Signal(Enum):
    """Trading signal types."""
    BUY = "BUY"
    SELL = "SELL"
    NO_TRADE = "NO_TRADE"


@dataclass
class StrategyResult:
    """Result of strategy analysis."""
    signal: Signal
    confidence: int  # 0-100
    ema_20: Optional[float]
    ema_50: Optional[float]
    rsi: Optional[float]
    last_close: float
    rationale: str


class EMARSIStrategy:
    """EMA crossover strategy with RSI filter.
    
    Rules:
        - BUY: EMA20 > EMA50 AND RSI > 50
        - SELL: EMA20 < EMA50 AND RSI < 50
        - NO_TRADE: Otherwise
    """
    
    def __init__(
        self,
        ema_short_period: int = 20,
        ema_long_period: int = 50,
        rsi_period: int = 14,
        min_ema_distance_pct: float = 0.0
    ):
        """Initialize strategy.
        
        Args:
            ema_short_period: Short EMA period (default 20)
            ema_long_period: Long EMA period (default 50)
            rsi_period: RSI period (default 14)
            min_ema_distance_pct: Minimum EMA distance percentage to generate signal
                                  (default 0.0 = no minimum)
        """
        self.ema_short_period = ema_short_period
        self.ema_long_period = ema_long_period
        self.rsi_period = rsi_period
        self.min_ema_distance_pct = min_ema_distance_pct
    
    def analyze(self, candles: List[dict]) -> StrategyResult:
        """Analyze candles and generate trading signal.
        
        Args:
            candles: List of candle dictionaries with 'close' key
                    Candles should be ordered chronologically (oldest first)
        
        Returns:
            StrategyResult with signal, confidence, indicators, and rationale
            
        Raises:
            ValueError: If insufficient candles or missing data
        """
        if len(candles) == 0:
            raise ValueError("Cannot analyze empty candles list")
        
        if len(candles) < self.ema_long_period + 1:
            raise ValueError(
                f"Need at least {self.ema_long_period + 1} candles, got {len(candles)}"
            )
        
        # Extract close prices
        close_prices = [float(candle["close"]) for candle in candles]
        last_close = close_prices[-1]
        
        # Calculate indicators
        ema_20_values = calculate_ema(close_prices, self.ema_short_period)
        ema_50_values = calculate_ema(close_prices, self.ema_long_period)
        rsi_values = calculate_rsi(close_prices, self.rsi_period)
        
        # Get latest values
        ema_20 = ema_20_values[-1] if ema_20_values else None
        ema_50 = ema_50_values[-1] if ema_50_values else None
        rsi = rsi_values[-1] if rsi_values else None
        
        # Check if we have all required indicators
        if ema_20 is None or ema_50 is None or rsi is None:
            return StrategyResult(
                signal=Signal.NO_TRADE,
                confidence=0,
                ema_20=ema_20,
                ema_50=ema_50,
                rsi=rsi,
                last_close=last_close,
                rationale="Insufficient data to calculate all indicators"
            )
        
        # Calculate EMA distance percentage
        ema_distance_pct = abs(ema_20 - ema_50) / last_close * 100
        
        # Check minimum distance requirement
        if ema_distance_pct < self.min_ema_distance_pct:
            return StrategyResult(
                signal=Signal.NO_TRADE,
                confidence=0,
                ema_20=ema_20,
                ema_50=ema_50,
                rsi=rsi,
                last_close=last_close,
                rationale=f"EMA distance ({ema_distance_pct:.4f}%) below minimum ({self.min_ema_distance_pct}%)"
            )
        
        # Determine signal based on rules
        if ema_20 > ema_50 and rsi > 50:
            signal = Signal.BUY
            rationale = f"EMA20 ({ema_20:.5f}) > EMA50 ({ema_50:.5f}) and RSI ({rsi:.2f}) > 50"
        elif ema_20 < ema_50 and rsi < 50:
            signal = Signal.SELL
            rationale = f"EMA20 ({ema_20:.5f}) < EMA50 ({ema_50:.5f}) and RSI ({rsi:.2f}) < 50"
        else:
            signal = Signal.NO_TRADE
            if ema_20 > ema_50:
                rationale = f"EMA20 > EMA50 but RSI ({rsi:.2f}) <= 50"
            elif ema_20 < ema_50:
                rationale = f"EMA20 < EMA50 but RSI ({rsi:.2f}) >= 50"
            else:
                rationale = "EMA20 = EMA50"
        
        # Calculate confidence (0-100)
        confidence = self._calculate_confidence(
            ema_20=ema_20,
            ema_50=ema_50,
            rsi=rsi,
            ema_distance_pct=ema_distance_pct,
            signal=signal
        )
        
        return StrategyResult(
            signal=signal,
            confidence=confidence,
            ema_20=ema_20,
            ema_50=ema_50,
            rsi=rsi,
            last_close=last_close,
            rationale=rationale
        )
    
    def _calculate_confidence(
        self,
        ema_20: float,
        ema_50: float,
        rsi: float,
        ema_distance_pct: float,
        signal: Signal
    ) -> int:
        """Calculate confidence score (0-100) based on indicator strength.
        
        Confidence is based on:
        - Distance between EMAs (larger = higher confidence)
        - RSI distance from 50 (farther = higher confidence)
        
        Args:
            ema_20: EMA20 value
            ema_50: EMA50 value
            rsi: RSI value
            ema_distance_pct: EMA distance as percentage
            signal: Current signal
            
        Returns:
            Confidence score 0-100
        """
        if signal == Signal.NO_TRADE:
            return 0
        
        # EMA distance component (0-50 points)
        # Normalize to 0-50 scale (assume max reasonable distance is 2%)
        max_ema_distance = 2.0  # 2% of price
        ema_confidence = min(50.0, (ema_distance_pct / max_ema_distance) * 50.0)
        
        # RSI distance component (0-50 points)
        # Distance from 50, normalized to 0-50
        rsi_distance_from_50 = abs(rsi - 50.0)
        # RSI range is 0-100, so max distance from 50 is 50
        rsi_confidence = min(50.0, (rsi_distance_from_50 / 50.0) * 50.0)
        
        # Combine (simple average for now, could be weighted)
        total_confidence = (ema_confidence + rsi_confidence) / 2.0
        
        # Ensure within 0-100 range
        return int(min(100, max(0, total_confidence)))

