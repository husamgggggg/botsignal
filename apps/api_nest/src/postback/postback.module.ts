import { Module } from '@nestjs/common';
import { PostbackService } from './postback.service';
import { PostbackController } from './postback.controller';
import { PrismaModule } from '../prisma/prisma.module';

@Module({
  imports: [PrismaModule],
  controllers: [PostbackController],
  providers: [PostbackService],
  exports: [PostbackService],
})
export class PostbackModule {}

