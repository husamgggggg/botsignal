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

export interface ADXValues {
  adx: number[];
  plusDI: number[]; // +DI
  minusDI: number[]; // -DI
}

export interface StochasticValues {
  k: number[]; // %K
  d: number[]; // %D
}

export interface BollingerBands {
  upper: number[];
  middle: number[]; // SMA
  lower: number[];
  bandwidth: number[]; // (upper - lower) / middle
}

export interface ATRValues {
  atr: number[];
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
   * Get nearest support level below price
   */
  getNearestSupport(price: number, supportLevels: SupportResistanceLevel[]): number | null {
    const belowPrice = supportLevels
      .filter((s) => s.type === 'support' && s.price < price)
      .map((s) => s.price);
    if (belowPrice.length === 0) {
      return null;
    }
    return Math.max(...belowPrice);
  }

  /**
   * Get nearest resistance level above price
   */
  getNearestResistance(price: number, resistanceLevels: SupportResistanceLevel[]): number | null {
    const abovePrice = resistanceLevels
      .filter((r) => r.type === 'resistance' && r.price > price)
      .map((r) => r.price);
    if (abovePrice.length === 0) {
      return null;
    }
    return Math.min(...abovePrice);
  }

  /**
   * Detect candle pattern (enhanced version from bot)
   */
  detectCandlePattern(
    currentCandle: OandaCandle,
    prevCandle?: OandaCandle,
  ): { pattern: string; bullish: boolean } {
    const body = Math.abs(currentCandle.close - currentCandle.open);
    const upperWick = currentCandle.high - Math.max(currentCandle.close, currentCandle.open);
    const lowerWick = Math.min(currentCandle.close, currentCandle.open) - currentCandle.low;
    const totalRange = currentCandle.high - currentCandle.low;

    if (totalRange === 0) {
      return { pattern: 'NONE', bullish: false };
    }

    const bodyRatio = body / totalRange;
    const upperWickRatio = upperWick / totalRange;
    const lowerWickRatio = lowerWick / totalRange;

    const isBullish = currentCandle.close > currentCandle.open;
    const isBearish = currentCandle.close < currentCandle.open;

    // Pin Bar Bullish
    if (bodyRatio < 0.3 && lowerWickRatio > 0.6 && upperWickRatio < 0.2) {
      if (isBullish || Math.abs(currentCandle.close - currentCandle.open) < body * 0.3) {
        return { pattern: 'PIN_BAR_BULLISH', bullish: true };
      }
    }

    // Pin Bar Bearish
    if (bodyRatio < 0.3 && upperWickRatio > 0.6 && lowerWickRatio < 0.2) {
      if (isBearish || Math.abs(currentCandle.close - currentCandle.open) < body * 0.3) {
        return { pattern: 'PIN_BAR_BEARISH', bullish: false };
      }
    }

    // Hammer
    if (bodyRatio < 0.3 && lowerWickRatio > 0.6 && upperWickRatio < 0.3) {
      if (currentCandle.low < (currentCandle.high + currentCandle.low) / 2) {
        return { pattern: 'HAMMER', bullish: true };
      }
    }

    // Shooting Star
    if (bodyRatio < 0.3 && upperWickRatio > 0.6 && lowerWickRatio < 0.3) {
      if (currentCandle.high > (currentCandle.high + currentCandle.low) / 2) {
        return { pattern: 'SHOOTING_STAR', bullish: false };
      }
    }

    // Doji
    if (bodyRatio < 0.1) {
      return { pattern: 'DOJI', bullish: false };
    }

    // Engulfing patterns (need previous candle)
    if (prevCandle) {
      const prevBody = Math.abs(prevCandle.close - prevCandle.open);
      const prevIsBullish = prevCandle.close > prevCandle.open;
      const prevIsBearish = prevCandle.close < prevCandle.open;

      // Bullish Engulfing
      if (
        prevIsBearish &&
        isBullish &&
        body > prevBody * 1.5 &&
        currentCandle.open < prevCandle.close &&
        currentCandle.close > prevCandle.open
      ) {
        return { pattern: 'BULLISH_ENGULFING', bullish: true };
      }

      // Bearish Engulfing
      if (
        prevIsBullish &&
        isBearish &&
        body > prevBody * 1.5 &&
        currentCandle.open > prevCandle.close &&
        currentCandle.close < prevCandle.open
      ) {
        return { pattern: 'BEARISH_ENGULFING', bullish: false };
      }
    }

    return { pattern: 'NONE', bullish: false };
  }

