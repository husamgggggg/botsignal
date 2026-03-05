import { Module } from '@nestjs/common';
import { PlatformsController } from './platforms.controller';
import { ConfigModule } from '@nestjs/config';

@Module({
  imports: [ConfigModule],
  controllers: [PlatformsController],
})
export class PlatformsModule {}

