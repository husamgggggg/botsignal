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
  private readonly instruments = [
    'EUR/USD',
    'GBP/USD',
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

    for (const instrument of this.instruments) {
      try {
        await this.analyzeAndCreateSignal(instrument);
      } catch (error: any) {
        this.logger.error(`Failed to generate signal for ${instrument}: ${error.message}`);
      }
    }

    this.logger.log('Signal generation completed');
  }

  /**
   * Analyze instrument and create signal if conditions are met
   */
  private async analyzeAndCreateSignal(instrument: string) {
    try {
      // Analyze instrument
      const analysis = await this.strategyService.analyzeInstrument(instrument);

      // Log analysis result for debugging
      this.logger.debug(
        `${instrument}: Direction=${analysis.direction}, Confidence=${analysis.confidence}%, Strategy=${analysis.strategy}`,
      );

      // Only create signal if direction is determined and confidence >= 75%
      if (analysis.direction && analysis.confidence >= 75) {
        // Check if similar signal already exists (within last 5 minutes)
        const recentSignal = await this.prisma.signal.findFirst({
          where: {
            asset: instrument,
            direction: analysis.direction,
            active: true,
            createdAt: {
              gte: new Date(Date.now() - 5 * 60 * 1000), // Last 5 minutes
            },
          },
        });

        if (recentSignal) {
          this.logger.debug(`Similar signal already exists for ${instrument}`);
          return;
        }

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

        // Create new signal
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
    } catch (error: any) {
      this.logger.error(`Error analyzing ${instrument}: ${error.message}`);
    }
  }

  /**
   * Manually trigger signal generation (for testing)
   */
  async generateSignalsManually() {
    await this.generateSignals();
  }
}

