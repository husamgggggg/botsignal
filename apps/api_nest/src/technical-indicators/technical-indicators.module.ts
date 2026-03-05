import { Module } from '@nestjs/common';
import { TechnicalIndicatorsService } from './technical-indicators.service';

@Module({
  providers: [TechnicalIndicatorsService],
  exports: [TechnicalIndicatorsService],
})
export class TechnicalIndicatorsModule {}

