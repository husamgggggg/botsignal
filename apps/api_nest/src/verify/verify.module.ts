import { Module } from '@nestjs/common';
import { VerifyService } from './verify.service';
import { VerifyController } from './verify.controller';
import { PrismaModule } from '../prisma/prisma.module';
import { PostbackModule } from '../postback/postback.module';

@Module({
  imports: [PrismaModule, PostbackModule],
  controllers: [VerifyController],
  providers: [VerifyService],
})
export class VerifyModule {}

