import { Module } from '@nestjs/common';
import { ScheduleModule } from '@nestjs/schedule';
import { SignalGeneratorService } from './signal-generator.service';
import { StrategyModule } from '../strategy/strategy.module';
import { OandaModule } from '../oanda/oanda.module';
import { SignalsModule } from '../signals/signals.module';
import { PrismaModule } from '../prisma/prisma.module';

@Module({
  imports: [
    ScheduleModule.forRoot(),
    StrategyModule,
    OandaModule,
    SignalsModule,
    PrismaModule,
  ],
  providers: [SignalGeneratorService],
  exports: [SignalGeneratorService],
})
export class SignalGeneratorModule {}

