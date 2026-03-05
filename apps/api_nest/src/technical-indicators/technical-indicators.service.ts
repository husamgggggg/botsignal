import { Injectable, Logger } from '@nestjs/common';
import { OandaCandle } from '../oanda/oanda.service';

export interface EMAValues {
  ema10: number[];
  ema20: number[];
  ema50: number[];
}

export interface MACDValues {
  macdLine: number[];
  signalLine: number[];
  histogram: number[];
}

export interface SupportResistanceLevel {
  price: number;
  type: 'support' | 'resistance';
  touches: number;
  strength: number; // 0-100
}

@Injectable()
export class TechnicalIndicatorsService {
  private readonly logger = new Logger(TechnicalIndicatorsService.name);

  /**
   * Calculate EMA (Exponential Moving Average)
   * Formula: EMA = Price(t) × k + EMA(y) × (1 - k) where k = 2 / (N + 1)
   */
  calculateEMA(prices: number[], period: number): number[] {
    if (prices.length < period) {
      return [];
    }

    const k = 2 / (period + 1);
    const ema: number[] = [];

    // First EMA value is SMA
    let sum = 0;
    for (let i = 0; i < period; i++) {
      sum += prices[i];
    }
    ema[period - 1] = sum / period;

    // Calculate subsequent EMA values
    for (let i = period; i < prices.length; i++) {
      ema[i] = prices[i] * k + ema[i - 1] * (1 - k);
    }

    return ema;
  }

  /**
   * Calculate all EMA values (10, 20, 50)
   */
  calculateEMAs(candles: OandaCandle[]): EMAValues {
    const closes = candles.map((c) => c.close);

    return {
      ema10: this.calculateEMA(closes, 10),
      ema20: this.calculateEMA(closes, 20),
      ema50: this.calculateEMA(closes, 50),
    };
  }

  /**
   * Calculate RSI (Relative Strength Index)
   * Formula: RSI = 100 - (100 / (1 + RS)) where RS = Average Gain / Average Loss
   */
  calculateRSI(prices: number[], period: number = 14): number[] {
    if (prices.length < period + 1) {
      return [];
    }

    const rsi: number[] = [];
    const gains: number[] = [];
    const losses: number[] = [];

    // Calculate price changes
    for (let i = 1; i < prices.length; i++) {
      const change = prices[i] - prices[i - 1];
      gains.push(change > 0 ? change : 0);
      losses.push(change < 0 ? Math.abs(change) : 0);
    }

    // Calculate initial average gain and loss
    let avgGain = 0;
    let avgLoss = 0;
    for (let i = 0; i < period; i++) {
      avgGain += gains[i];
      avgLoss += losses[i];
    }
    avgGain /= period;
    avgLoss /= period;

    // Calculate RSI for first period
    if (avgLoss === 0) {
      rsi[period] = 100;
    } else {
      const rs = avgGain / avgLoss;
      rsi[period] = 100 - (100 / (1 + rs));
    }

    // Calculate subsequent RSI values using Wilder's smoothing
    for (let i = period + 1; i < gains.length; i++) {
      avgGain = (avgGain * (period - 1) + gains[i]) / period;
      avgLoss = (avgLoss * (period - 1) + losses[i]) / period;

      if (avgLoss === 0) {
        rsi[i] = 100;
      } else {
        const rs = avgGain / avgLoss;
        rsi[i] = 100 - (100 / (1 + rs));
      }
    }

    return rsi;
  }

  /**
   * Calculate MACD (Moving Average Convergence Divergence
   */
  calculateMACD(prices: number[], fastPeriod: number = 12, slowPeriod: number = 26, signalPeriod: number = 9): MACDValues {
    const emaFast = this.calculateEMA(prices, fastPeriod);
    const emaSlow = this.calculateEMA(prices, slowPeriod);

    if (emaFast.length === 0 || emaSlow.length === 0) {
      return { macdLine: [], signalLine: [], histogram: [] };
    }

    // Calculate MACD Line
    const macdLine: number[] = [];
    const minLength = Math.min(emaFast.length, emaSlow.length);
    const startIndex = Math.max(emaFast.length - minLength, emaSlow.length - minLength);

    for (let i = startIndex; i < minLength; i++) {
      const fastIndex = emaFast.length - minLength + i;
      const slowIndex = emaSlow.length - minLength + i;
      macdLine.push(emaFast[fastIndex] - emaSlow[slowIndex]);
    }

    // Calculate Signal Line (EMA of MACD Line)
    const signalLine = this.calculateEMA(macdLine, signalPeriod);

    // Calculate Histogram
    const histogram: number[] = [];
    const signalStartIndex = macdLine.length - signalLine.length;
    for (let i = 0; i < signalLine.length; i++) {
      histogram.push(macdLine[signalStartIndex + i] - signalLine[i]);
    }

    return { macdLine, signalLine, histogram };
  }

