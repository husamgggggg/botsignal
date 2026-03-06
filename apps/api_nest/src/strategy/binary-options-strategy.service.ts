import { Injectable, Logger } from '@nestjs/common';
import { OandaService, OandaCandle } from '../oanda/oanda.service';
import {
  TechnicalIndicatorsService,
  ADXValues,
  StochasticValues,
  BollingerBands,
  ATRValues,
} from '../technical-indicators/technical-indicators.service';
import { Direction } from '@prisma/client';

/**
 * Binary Options Signal Analysis Result
 */
export interface BinarySignalAnalysis {
  direction: Direction | null;
  confidence: number; // 0-100
  strategy: string;
  confirmations: {
    trend: boolean;
    momentum: boolean;
    volatility: boolean;
    supportResistance: boolean;
    marketStructure: boolean;
  };
  details: {
    trendStrength?: number; // ADX value
    rsiValue?: number;
    stochasticK?: number;
    stochasticD?: number;
    macdHistogram?: number;
    bollingerSqueeze?: boolean;
    atrValue?: number;
    marketStructure?: 'bullish' | 'bearish' | 'sideways';
    rsiDivergence?: 'bullish' | 'bearish' | 'none';
  };
}

/**
 * Professional Binary Options Signal Engine
 * Optimized for 30s - 5m expiry trading
 * Target: 70-80% accuracy
 */
@Injectable()
export class BinaryOptionsStrategyService {
  private readonly logger = new Logger(BinaryOptionsStrategyService.name);

  constructor(
    private oandaService: OandaService,
    private technicalIndicators: TechnicalIndicatorsService,
  ) {}

  /**
   * Main analysis method - analyzes instrument and returns signal
   */
  async analyzeInstrument(instrument: string): Promise<BinarySignalAnalysis> {
    try {
      // Get candles (M1 timeframe, 200 candles for indicators)
      const candles = await this.oandaService.getCandles(instrument, 'M1', 200);

      if (candles.length < 100) {
        this.logger.warn(`Not enough candles for ${instrument}: ${candles.length}`);
        return this.createEmptyAnalysis();
      }

      return this.analyzeBinarySignal(instrument, candles);
    } catch (error: any) {
      this.logger.error(`Failed to analyze ${instrument}: ${error.message}`);
      return this.createEmptyAnalysis();
    }
  }

