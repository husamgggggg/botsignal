import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { ThrottlerModule } from '@nestjs/throttler';
import { PrismaModule } from './prisma/prisma.module';
import { AuthModule } from './auth/auth.module';
import { VerifyModule } from './verify/verify.module';
import { PostbackModule } from './postback/postback.module';
import { SignalsModule } from './signals/signals.module';
import { AdminModule } from './admin/admin.module';
import { PlatformsModule } from './platforms/platforms.module';
import { SignalGeneratorModule } from './signal-generator/signal-generator.module';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
    }),
    ThrottlerModule.forRoot([
      {
        ttl: 60000, // 1 minute
        limit: 10, // 10 requests per minute
      },
    ]),
    PrismaModule,
    AuthModule,
    VerifyModule,
    PostbackModule,
    SignalsModule,
    AdminModule,
    PlatformsModule,
    SignalGeneratorModule,
  ],
})
export class AppModule {}