  /**
   * Find Support and Resistance levels (enhanced from bot)
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

  /**
   * Calculate ATR (Average True Range)
   * Measures market volatility
   */
  calculateATR(candles: OandaCandle[], period: number = 14): ATRValues {
    if (candles.length < period + 1) {
      return { atr: [] };
    }

    const trueRanges: number[] = [];

    // Calculate True Range for each candle
    for (let i = 1; i < candles.length; i++) {
      const high = candles[i].high;
      const low = candles[i].low;
      const prevClose = candles[i - 1].close;

      const tr1 = high - low;
      const tr2 = Math.abs(high - prevClose);
      const tr3 = Math.abs(low - prevClose);

      trueRanges.push(Math.max(tr1, tr2, tr3));
    }

    // Calculate ATR using Wilder's smoothing
    const atr: number[] = [];
    let sum = 0;
    for (let i = 0; i < period; i++) {
      sum += trueRanges[i];
    }
    atr[period - 1] = sum / period;

    for (let i = period; i < trueRanges.length; i++) {
      atr[i] = (atr[i - 1] * (period - 1) + trueRanges[i]) / period;
    }

    return { atr };
  }

  /**
   * Calculate ADX (Average Directional Index)
   * Measures trend strength (0-100, >25 = strong trend)
   */
  calculateADX(candles: OandaCandle[], period: number = 14): ADXValues {
    if (candles.length < period * 2) {
      return { adx: [], plusDI: [], minusDI: [] };
    }

    const plusDM: number[] = [];
    const minusDM: number[] = [];
    const tr: number[] = [];

    // Calculate +DM, -DM, and TR
    for (let i = 1; i < candles.length; i++) {
      const highDiff = candles[i].high - candles[i - 1].high;
      const lowDiff = candles[i - 1].low - candles[i].low;

      plusDM.push(highDiff > lowDiff && highDiff > 0 ? highDiff : 0);
      minusDM.push(lowDiff > highDiff && lowDiff > 0 ? lowDiff : 0);

      const tr1 = candles[i].high - candles[i].low;
      const tr2 = Math.abs(candles[i].high - candles[i - 1].close);
      const tr3 = Math.abs(candles[i].low - candles[i - 1].close);
      tr.push(Math.max(tr1, tr2, tr3));
    }

    // Calculate smoothed +DI and -DI
    const plusDI: number[] = [];
    const minusDI: number[] = [];
    const dx: number[] = [];

    // Initial values (SMA)
    let plusDMSum = 0;
    let minusDMSum = 0;
    let trSum = 0;

    for (let i = 0; i < period; i++) {
      plusDMSum += plusDM[i];
      minusDMSum += minusDM[i];
      trSum += tr[i];
    }

    let plusDIAvg = (plusDMSum / trSum) * 100;
    let minusDIAvg = (minusDMSum / trSum) * 100;

    plusDI[period - 1] = plusDIAvg;
    minusDI[period - 1] = minusDIAvg;

    // Calculate DX
    const diSum = plusDIAvg + minusDIAvg;
    dx[period - 1] = diSum > 0 ? (Math.abs(plusDIAvg - minusDIAvg) / diSum) * 100 : 0;

    // Calculate subsequent values using Wilder's smoothing
    for (let i = period; i < plusDM.length; i++) {
      plusDMSum = (plusDMSum * (period - 1)) / period + plusDM[i];
      minusDMSum = (minusDMSum * (period - 1)) / period + minusDM[i];
      trSum = (trSum * (period - 1)) / period + tr[i];

      plusDIAvg = (plusDMSum / trSum) * 100;
      minusDIAvg = (minusDMSum / trSum) * 100;

      plusDI[i] = plusDIAvg;
      minusDI[i] = minusDIAvg;

      const diSumCurrent = plusDIAvg + minusDIAvg;
      dx[i] = diSumCurrent > 0 ? (Math.abs(plusDIAvg - minusDIAvg) / diSumCurrent) * 100 : 0;
    }

    // Calculate ADX (smoothed DX)
    const adx: number[] = [];
    let adxSum = 0;
    for (let i = period - 1; i < period * 2 - 1 && i < dx.length; i++) {
      adxSum += dx[i];
    }
    adx[period * 2 - 2] = adxSum / period;

    for (let i = period * 2 - 1; i < dx.length; i++) {
      adx[i] = (adx[i - 1] * (period - 1) + dx[i]) / period;
    }

    return { adx, plusDI, minusDI };
  }

