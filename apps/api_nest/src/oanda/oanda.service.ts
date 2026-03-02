import { Injectable, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import axios, { AxiosInstance } from 'axios';

export interface OandaCandle {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  complete: boolean;
}

export interface OandaPriceData {
  o: number; // open
  h: number; // high
  l: number; // low
  c: number; // close
}

export interface OandaCandlesResponse {
  instrument: string;
  granularity: string;
  candles: Array<{
    time: string;
    bid: OandaPriceData;
    ask: OandaPriceData;
    mid: OandaPriceData;
    volume: number;
    complete: boolean;
  }>;
}

@Injectable()
export class OandaService {
  private readonly logger = new Logger(OandaService.name);
  private readonly apiKey: string;
  private readonly accountId: string;
  private readonly baseUrl: string;
  private readonly httpClient: AxiosInstance;

  constructor(private configService: ConfigService) {
    this.apiKey = this.configService.get<string>('OANDA_API_KEY', '');
    this.accountId = this.configService.get<string>('OANDA_ACCOUNT_ID', '');
    const environment = this.configService.get<string>('OANDA_ENVIRONMENT', 'practice'); // 'practice' or 'live'
    this.baseUrl = environment === 'live' 
      ? 'https://api-fxtrade.oanda.com'
      : 'https://api-fxpractice.oanda.com';

    this.httpClient = axios.create({
      baseURL: this.baseUrl,
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json',
      },
      timeout: 10000, // 10 seconds timeout
    });

    if (!this.apiKey) {
      this.logger.warn('OANDA_API_KEY is not configured. OANDA features will be disabled.');
    }
  }

  /**
   * Convert OANDA instrument name to standard format
   * Example: EUR_USD -> EUR/USD
   */
  private normalizeInstrument(instrument: string): string {
    return instrument.replace('_', '/');
  }

  /**
   * Convert standard instrument to OANDA format
   * Example: EUR/USD -> EUR_USD
   */
  private toOandaFormat(instrument: string): string {
    return instrument.replace('/', '_');
  }

  /**
   * Get candles data from OANDA
   * @param instrument - Currency pair (e.g., 'EUR/USD')
   * @param granularity - Timeframe (e.g., 'M1', 'M5', 'H1')
   * @param count - Number of candles to retrieve
   */
  async getCandles(
    instrument: string,
    granularity: string = 'M1',
    count: number = 500,
  ): Promise<OandaCandle[]> {
    try {
      // Check if API key is configured
      if (!this.apiKey || this.apiKey === '') {
        this.logger.warn('OANDA_API_KEY is not configured. Skipping API call.');
        return [];
      }

      const oandaInstrument = this.toOandaFormat(instrument);
      const url = `/v3/instruments/${oandaInstrument}/candles`;
      
      this.logger.debug(`Requesting candles for ${instrument} (${oandaInstrument}) from ${url}`);

      const response = await this.httpClient.get<OandaCandlesResponse>(
        url,
        {
          params: {
            granularity,
            count,
            price: 'M', // Mid price
          },
        },
      );

      if (!response.data || !response.data.candles || response.data.candles.length === 0) {
        this.logger.warn(`No candles found for ${instrument}`);
        return [];
      }

      // Convert OANDA candles to our format
      const candles: OandaCandle[] = response.data.candles
        .filter((c) => c.complete) // Only use complete candles
        .map((c) => ({
          time: c.time,
          open: c.mid.o,
          high: c.mid.h,
          low: c.mid.l,
          close: c.mid.c,
          volume: c.volume,
          complete: c.complete,
        }));

      this.logger.log(`Retrieved ${candles.length} candles for ${instrument}`);
      return candles;
    } catch (error: any) {
      const errorMessage = error.response?.data?.errorMessage || error.message;
      const statusCode = error.response?.status || 'unknown';
      
      this.logger.error(
        `Failed to get candles for ${instrument}: ${errorMessage} (Status: ${statusCode})`,
      );
      
      // Log full error details in debug mode
      if (error.response?.data) {
        this.logger.debug(`OANDA API Error Details: ${JSON.stringify(error.response.data)}`);
      }
      
      // Return empty array instead of throwing to allow system to continue
      return [];
    }
  }

  /**
   * Get current price for an instrument
   */
  async getCurrentPrice(instrument: string): Promise<number> {
    try {
      const oandaInstrument = this.toOandaFormat(instrument);
      const response = await this.httpClient.get(
        `/v3/instruments/${oandaInstrument}/candles`,
        {
          params: {
            granularity: 'M1',
            count: 1,
            price: 'M',
          },
        },
      );

      if (response.data.candles && response.data.candles.length > 0) {
        const lastCandle = response.data.candles[response.data.candles.length - 1];
        return lastCandle.mid.c; // Close price
      }

      throw new Error('No price data available');
    } catch (error: any) {
      this.logger.error(`Failed to get current price for ${instrument}: ${error.message}`);
      throw error;
    }
  }

  /**
   * Get available instruments
   */
  async getInstruments(): Promise<string[]> {
    try {
      const response = await this.httpClient.get('/v3/accounts/${this.accountId}/instruments');
      const instruments = response.data.instruments || [];
      return instruments.map((inst: any) => this.normalizeInstrument(inst.name));
    } catch (error: any) {
      this.logger.error(`Failed to get instruments: ${error.message}`);
      return [];
    }
  }
}

