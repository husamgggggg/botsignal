import { Injectable, Logger } from '@nestjs/common';
import { Cron } from '@nestjs/schedule';
import { PrismaService } from '../prisma/prisma.service';
import { StrategyService } from '../strategy/strategy.service';
import { OandaService } from '../oanda/oanda.service';
import { Platform, Direction, NewsStatus } from '@prisma/client';
import { SignalsService } from '../signals/signals.service';

@Injectable()
export class SignalGeneratorService {
  private readonly logger = new Logger(SignalGeneratorService.name);
  // Only major pairs that are available in OANDA Practice account
  // Note: EUR/USD and GBP/USD can be included if needed (set INCLUDE_EUR_USD=true in .env)
  private readonly instruments = (() => {
    const includeEurUsd = process.env.INCLUDE_EUR_USD === 'true';
    const baseInstruments = [
      'USD/JPY',
      'AUD/USD',
      'USD/CAD',
      'USD/CHF',
      'NZD/USD',
      'EUR/GBP',
      'EUR/JPY',
      'GBP/JPY',
      'AUD/JPY',
      'EUR/AUD',
      'GBP/AUD',
      'GBP/CHF',
    ];
    
    if (includeEurUsd) {
      return ['EUR/USD', 'GBP/USD', ...baseInstruments];
    }
    
    return baseInstruments;
  })();

  constructor(
    private prisma: PrismaService,
    private strategyService: StrategyService,
    private oandaService: OandaService,
    private signalsService: SignalsService,
  ) {}

