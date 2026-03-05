import { Module } from '@nestjs/common';
import { OandaService } from './oanda.service';

@Module({
  providers: [OandaService],
  exports: [OandaService],
})
export class OandaModule {}

