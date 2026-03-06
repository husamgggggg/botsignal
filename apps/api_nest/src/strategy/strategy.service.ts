import { Injectable, Logger } from '@nestjs/common';
import { BinaryOptionsStrategyService } from './binary-options-strategy.service';
import { Direction } from '@prisma/client';

/**
 * Legacy interface for backward compatibility
 * Maps to BinarySignalAnalysis
 */
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

/**
 * Strategy Service - Wrapper for Binary Options Strategy
 * Uses the new professional binary options signal engine
 */
@Injectable()
export class StrategyService {
  private readonly logger = new Logger(StrategyService.name);

  constructor(
    private binaryOptionsStrategy: BinaryOptionsStrategyService,
  ) {}

  /**
   * Analyze instrument and return signal
   * Uses the new Binary Options Professional Strategy
   */
  async analyzeInstrument(instrument: string): Promise<StrategyAnalysis> {
    try {
      // Use Binary Options Professional Strategy
      const result = await this.binaryOptionsStrategy.analyzeInstrument(instrument);
      
      // Convert BinarySignalAnalysis to StrategyAnalysis (legacy format)
      const legacyResult: StrategyAnalysis = {
        direction: result.direction,
        confidence: result.confidence,
        strategy: result.strategy,
        indicators: {
          macd: result.confirmations.momentum, // MACD is part of momentum
          rsi: result.confirmations.momentum, // RSI is part of momentum
          ema: result.confirmations.trend, // EMA is part of trend
          supportResistance: result.confirmations.supportResistance,
          priceAction: result.confirmations.volatility || result.confirmations.supportResistance,
        },
        details: {
          rsiValue: result.details.rsiValue,
          macdStatus: result.details.macdHistogram !== undefined
            ? (result.details.macdHistogram > 0 ? 'Bullish' : 'Bearish')
            : undefined,
          emaStatus: result.confirmations.trend
            ? (result.direction === Direction.CALL ? 'Uptrend' : 'Downtrend')
            : undefined,
          supportResistanceStatus: result.confirmations.supportResistance
            ? (result.direction === Direction.CALL ? 'Near Support' : 'Near Resistance')
            : undefined,
        },
      };
      
      // Log detailed analysis for debugging
      if (result.direction) {
        this.logger.log(
          `${instrument} Analysis: ${result.direction} signal with ${result.confidence}% confidence. ` +
          `Confirmations: Trend=${result.confirmations.trend}, Momentum=${result.confirmations.momentum}, ` +
          `Volatility=${result.confirmations.volatility}, S/R=${result.confirmations.supportResistance}, ` +
          `MarketStructure=${result.confirmations.marketStructure}`,
        );
      }
      
      return legacyResult;
    } catch (error: any) {
      this.logger.error(`Failed to analyze ${instrument}: ${error.message}`);
      return {
        direction: null,
        confidence: 0,
        strategy: 'Binary Options Professional',
        indicators: { macd: false, rsi: false, ema: false, supportResistance: false, priceAction: false },
        details: {},
      };
    }
  }
}