  /**
   * Core Binary Options Signal Analysis
   */
  private analyzeBinarySignal(
    instrument: string,
    candles: OandaCandle[],
  ): BinarySignalAnalysis {
    const closes = candles.map((c) => c.close);
    const highs = candles.map((c) => c.high);
    const lows = candles.map((c) => c.low);
    const currentPrice = closes[closes.length - 1];
    const currentCandle = candles[candles.length - 1];
    const prevCandle = candles.length > 1 ? candles[candles.length - 2] : undefined;

    // ============================================
    // MARKET ANALYSIS LAYER
    // ============================================

    // 1. Trend Detection (EMA 20, 50, 100 instead of 200 for shorter timeframe)
    const ema20 = this.technicalIndicators.calculateEMA(closes, 20);
    const ema50 = this.technicalIndicators.calculateEMA(closes, 50);
    const ema100 = this.technicalIndicators.calculateEMA(closes, 100); // Use 100 instead of 200 for M1

    const ema20Last = ema20[ema20.length - 1];
    const ema50Last = ema50[ema50.length - 1];
    const ema100Last = ema100[ema100.length - 1];

    // Trend alignment (use 100 instead of 200)
    const bullishTrend = currentPrice > ema20Last && ema20Last > ema50Last && ema50Last > ema100Last;
    const bearishTrend = currentPrice < ema20Last && ema20Last < ema50Last && ema50Last < ema100Last;

    // 2. Trend Strength (ADX)
    const adx = this.technicalIndicators.calculateADX(candles, 14);
    const adxLast = adx.adx[adx.adx.length - 1] || 0;
    const plusDILast = adx.plusDI[adx.plusDI.length - 1] || 0;
    const minusDILast = adx.minusDI[adx.minusDI.length - 1] || 0;

    const strongTrend = adxLast > 25; // ADX > 25 indicates strong trend
    const trendDirection = plusDILast > minusDILast ? 'bullish' : 'bearish';

    // 3. Market Structure
    const marketStructure = this.technicalIndicators.detectMarketStructure(candles, 20);

    // ============================================
    // MOMENTUM LAYER
    // ============================================

    // 1. RSI
    const rsi = this.technicalIndicators.calculateRSI(closes, 14);
    const rsiLast = rsi[rsi.length - 1] || 50;

    // 2. RSI Divergence
    const rsiDivergence = this.technicalIndicators.detectRSIDivergence(closes, rsi, 20);

    // 3. Stochastic
    const stochastic = this.technicalIndicators.calculateStochastic(candles, 14, 3);
    const stochasticKLast = stochastic.k[stochastic.k.length - 1] || 50;
    const stochasticDLast = stochastic.d[stochastic.d.length - 1] || 50;
    const stochasticKPrev = stochastic.k[stochastic.k.length - 2] || 50;
    const stochasticDPrev = stochastic.d[stochastic.d.length - 2] || 50;

    // Stochastic crossover
    const stochasticBullish = stochasticKLast > stochasticDLast && stochasticKPrev <= stochasticDPrev;
    const stochasticBearish = stochasticKLast < stochasticDLast && stochasticKPrev >= stochasticDPrev;

    // 4. MACD
    const macd = this.technicalIndicators.calculateMACD(closes, 12, 26, 9);
    const macdHistogramLast = macd.histogram[macd.histogram.length - 1] || 0;
    const macdHistogramPrev = macd.histogram[macd.histogram.length - 2] || 0;

    // MACD momentum shift
    const macdBullish = macdHistogramLast > 0 && macdHistogramLast > macdHistogramPrev;
    const macdBearish = macdHistogramLast < 0 && macdHistogramLast < macdHistogramPrev;

    // ============================================
    // VOLATILITY LAYER
    // ============================================

    // 1. Bollinger Bands
    const bollinger = this.technicalIndicators.calculateBollingerBands(closes, 20, 2);
    const bollingerUpperLast = bollinger.upper[bollinger.upper.length - 1];
    const bollingerLowerLast = bollinger.lower[bollinger.lower.length - 1];
    const bollingerMiddleLast = bollinger.middle[bollinger.middle.length - 1];
    const bollingerBandwidthLast = bollinger.bandwidth[bollinger.bandwidth.length - 1] || 0;

    // Bollinger Squeeze (low volatility - potential breakout)
    const bollingerSqueeze = bollingerBandwidthLast < 0.01; // 1% bandwidth threshold

    // Breakout detection
    const bollingerBreakoutUp = currentPrice > bollingerUpperLast;
    const bollingerBreakoutDown = currentPrice < bollingerLowerLast;

    // 2. ATR (Average True Range)
    const atr = this.technicalIndicators.calculateATR(candles, 14);
    const atrLast = atr.atr[atr.atr.length - 1] || 0;
    const atrPercent = (atrLast / currentPrice) * 100;

    // Filter: Avoid signals during very low volatility (sideways market)
    const lowVolatility = atrPercent < 0.05; // Less than 0.05% ATR

    // ============================================
    // SUPPORT & RESISTANCE LAYER
    // ============================================

    const supportResistance = this.technicalIndicators.findSupportResistance(candles, 50, 2, 0.0015);
    const nearestSupport = this.technicalIndicators.getNearestSupport(currentPrice, supportResistance);
    const nearestResistance = this.technicalIndicators.getNearestResistance(currentPrice, supportResistance);

    // Rejection detection (price bounces off support/resistance)
    const supportRejection =
      nearestSupport !== null &&
      Math.abs(currentPrice - nearestSupport) / nearestSupport < 0.002 && // Within 0.2%
      currentCandle.close > currentCandle.open; // Bullish candle

    const resistanceRejection =
      nearestResistance !== null &&
      Math.abs(currentPrice - nearestResistance) / nearestResistance < 0.002 && // Within 0.2%
      currentCandle.close < currentCandle.open; // Bearish candle

    // ============================================
    // SIGNAL LOGIC - CALL SIGNAL
    // ============================================

    const callConfirmations = {
      trend: bullishTrend && strongTrend && trendDirection === 'bullish',
      momentum:
        (rsiLast >= 30 && rsiLast <= 70 && rsiLast > 50) || // RSI recovery from oversold
        rsiDivergence.type === 'bullish' ||
        (stochasticBullish && stochasticKLast < 80) || // Stochastic crossover, not overbought
        macdBullish,
      volatility: bollingerBreakoutUp || (bollingerSqueeze && currentPrice > bollingerMiddleLast),
      supportResistance: supportRejection || (nearestResistance !== null && currentPrice > nearestResistance * 0.998),
      marketStructure: marketStructure.structure === 'bullish',
    };

    const callConfirmationCount = Object.values(callConfirmations).filter((v) => v).length;

    this.logger.debug(
      `${instrument} CALL Confirmations: ${callConfirmationCount}/5 - ` +
      `Trend:${callConfirmations.trend} Momentum:${callConfirmations.momentum} ` +
      `Volatility:${callConfirmations.volatility} S/R:${callConfirmations.supportResistance} ` +
      `MarketStructure:${callConfirmations.marketStructure}`
    );

    // ============================================
    // SIGNAL LOGIC - PUT SIGNAL
    // ============================================

    const putConfirmations = {
      trend: bearishTrend && strongTrend && trendDirection === 'bearish',
      momentum:
        (rsiLast >= 30 && rsiLast <= 70 && rsiLast < 50) || // RSI rejection from overbought
        rsiDivergence.type === 'bearish' ||
        (stochasticBearish && stochasticKLast > 20) || // Stochastic crossover, not oversold
        macdBearish,
      volatility: bollingerBreakoutDown || (bollingerSqueeze && currentPrice < bollingerMiddleLast),
      supportResistance: resistanceRejection || (nearestSupport !== null && currentPrice < nearestSupport * 1.002),
      marketStructure: marketStructure.structure === 'bearish',
    };

    const putConfirmationCount = Object.values(putConfirmations).filter((v) => v).length;

    this.logger.debug(
      `${instrument} PUT Confirmations: ${putConfirmationCount}/5 - ` +
      `Trend:${putConfirmations.trend} Momentum:${putConfirmations.momentum} ` +
      `Volatility:${putConfirmations.volatility} S/R:${putConfirmations.supportResistance} ` +
      `MarketStructure:${putConfirmations.marketStructure}`
    );

    // ============================================
    // FILTER: Avoid sideways markets
    // ============================================

    if (lowVolatility && !bollingerSqueeze) {
      this.logger.debug(`${instrument}: Low volatility detected (ATR: ${atrPercent.toFixed(4)}%), skipping signal`);
      return this.createEmptyAnalysis();
    }

    // Log detailed analysis for debugging
    this.logger.debug(
      `${instrument} Analysis - ` +
      `Trend: ${bullishTrend ? 'BULL' : bearishTrend ? 'BEAR' : 'NONE'} (ADX: ${adxLast.toFixed(1)}, Strong: ${strongTrend}), ` +
      `RSI: ${rsiLast.toFixed(1)}, Stochastic: K=${stochasticKLast.toFixed(1)} D=${stochasticDLast.toFixed(1)}, ` +
      `MACD Hist: ${macdHistogramLast.toFixed(5)}, ` +
      `BB Squeeze: ${bollingerSqueeze}, ATR: ${atrPercent.toFixed(4)}%, ` +
      `Market Structure: ${marketStructure.structure} (${marketStructure.strength.toFixed(1)})`
    );

    // ============================================
    // CONFIDENCE CALCULATION
    // ============================================

    // Minimum 3 confirmations required
    const minConfirmations = 3;

    if (callConfirmationCount >= minConfirmations && callConfirmationCount > putConfirmationCount) {
      const confidence = this.calculateConfidence(callConfirmations, {
        adx: adxLast,
        rsi: rsiLast,
        stochasticK: stochasticKLast,
        macdHistogram: macdHistogramLast,
        bollingerBandwidth: bollingerBandwidthLast,
        marketStructureStrength: marketStructure.strength,
        rsiDivergenceStrength: rsiDivergence.strength,
      });

      this.logger.debug(`${instrument} CALL Confidence calculated: ${confidence}%`);
      
      if (confidence >= 70) {
        this.logger.log(`${instrument} ✅ CALL signal generated: ${confidence}% confidence`);
        return {
          direction: Direction.CALL,
          confidence,
          strategy: 'Binary Options Professional',
          confirmations: callConfirmations,
          details: {
            trendStrength: adxLast,
            rsiValue: rsiLast,
            stochasticK: stochasticKLast,
            stochasticD: stochasticDLast,
            macdHistogram: macdHistogramLast,
            bollingerSqueeze,
            atrValue: atrPercent,
            marketStructure: marketStructure.structure,
            rsiDivergence: rsiDivergence.type,
          },
        };
      }
    }

    if (putConfirmationCount >= minConfirmations && putConfirmationCount > callConfirmationCount) {
      const confidence = this.calculateConfidence(putConfirmations, {
        adx: adxLast,
        rsi: rsiLast,
        stochasticK: stochasticKLast,
        macdHistogram: macdHistogramLast,
        bollingerBandwidth: bollingerBandwidthLast,
        marketStructureStrength: marketStructure.strength,
        rsiDivergenceStrength: rsiDivergence.strength,
      });

      this.logger.debug(`${instrument} PUT Confidence calculated: ${confidence}%`);
      
      if (confidence >= 70) {
        this.logger.log(`${instrument} ✅ PUT signal generated: ${confidence}% confidence`);
        return {
          direction: Direction.PUT,
          confidence,
          strategy: 'Binary Options Professional',
          confirmations: putConfirmations,
          details: {
            trendStrength: adxLast,
            rsiValue: rsiLast,
            stochasticK: stochasticKLast,
            stochasticD: stochasticDLast,
            macdHistogram: macdHistogramLast,
            bollingerSqueeze,
            atrValue: atrPercent,
            marketStructure: marketStructure.structure,
            rsiDivergence: rsiDivergence.type,
          },
        };
      }
    }

    // No signal
    const maxConfirmationCount = Math.max(callConfirmationCount, putConfirmationCount);
    if (maxConfirmationCount > 0) {
      this.logger.debug(
        `${instrument} ❌ No signal: Max confirmations=${maxConfirmationCount}/${minConfirmations} ` +
        `(CALL:${callConfirmationCount}, PUT:${putConfirmationCount})`
      );
    }
    return this.createEmptyAnalysis();
  }

