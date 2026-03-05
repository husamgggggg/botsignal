import { Injectable, Logger } from '@nestjs/common';
import { OandaService, OandaCandle } from '../oanda/oanda.service';
import { TechnicalIndicatorsService, SupportResistanceLevel } from '../technical-indicators/technical-indicators.service';
import { Direction } from '@prisma/client';

export interface StrategyAnalysis {
  direction: Direction | null;
  confidence: number; // 0-100
  strategy: string;
  indicators: {
    macd: boolean;
    rsi: boolean;
    ema: boolean;
    supportResistance: boolean;
    priceAction: boolean;
  };
  details: {
    macdStatus?: string;
    rsiValue?: number;
    emaStatus?: string;
    supportResistanceStatus?: string;
    priceActionPattern?: string;
  };
}

@Injectable()
export class StrategyService {
  private readonly logger = new Logger(StrategyService.name);

  constructor(
    private oandaService: OandaService,
    private technicalIndicators: TechnicalIndicatorsService,
  ) {}

  /**
   * Advanced Multi-Indicator Strategy (Enhanced from bot)
   * Requires confirmation from at least 4 out of 5 indicators
   * Based on bot/src/strategies/advanced_multi_indicator.py
   */
  async analyzeAdvancedMultiIndicator(
    instrument: string,
    candles: OandaCandle[],
  ): Promise<StrategyAnalysis> {
    // Need at least 50 candles (EMA50 + some buffer)
    const minCandles = 50;
    if (candles.length < minCandles) {
      return {
        direction: null,
        confidence: 0,
        strategy: 'Advanced Multi-Indicator',
        indicators: { macd: false, rsi: false, ema: false, supportResistance: false, priceAction: false },
        details: {},
      };
    }

    const closes = candles.map((c) => c.close);
    const highs = candles.map((c) => c.high);
    const lows = candles.map((c) => c.low);
    const currentPrice = closes[closes.length - 1];
    const currentCandle = candles[candles.length - 1];
    const prevCandle = candles.length > 1 ? candles[candles.length - 2] : undefined;

    // Calculate indicators
    const emas = this.technicalIndicators.calculateEMAs(candles);
    const rsi = this.technicalIndicators.calculateRSI(closes, 14);
    const macd = this.technicalIndicators.calculateMACD(closes, 12, 26, 9);
    const supportResistance = this.technicalIndicators.findSupportResistance(candles, 50, 2, 0.15);
    const candlePattern = this.technicalIndicators.detectCandlePattern(currentCandle, prevCandle);

    // Get latest values
    const ema10Last = emas.ema10[emas.ema10.length - 1];
    const ema20Last = emas.ema20[emas.ema20.length - 1];
    const ema50Last = emas.ema50[emas.ema50.length - 1];
    const rsiLast = rsi[rsi.length - 1];
    const macdLineLast = macd.macdLine[macd.macdLine.length - 1];
    const signalLineLast = macd.signalLine[macd.signalLine.length - 1];
    const histogramLast = macd.histogram[macd.histogram.length - 1];

    // Check if all indicators are available
    if (
      ema10Last === undefined ||
      ema20Last === undefined ||
      ema50Last === undefined ||
      rsiLast === undefined ||
      macdLineLast === undefined ||
      signalLineLast === undefined ||
      histogramLast === undefined
    ) {
      return {
        direction: null,
        confidence: 0,
        strategy: 'Advanced Multi-Indicator',
        indicators: { macd: false, rsi: false, ema: false, supportResistance: false, priceAction: false },
        details: {},
      };
    }

    // Get nearest support/resistance
    const nearestSupport = this.technicalIndicators.getNearestSupport(currentPrice, supportResistance);
    const nearestResistance = this.technicalIndicators.getNearestResistance(currentPrice, supportResistance);

    // Check BUY conditions (from bot strategy)
    const buyConfirmations: Record<string, boolean> = {};

    // 1. MACD: MACD Line > Signal Line AND MACD Line > 0 AND Histogram > 0
    buyConfirmations.macd =
      macdLineLast > signalLineLast && macdLineLast > 0 && histogramLast > 0;

    // 2. RSI: بين 45-70 (تجنب الذروة)
    buyConfirmations.rsi = rsiLast >= 45 && rsiLast <= 70;

    // 3. EMA: السعر > EMA10 > EMA20 > EMA50 (ترند صاعد قوي)
    buyConfirmations.ema = currentPrice > ema10Last && ema10Last > ema20Last && ema20Last > ema50Last;

    // 4. Support/Resistance: السعر قريب من دعم (0.2% tolerance)
    buyConfirmations.supportResistance = false;
    if (nearestSupport !== null) {
      const distancePct = (Math.abs(currentPrice - nearestSupport) / nearestSupport) * 100;
      if (distancePct <= 0.2) {
        buyConfirmations.supportResistance = true;
      }
    }

    // 5. Price Action: نمط صاعد
    buyConfirmations.priceAction = candlePattern.bullish && candlePattern.pattern !== 'NONE';

    // Check SELL conditions
    const sellConfirmations: Record<string, boolean> = {};

    // 1. MACD: MACD Line < Signal Line AND MACD Line < 0 AND Histogram < 0
    sellConfirmations.macd =
      macdLineLast < signalLineLast && macdLineLast < 0 && histogramLast < 0;

    // 2. RSI: بين 30-55 (تجنب الذروة)
    sellConfirmations.rsi = rsiLast >= 30 && rsiLast <= 55;

    // 3. EMA: السعر < EMA10 < EMA20 < EMA50 (ترند هابط قوي)
    sellConfirmations.ema = currentPrice < ema10Last && ema10Last < ema20Last && ema20Last < ema50Last;

    // 4. Support/Resistance: السعر قريب من مقاومة
    sellConfirmations.supportResistance = false;
    if (nearestResistance !== null) {
      const distancePct = (Math.abs(currentPrice - nearestResistance) / nearestResistance) * 100;
      if (distancePct <= 0.2) {
        sellConfirmations.supportResistance = true;
      }
    }

    // 5. Price Action: نمط هابط
    sellConfirmations.priceAction = !candlePattern.bullish && candlePattern.pattern !== 'NONE';

    // Count confirmations
    const buyCount = Object.values(buyConfirmations).filter((v) => v).length;
    const sellCount = Object.values(sellConfirmations).filter((v) => v).length;

    const minConfirmations = 4; // Minimum required confirmations

    // Calculate confidence (enhanced from bot)
    const calculateConfidence = (
      confirmations: Record<string, boolean>,
      signalType: 'buy' | 'sell',
    ): number => {
      // Base confidence: 20 points per confirmation
      let baseConfidence = Object.values(confirmations).filter((v) => v).length * 20;

      // MACD strength (0-15 points)
      let macdStrength = 0;
      if (confirmations.macd && macdLineLast !== undefined) {
        macdStrength = Math.min(15, Math.abs(macdLineLast) * 10000);
      }

      // RSI strength (0-10 points) - closer to ideal = better
      let rsiStrength = 0;
      if (confirmations.rsi && rsiLast !== undefined) {
        const idealRsi = signalType === 'buy' ? 57.5 : 42.5; // (45+70)/2 or (30+55)/2
        const rsiDistance = Math.abs(rsiLast - idealRsi);
        rsiStrength = Math.max(0, 10 - rsiDistance * 0.4);
      }

      // EMA strength (0-10 points)
      let emaStrength = 0;
      if (confirmations.ema && ema10Last !== undefined) {
        const distancePct =
          signalType === 'buy'
            ? ((currentPrice - ema10Last) / ema10Last) * 100
            : ((ema10Last - currentPrice) / ema10Last) * 100;
        emaStrength = Math.min(10, Math.max(5, distancePct * 2));
      }

      // Support/Resistance strength (0-10 points)
      let srStrength = 0;
      if (confirmations.supportResistance) {
        const level = signalType === 'buy' ? nearestSupport : nearestResistance;
        if (level !== null) {
          const distancePct = (Math.abs(currentPrice - level) / level) * 100;
          srStrength = Math.max(0, 10 - distancePct * 50);
        }
      }

      // Price Action strength (0-5 points)
      const priceActionStrength = confirmations.priceAction ? 5 : 0;

      const totalConfidence = baseConfidence + macdStrength + rsiStrength + emaStrength + srStrength + priceActionStrength;

      // Minimum 75%, maximum 100%
      return Math.max(75, Math.min(100, Math.round(totalConfidence)));
    };

    // Determine signal
    if (buyCount >= minConfirmations && buyCount > sellCount) {
      const confidence = calculateConfidence(buyConfirmations, 'buy');
      return {
        direction: Direction.CALL,
        confidence,
        strategy: 'Advanced Multi-Indicator',
        indicators: buyConfirmations,
        details: {
          macdStatus: buyConfirmations.macd ? 'Bullish' : undefined,
          rsiValue: buyConfirmations.rsi ? rsiLast : undefined,
          emaStatus: buyConfirmations.ema ? 'Uptrend' : undefined,
          supportResistanceStatus: buyConfirmations.supportResistance ? 'Near Support' : undefined,
          priceActionPattern: buyConfirmations.priceAction ? candlePattern.pattern : undefined,
        },
      };
    }

    if (sellCount >= minConfirmations && sellCount > buyCount) {
      const confidence = calculateConfidence(sellConfirmations, 'sell');
      return {
        direction: Direction.PUT,
        confidence,
        strategy: 'Advanced Multi-Indicator',
        indicators: sellConfirmations,
        details: {
          macdStatus: sellConfirmations.macd ? 'Bearish' : undefined,
          rsiValue: sellConfirmations.rsi ? rsiLast : undefined,
          emaStatus: sellConfirmations.ema ? 'Downtrend' : undefined,
          supportResistanceStatus: sellConfirmations.supportResistance ? 'Near Resistance' : undefined,
          priceActionPattern: sellConfirmations.priceAction ? candlePattern.pattern : undefined,
        },
      };
    }

    // No signal (insufficient confirmations)
    return {
      direction: null,
      confidence: Math.max(buyCount, sellCount) * 15, // Max 60% if less than 4 indicators
      strategy: 'Advanced Multi-Indicator',
      indicators: {
        macd: false,
        rsi: false,
        ema: false,
        supportResistance: false,
        priceAction: false,
      },
      details: {},
    };
  }