  /**
   * Calculate Stochastic Oscillator
   * %K = ((Current Close - Lowest Low) / (Highest High - Lowest Low)) * 100
   * %D = 3-period SMA of %K
   */
  calculateStochastic(
    candles: OandaCandle[],
    kPeriod: number = 14,
    dPeriod: number = 3,
  ): StochasticValues {
    if (candles.length < kPeriod + dPeriod) {
      return { k: [], d: [] };
    }

    const k: number[] = [];

    // Calculate %K
    for (let i = kPeriod - 1; i < candles.length; i++) {
      const periodCandles = candles.slice(i - kPeriod + 1, i + 1);
      const highestHigh = Math.max(...periodCandles.map((c) => c.high));
      const lowestLow = Math.min(...periodCandles.map((c) => c.low));
      const currentClose = candles[i].close;

      const range = highestHigh - lowestLow;
      if (range === 0) {
        k.push(50); // Neutral if no range
      } else {
        k.push(((currentClose - lowestLow) / range) * 100);
      }
    }

    // Calculate %D (SMA of %K)
    const d = this.calculateSMA(k, dPeriod);

    // Align arrays (k starts at index kPeriod-1, d starts later)
    const kAligned = new Array(kPeriod - 1).fill(NaN).concat(k);
    const dAligned = new Array(kPeriod + dPeriod - 2).fill(NaN).concat(d);

    return { k: kAligned, d: dAligned };
  }

  /**
   * Calculate SMA (Simple Moving Average) - helper for Stochastic
   */
  private calculateSMA(values: number[], period: number): number[] {
    if (values.length < period) {
      return [];
    }

    const sma: number[] = [];
    for (let i = period - 1; i < values.length; i++) {
      let sum = 0;
      for (let j = i - period + 1; j <= i; j++) {
        sum += values[j];
      }
      sma.push(sum / period);
    }

    return sma;
  }

  /**
   * Calculate Bollinger Bands
   * Upper = SMA + (StdDev * multiplier)
   * Lower = SMA - (StdDev * multiplier)
   */
  calculateBollingerBands(
    prices: number[],
    period: number = 20,
    multiplier: number = 2,
  ): BollingerBands {
    if (prices.length < period) {
      return { upper: [], middle: [], lower: [], bandwidth: [] };
    }

    const middle: number[] = [];
    const upper: number[] = [];
    const lower: number[] = [];
    const bandwidth: number[] = [];

    for (let i = period - 1; i < prices.length; i++) {
      const periodPrices = prices.slice(i - period + 1, i + 1);
      const sma = periodPrices.reduce((sum, p) => sum + p, 0) / period;

      // Calculate standard deviation
      const variance = periodPrices.reduce((sum, p) => sum + Math.pow(p - sma, 2), 0) / period;
      const stdDev = Math.sqrt(variance);

      const upperBand = sma + stdDev * multiplier;
      const lowerBand = sma - stdDev * multiplier;

      middle.push(sma);
      upper.push(upperBand);
      lower.push(lowerBand);
      bandwidth.push((upperBand - lowerBand) / sma);
    }

    // Align arrays
    const alignedMiddle = new Array(period - 1).fill(NaN).concat(middle);
    const alignedUpper = new Array(period - 1).fill(NaN).concat(upper);
    const alignedLower = new Array(period - 1).fill(NaN).concat(lower);
    const alignedBandwidth = new Array(period - 1).fill(NaN).concat(bandwidth);

    return {
      upper: alignedUpper,
      middle: alignedMiddle,
      lower: alignedLower,
      bandwidth: alignedBandwidth,
    };
  }