  /**
   * Calculate Confidence Score (0-100%)
   * Based on confirmations and indicator strength
   */
  private calculateConfidence(
    confirmations: Record<string, boolean>,
    indicators: {
      adx: number;
      rsi: number;
      stochasticK: number;
      macdHistogram: number;
      bollingerBandwidth: number;
      marketStructureStrength: number;
      rsiDivergenceStrength: number;
    },
  ): number {
    // Base confidence: 15 points per confirmation
    let confidence = Object.values(confirmations).filter((v) => v).length * 15;

    // Trend strength bonus (ADX)
    if (confirmations.trend) {
      confidence += Math.min(20, (indicators.adx / 50) * 20); // Up to 20 points
    }

    // Momentum strength bonus
    if (confirmations.momentum) {
      // RSI strength (closer to ideal = better)
      const rsiStrength = indicators.rsi > 50
        ? Math.min(10, (70 - Math.abs(indicators.rsi - 60)) * 0.5) // Bullish: ideal around 60
        : Math.min(10, (70 - Math.abs(indicators.rsi - 40)) * 0.5); // Bearish: ideal around 40

      // Stochastic strength
      const stochasticStrength = Math.min(5, Math.abs(indicators.stochasticK - 50) / 10);

      // MACD strength
      const macdStrength = Math.min(5, Math.abs(indicators.macdHistogram) * 1000);

      confidence += rsiStrength + stochasticStrength + macdStrength;
    }

    // Volatility bonus (breakout strength)
    if (confirmations.volatility) {
      const volatilityStrength = indicators.bollingerBandwidth < 0.01
        ? 10 // Squeeze breakout
        : Math.min(10, indicators.bollingerBandwidth * 1000); // Regular breakout
      confidence += volatilityStrength;
    }

    // Market structure bonus
    if (confirmations.marketStructure) {
      confidence += Math.min(10, indicators.marketStructureStrength);
    }

    // RSI Divergence bonus
    if (indicators.rsiDivergenceStrength > 0) {
      confidence += Math.min(10, indicators.rsiDivergenceStrength);
    }

    // Cap at 100%
    return Math.min(100, Math.round(confidence));
  }

  /**
   * Create empty analysis result
   */
  private createEmptyAnalysis(): BinarySignalAnalysis {
    return {
      direction: null,
      confidence: 0,
      strategy: 'Binary Options Professional',
      confirmations: {
        trend: false,
        momentum: false,
        volatility: false,
        supportResistance: false,
        marketStructure: false,
      },
      details: {},
    };
  }
}