  /**
   * Analyze instrument and return signal
   */
  async analyzeInstrument(instrument: string): Promise<StrategyAnalysis> {
    try {
      // Get candles (M1 timeframe, 500 candles)
      const candles = await this.oandaService.getCandles(instrument, 'M1', 500);

      if (candles.length < 100) {
        this.logger.warn(`Not enough candles for ${instrument}: ${candles.length}`);
        return {
          direction: null,
          confidence: 0,
          strategy: 'Advanced Multi-Indicator',
          indicators: { macd: false, rsi: false, ema: false, supportResistance: false, priceAction: false },
          details: {},
        };
      }

      // Use Advanced Multi-Indicator strategy (default)
      const result = await this.analyzeAdvancedMultiIndicator(instrument, candles);
      
      // Log detailed analysis for debugging
      if (result.direction) {
        this.logger.debug(
          `${instrument} Analysis: ${result.direction} signal with ${result.confidence}% confidence. ` +
          `Indicators: MACD=${result.indicators.macd}, RSI=${result.indicators.rsi}, ` +
          `EMA=${result.indicators.ema}, S/R=${result.indicators.supportResistance}, ` +
          `PriceAction=${result.indicators.priceAction}`,
        );
      }
      
      return result;
    } catch (error: any) {
      this.logger.error(`Failed to analyze ${instrument}: ${error.message}`);
      return {
        direction: null,
        confidence: 0,
        strategy: 'Advanced Multi-Indicator',
        indicators: { macd: false, rsi: false, ema: false, supportResistance: false, priceAction: false },
        details: {},
      };
    }
  }
}