  /**
   * Generate signals for all instruments
   * Runs every minute (M1 timeframe)
   * Matches Python bot logic: analyze all, then select strongest signal
   */
  @Cron('* * * * *') // Every minute
  async generateSignals() {
    // Check if OANDA API is configured
    const apiKey = process.env.OANDA_API_KEY;
    if (!apiKey || apiKey === '') {
      this.logger.warn('OANDA_API_KEY is not configured. Skipping signal generation.');
      return;
    }

    this.logger.log('Starting signal generation...');

    // Step 1: Analyze all instruments and collect qualified signals
    const qualifiedSignals: Array<{
      instrument: string;
      analysis: Awaited<ReturnType<typeof this.strategyService.analyzeInstrument>>;
    }> = [];

    for (const instrument of this.instruments) {
      try {
        const analysis = await this.strategyService.analyzeInstrument(instrument);
        
        // Log all analysis results for debugging
        if (analysis.direction) {
          this.logger.debug(
            `${instrument}: ${analysis.direction} signal, ${analysis.confidence}% confidence, ` +
            `Indicators: MACD=${analysis.indicators.macd}, RSI=${analysis.indicators.rsi}, ` +
            `EMA=${analysis.indicators.ema}, S/R=${analysis.indicators.supportResistance}, ` +
            `PA=${analysis.indicators.priceAction}`
          );
        }
        
        // Only consider signals with direction and confidence >= 60%
        if (analysis.direction && analysis.confidence >= 60) {
          qualifiedSignals.push({ instrument, analysis });
          this.logger.log(`✅ Qualified: ${instrument} ${analysis.direction} (${analysis.confidence}%)`);
        } else if (analysis.direction) {
          this.logger.debug(`❌ Rejected (low confidence): ${instrument} ${analysis.direction} (${analysis.confidence}% < 70%)`);
        }
      } catch (error: any) {
        this.logger.error(`Failed to analyze ${instrument}: ${error.message}`);
      }
    }

    this.logger.log(`Found ${qualifiedSignals.length} qualified signal(s) out of ${this.instruments.length} instruments`);

    if (qualifiedSignals.length === 0) {
      this.logger.log('No qualified signals found (need: direction + confidence >= 60%)');
      return;
    }

    // Step 2: Check global cooldown (60 seconds)
    const lastGlobalSignal = await this.prisma.signal.findFirst({
      where: {
        active: true,
      },
      orderBy: {
        createdAt: 'desc',
      },
    });

    if (lastGlobalSignal) {
      const timeSinceLastSignal = Date.now() - lastGlobalSignal.createdAt.getTime();
      if (timeSinceLastSignal < 60 * 1000) {
        this.logger.log(`⏸️ Global cooldown active: ${Math.round(timeSinceLastSignal / 1000)}s / 60s since last signal (${lastGlobalSignal.asset} ${lastGlobalSignal.direction})`);
        return;
      } else {
        this.logger.log(`✅ Global cooldown expired: ${Math.round(timeSinceLastSignal / 1000)}s since last signal`);
      }
    } else {
      this.logger.log('✅ No previous signals found, cooldown check passed');
    }

    // Step 3: Filter signals based on instrument-specific rules
    const eligibleSignals = [];
    for (const { instrument, analysis } of qualifiedSignals) {
      // Check if similar signal already exists (within last 5 minutes)
      const recentSignal = await this.prisma.signal.findFirst({
        where: {
          asset: instrument,
          direction: analysis.direction,
          active: true,
          createdAt: {
            gte: new Date(Date.now() - 5 * 60 * 1000),
          },
        },
      });

      if (recentSignal) {
        this.logger.debug(`⏭️ Skipped ${instrument}: Similar signal exists (${Math.round((Date.now() - recentSignal.createdAt.getTime()) / 1000)}s ago)`);
        continue; // Skip if similar signal exists
      }

      // Check if direction changed or cooldown expired
      const lastInstrumentSignal = await this.prisma.signal.findFirst({
        where: {
          asset: instrument,
          active: true,
        },
        orderBy: {
          createdAt: 'desc',
        },
      });

      const directionChanged = lastInstrumentSignal && lastInstrumentSignal.direction !== analysis.direction;
      
      if (!directionChanged && lastInstrumentSignal) {
        const timeSinceLastInstrumentSignal = Date.now() - lastInstrumentSignal.createdAt.getTime();
        if (timeSinceLastInstrumentSignal < 60 * 1000) {
          this.logger.debug(`⏭️ Skipped ${instrument}: Cooldown active (${Math.round(timeSinceLastInstrumentSignal / 1000)}s / 60s)`);
          continue; // Skip if cooldown active and direction didn't change
        }
      }

      if (directionChanged) {
        this.logger.log(`🔄 Direction changed for ${instrument}: ${lastInstrumentSignal?.direction} → ${analysis.direction}`);
      }

      eligibleSignals.push({ instrument, analysis });
      this.logger.log(`✅ Eligible: ${instrument} ${analysis.direction} (${analysis.confidence}%)`);
    }

    this.logger.log(`Found ${eligibleSignals.length} eligible signal(s) after filtering`);

    if (eligibleSignals.length === 0) {
      this.logger.log('No eligible signals after filtering (cooldown or duplicate)');
      return;
    }

    // Step 4: Select strongest signal (highest confidence)
    // Try to avoid repeating the last instrument if possible
    const lastInstrument = lastGlobalSignal?.asset;
    const signalsNotLastInstrument = eligibleSignals.filter(s => s.instrument !== lastInstrument);
    const signalsToChooseFrom = signalsNotLastInstrument.length > 0 ? signalsNotLastInstrument : eligibleSignals;
    
    const strongestSignal = signalsToChooseFrom.reduce((best, current) => 
      current.analysis.confidence > best.analysis.confidence ? current : best
    );

    // Step 5: Create the selected signal
    await this.createSignal(strongestSignal.instrument, strongestSignal.analysis);

    this.logger.log(`Signal generation completed. Selected: ${strongestSignal.instrument} (${strongestSignal.analysis.confidence}% confidence)`);
  }

  /**
   * Create signal for instrument (internal helper)
   */
  private async createSignal(
    instrument: string,
    analysis: Awaited<ReturnType<typeof this.strategyService.analyzeInstrument>>,
  ) {
    // Deactivate old signals for this instrument
    await this.prisma.signal.updateMany({
      where: {
        asset: instrument,
        active: true,
      },
      data: {
        active: false,
      },
    });

    // Create new signal (direction is guaranteed to be non-null by caller)
    if (!analysis.direction) {
      throw new Error(`Cannot create signal for ${instrument}: direction is null`);
    }

    const expirySeconds = 60; // 1 minute expiry for M1 timeframe
    const signal = await this.signalsService.createSignal({
      platform: Platform.QUOTEX, // Default platform
      asset: instrument,
      direction: analysis.direction,
      expirySeconds,
      confidence: Math.round(analysis.confidence),
      newsStatus: NewsStatus.SAFE, // Can be enhanced with news API
    });

    this.logger.log(
      `Created signal: ${instrument} ${analysis.direction} (${analysis.confidence}% confidence)`,
    );
  }

  /**
   * Manually trigger signal generation (for testing)
   */
  async generateSignalsManually() {
    await this.generateSignals();
  }
}

