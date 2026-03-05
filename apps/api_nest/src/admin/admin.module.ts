import { Module } from '@nestjs/common';
import { AdminController } from './admin.controller';
import { AdminService } from './admin.service';
import { SignalsModule } from '../signals/signals.module';
import { PrismaModule } from '../prisma/prisma.module';

@Module({
  imports: [SignalsModule, PrismaModule],
  controllers: [AdminController],
  providers: [AdminService],
})
export class AdminModule {}

