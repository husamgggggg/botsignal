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
  // Note: EUR/USD and GBP/USD are excluded as per Python bot logic
  private readonly instruments = [
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
    // Note: USD/BRL, USD/BDT, and USD/NGN are not available in OANDA Practice account
  ];

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
        
        // Only consider signals with direction and confidence >= 70%
        if (analysis.direction && analysis.confidence >= 70) {
          qualifiedSignals.push({ instrument, analysis });
        }
      } catch (error: any) {
        this.logger.error(`Failed to analyze ${instrument}: ${error.message}`);
      }
    }

    if (qualifiedSignals.length === 0) {
      this.logger.log('No qualified signals found');
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
        this.logger.debug(`Global cooldown active: ${Math.round(timeSinceLastSignal / 1000)}s since last signal`);
        return;
      }
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
          continue; // Skip if cooldown active and direction didn't change
        }
      }

      eligibleSignals.push({ instrument, analysis });
    }

    if (eligibleSignals.length === 0) {
      this.logger.log('No eligible signals after filtering');
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