  /**
   * Detect RSI Divergence
   * Bullish: Price makes lower low, RSI makes higher low
   * Bearish: Price makes higher high, RSI makes lower high
   */
  detectRSIDivergence(
    prices: number[],
    rsi: number[],
    lookback: number = 20,
  ): { type: 'bullish' | 'bearish' | 'none'; strength: number } {
    if (prices.length < lookback * 2 || rsi.length < lookback * 2) {
      return { type: 'none', strength: 0 };
    }

    const recentPrices = prices.slice(-lookback);
    const recentRSI = rsi.slice(-lookback);

    // Find price peaks and troughs
    const pricePeaks: number[] = [];
    const priceTroughs: number[] = [];
    const rsiPeaks: number[] = [];
    const rsiTroughs: number[] = [];

    for (let i = 2; i < recentPrices.length - 2; i++) {
      // Price peak
      if (
        recentPrices[i] > recentPrices[i - 1] &&
        recentPrices[i] > recentPrices[i - 2] &&
        recentPrices[i] > recentPrices[i + 1] &&
        recentPrices[i] > recentPrices[i + 2]
      ) {
        pricePeaks.push(recentPrices[i]);
        rsiPeaks.push(recentRSI[i]);
      }

      // Price trough
      if (
        recentPrices[i] < recentPrices[i - 1] &&
        recentPrices[i] < recentPrices[i - 2] &&
        recentPrices[i] < recentPrices[i + 1] &&
        recentPrices[i] < recentPrices[i + 2]
      ) {
        priceTroughs.push(recentPrices[i]);
        rsiTroughs.push(recentRSI[i]);
      }
    }

    // Check for bullish divergence (price lower low, RSI higher low)
    if (priceTroughs.length >= 2 && rsiTroughs.length >= 2) {
      const lastPriceTrough = priceTroughs[priceTroughs.length - 1];
      const prevPriceTrough = priceTroughs[priceTroughs.length - 2];
      const lastRSITrough = rsiTroughs[rsiTroughs.length - 1];
      const prevRSITrough = rsiTroughs[rsiTroughs.length - 2];

      if (lastPriceTrough < prevPriceTrough && lastRSITrough > prevRSITrough) {
        const strength = Math.min(100, Math.abs(lastPriceTrough - prevPriceTrough) * 1000);
        return { type: 'bullish', strength };
      }
    }

    // Check for bearish divergence (price higher high, RSI lower high)
    if (pricePeaks.length >= 2 && rsiPeaks.length >= 2) {
      const lastPricePeak = pricePeaks[pricePeaks.length - 1];
      const prevPricePeak = pricePeaks[pricePeaks.length - 2];
      const lastRSIPeak = rsiPeaks[rsiPeaks.length - 1];
      const prevRSIPeak = rsiPeaks[rsiPeaks.length - 2];

      if (lastPricePeak > prevPricePeak && lastRSIPeak < prevRSIPeak) {
        const strength = Math.min(100, Math.abs(lastPricePeak - prevPricePeak) * 1000);
        return { type: 'bearish', strength };
      }
    }

    return { type: 'none', strength: 0 };
  }

  /**
   * Detect Market Structure (Higher Highs / Lower Lows)
   * Returns: 'bullish' | 'bearish' | 'sideways'
   */
  detectMarketStructure(candles: OandaCandle[], lookback: number = 20): {
    structure: 'bullish' | 'bearish' | 'sideways';
    strength: number;
  } {
    if (candles.length < lookback * 2) {
      return { structure: 'sideways', strength: 0 };
    }

    const recentCandles = candles.slice(-lookback);
    const highs = recentCandles.map((c) => c.high);
    const lows = recentCandles.map((c) => c.low);

    // Find peaks and troughs
    const peaks: number[] = [];
    const troughs: number[] = [];

    for (let i = 2; i < recentCandles.length - 2; i++) {
      if (
        highs[i] > highs[i - 1] &&
        highs[i] > highs[i - 2] &&
        highs[i] > highs[i + 1] &&
        highs[i] > highs[i + 2]
      ) {
        peaks.push(highs[i]);
      }

      if (
        lows[i] < lows[i - 1] &&
        lows[i] < lows[i - 2] &&
        lows[i] < lows[i + 1] &&
        lows[i] < lows[i + 2]
      ) {
        troughs.push(lows[i]);
      }
    }

    // Check for higher highs and higher lows (bullish)
    if (peaks.length >= 2 && troughs.length >= 2) {
      const lastPeak = peaks[peaks.length - 1];
      const prevPeak = peaks[peaks.length - 2];
      const lastTrough = troughs[troughs.length - 1];
      const prevTrough = troughs[troughs.length - 2];

      if (lastPeak > prevPeak && lastTrough > prevTrough) {
        const strength = Math.min(100, ((lastPeak - prevPeak) / prevPeak) * 10000);
        return { structure: 'bullish', strength };
      }

      // Check for lower highs and lower lows (bearish)
      if (lastPeak < prevPeak && lastTrough < prevTrough) {
        const strength = Math.min(100, ((prevTrough - lastTrough) / prevTrough) * 10000);
        return { structure: 'bearish', strength };
      }
    }

    return { structure: 'sideways', strength: 0 };
  }
}

