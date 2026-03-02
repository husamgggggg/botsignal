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
   * Advanced Multi-Indicator Strategy (Default - Strongest)
   * Requires confirmation from at least 4 out of 5 indicators
   */
  async analyzeAdvancedMultiIndicator(
    instrument: string,
    candles: OandaCandle[],
  ): Promise<StrategyAnalysis> {
    if (candles.length < 100) {
      return {
        direction: null,
        confidence: 0,
        strategy: 'Advanced Multi-Indicator',
        indicators: { macd: false, rsi: false, ema: false, supportResistance: false, priceAction: false },
        details: {},
      };
    }

    const closes = candles.map((c) => c.close);
    const currentPrice = closes[closes.length - 1];

    // Calculate indicators
    const emas = this.technicalIndicators.calculateEMAs(candles);
    const rsi = this.technicalIndicators.calculateRSI(closes);
    const macd = this.technicalIndicators.calculateMACD(closes);
    const supportResistance = this.technicalIndicators.findSupportResistance(candles);
    const priceAction = this.technicalIndicators.detectPriceActionPatterns(candles);

    // Get latest values
    const lastIndex = closes.length - 1;
    const ema10Last = emas.ema10[emas.ema10.length - 1];
    const ema20Last = emas.ema20[emas.ema20.length - 1];
    const ema50Last = emas.ema50[emas.ema50.length - 1];
    const rsiLast = rsi[rsi.length - 1];
    const macdLineLast = macd.macdLine[macd.macdLine.length - 1];
    const signalLineLast = macd.signalLine[macd.signalLine.length - 1];
    const histogramLast = macd.histogram[macd.histogram.length - 1];

    // Check indicators for BUY
    let buyIndicators = 0;
    const buyDetails: any = {};

    // MACD check
    if (macdLineLast > signalLineLast && macdLineLast > 0 && histogramLast > 0) {
      buyIndicators++;
      buyDetails.macdStatus = 'Bullish';
    }

    // RSI check (45-70 for buy)
    if (rsiLast >= 45 && rsiLast <= 70) {
      buyIndicators++;
      buyDetails.rsiValue = rsiLast;
    }

    // EMA check
    if (currentPrice > ema10Last && ema10Last > ema20Last && ema20Last > ema50Last) {
      buyIndicators++;
      buyDetails.emaStatus = 'Uptrend';
    }

    // Support/Resistance check
    const nearSupport = supportResistance
      .filter((level) => level.type === 'support')
      .some((level) => Math.abs(currentPrice - level.price) / level.price <= 0.0015);
    if (nearSupport) {
      buyIndicators++;
      buyDetails.supportResistanceStatus = 'Near Support';
    }

    // Price Action check
    const recentBullishPattern = priceAction
      .filter((p) => p.index >= candles.length - 6 && p.bullish)
      .length > 0;
    if (recentBullishPattern) {
      buyIndicators++;
      buyDetails.priceActionPattern = 'Bullish Pattern';
    }

    // Check indicators for SELL
    let sellIndicators = 0;
    const sellDetails: any = {};

    // MACD check
    if (macdLineLast < signalLineLast && macdLineLast < 0 && histogramLast < 0) {
      sellIndicators++;
      sellDetails.macdStatus = 'Bearish';
    }

    // RSI check (30-55 for sell)
    if (rsiLast >= 30 && rsiLast <= 55) {
      sellIndicators++;
      sellDetails.rsiValue = rsiLast;
    }

    // EMA check
    if (currentPrice < ema10Last && ema10Last < ema20Last && ema20Last < ema50Last) {
      sellIndicators++;
      sellDetails.emaStatus = 'Downtrend';
    }

    // Support/Resistance check
    const nearResistance = supportResistance
      .filter((level) => level.type === 'resistance')
      .some((level) => Math.abs(currentPrice - level.price) / level.price <= 0.0015);
    if (nearResistance) {
      sellIndicators++;
      sellDetails.supportResistanceStatus = 'Near Resistance';
    }

    // Price Action check
    const recentBearishPattern = priceAction
      .filter((p) => p.index >= candles.length - 6 && !p.bullish)
      .length > 0;
    if (recentBearishPattern) {
      sellIndicators++;
      sellDetails.priceActionPattern = 'Bearish Pattern';
    }

    // Determine direction and confidence
    if (buyIndicators >= 4) {
      const confidence = Math.min(100, 75 + (buyIndicators - 4) * 5); // 75-100%
      return {
        direction: Direction.CALL,
        confidence,
        strategy: 'Advanced Multi-Indicator',
        indicators: {
          macd: buyDetails.macdStatus === 'Bullish',
          rsi: buyDetails.rsiValue !== undefined,
          ema: buyDetails.emaStatus === 'Uptrend',
          supportResistance: buyDetails.supportResistanceStatus !== undefined,
          priceAction: buyDetails.priceActionPattern !== undefined,
        },
        details: buyDetails,
      };
    }

    if (sellIndicators >= 4) {
      const confidence = Math.min(100, 75 + (sellIndicators - 4) * 5); // 75-100%
      return {
        direction: Direction.PUT,
        confidence,
        strategy: 'Advanced Multi-Indicator',
        indicators: {
          macd: sellDetails.macdStatus === 'Bearish',
          rsi: sellDetails.rsiValue !== undefined,
          ema: sellDetails.emaStatus === 'Downtrend',
          supportResistance: sellDetails.supportResistanceStatus !== undefined,
          priceAction: sellDetails.priceActionPattern !== undefined,
        },
        details: sellDetails,
      };
    }

    return {
      direction: null,
      confidence: Math.max(buyIndicators, sellIndicators) * 15, // Max 60% if less than 4 indicators
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

