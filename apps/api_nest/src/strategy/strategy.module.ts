import { Module } from '@nestjs/common';
import { StrategyService } from './strategy.service';
import { BinaryOptionsStrategyService } from './binary-options-strategy.service';
import { OandaModule } from '../oanda/oanda.module';
import { TechnicalIndicatorsModule } from '../technical-indicators/technical-indicators.module';

@Module({
  imports: [OandaModule, TechnicalIndicatorsModule],
  providers: [StrategyService, BinaryOptionsStrategyService],
  exports: [StrategyService, BinaryOptionsStrategyService],
})
export class StrategyModule {}