  /**
   * Find Support and Resistance levels
   */
  findSupportResistance(
    candles: OandaCandle[],
    lookback: number = 50,
    minTouches: number = 2,
    tolerance: number = 0.0015, // 0.15%
  ): SupportResistanceLevel[] {
    const levels: SupportResistanceLevel[] = [];
    const highs: number[] = [];
    const lows: number[] = [];

    // Find peaks and troughs
    for (let i = lookback; i < candles.length - lookback; i++) {
      const currentHigh = candles[i].high;
      const currentLow = candles[i].low;

      // Check if it's a peak (resistance)
      let isPeak = true;
      for (let j = i - lookback; j <= i + lookback; j++) {
        if (j !== i && candles[j].high >= currentHigh) {
          isPeak = false;
          break;
        }
      }
      if (isPeak) {
        highs.push(currentHigh);
      }

      // Check if it's a trough (support)
      let isTrough = true;
      for (let j = i - lookback; j <= i + lookback; j++) {
        if (j !== i && candles[j].low <= currentLow) {
          isTrough = false;
          break;
        }
      }
      if (isTrough) {
        lows.push(currentLow);
      }
    }

    // Group similar levels
    const groupedHighs = this.groupLevels(highs, tolerance);
    const groupedLows = this.groupLevels(lows, tolerance);

    // Create resistance levels
    for (const group of groupedHighs) {
      if (group.count >= minTouches) {
        levels.push({
          price: group.price,
          type: 'resistance',
          touches: group.count,
          strength: Math.min(100, group.count * 20), // Strength based on touches
        });
      }
    }

    // Create support levels
    for (const group of groupedLows) {
      if (group.count >= minTouches) {
        levels.push({
          price: group.price,
          type: 'support',
          touches: group.count,
          strength: Math.min(100, group.count * 20),
        });
      }
    }

    return levels.sort((a, b) => b.strength - a.strength);
  }

  /**
   * Group similar price levels
   */
  private groupLevels(prices: number[], tolerance: number): Array<{ price: number; count: number }> {
    const groups: Array<{ price: number; count: number }> = [];

    for (const price of prices) {
      let found = false;
      for (const group of groups) {
        const diff = Math.abs(price - group.price) / group.price;
        if (diff <= tolerance) {
          group.count++;
          group.price = (group.price * (group.count - 1) + price) / group.count; // Average
          found = true;
          break;
        }
      }
      if (!found) {
        groups.push({ price, count: 1 });
      }
    }

    return groups;
  }

  /**
   * Detect Price Action patterns
   */
  detectPriceActionPatterns(candles: OandaCandle[]): Array<{ pattern: string; index: number; bullish: boolean }> {
    const patterns: Array<{ pattern: string; index: number; bullish: boolean }> = [];

    for (let i = 1; i < candles.length; i++) {
      const prev = candles[i - 1];
      const current = candles[i];

      // Bullish Engulfing
      if (prev.close < prev.open && current.close > current.open && 
          current.open < prev.close && current.close > prev.open) {
        patterns.push({ pattern: 'Bullish Engulfing', index: i, bullish: true });
      }

      // Bearish Engulfing
      if (prev.close > prev.open && current.close < current.open && 
          current.open > prev.close && current.close < prev.open) {
        patterns.push({ pattern: 'Bearish Engulfing', index: i, bullish: false });
      }

      // Hammer (Bullish)
      const body = Math.abs(current.close - current.open);
      const lowerShadow = Math.min(current.open, current.close) - current.low;
      const upperShadow = current.high - Math.max(current.open, current.close);
      if (lowerShadow > body * 2 && upperShadow < body * 0.5 && current.close > current.open) {
        patterns.push({ pattern: 'Hammer', index: i, bullish: true });
      }

      // Shooting Star (Bearish)
      if (upperShadow > body * 2 && lowerShadow < body * 0.5 && current.close < current.open) {
        patterns.push({ pattern: 'Shooting Star', index: i, bullish: false });
      }

      // Pin Bar Bullish
      if (lowerShadow > body * 3 && upperShadow < body * 0.3) {
        patterns.push({ pattern: 'Pin Bar Bullish', index: i, bullish: true });
      }

      // Pin Bar Bearish
      if (upperShadow > body * 3 && lowerShadow < body * 0.3) {
        patterns.push({ pattern: 'Pin Bar Bearish', index: i, bullish: false });
      }

      // Doji
      if (body < (current.high - current.low) * 0.1) {
        patterns.push({ pattern: 'Doji', index: i, bullish: false }); // Neutral
      }
    }

    return patterns;
  }
}

