import { Injectable, ForbiddenException } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { Platform, Direction, NewsStatus, AccountStatus } from '@prisma/client';
import { FcmService } from '../fcm/fcm.service';
import { IsEnum, IsString, IsNumber, IsOptional, Min, Max } from 'class-validator';

export class CreateSignalDto {
  @IsEnum(Platform)
  @IsOptional()
  platform?: Platform;

  @IsString()
  asset: string;

  @IsEnum(Direction)
  direction: Direction;

  @IsNumber()
  @Min(1)
  expirySeconds: number;

  @IsNumber()
  @Min(0)
  @Max(100)
  confidence: number;

  @IsEnum(NewsStatus)
  @IsOptional()
  newsStatus?: NewsStatus;
}

@Injectable()
export class SignalsService {
  constructor(
    private prisma: PrismaService,
    private fcmService: FcmService,
  ) {}

  async getSignals(deviceId: string, platform?: Platform) {
    // Check if device has verified active account
    const device = await this.prisma.device.findUnique({
      where: { deviceId },
      include: {
        accounts: {
          include: {
            account: true,
          },
        },
      },
    });

    if (!device) {
      throw new ForbiddenException('Device not found');
    }

    // Check if any linked account is DEPOSITED
    const hasActiveAccount = device.accounts.some(
      (da) => da.account.status === AccountStatus.DEPOSITED,
    );

    if (!hasActiveAccount) {
      throw new ForbiddenException('Account verification required');
    }

    // Get active signals
    const where: any = { active: true };
    if (platform) {
      where.platform = platform;
    }

    const signals = await this.prisma.signal.findMany({
      where,
      orderBy: { createdAt: 'desc' },
      take: 50,
    });

    return signals;
  }

  async createSignal(dto: CreateSignalDto) {
    const signal = await this.prisma.signal.create({
      data: {
        platform: dto.platform,
        asset: dto.asset,
        direction: dto.direction,
        expirySeconds: dto.expirySeconds,
        confidence: dto.confidence,
        newsStatus: dto.newsStatus || NewsStatus.SAFE,
        active: true,
      },
    });

    // Send push notifications to all verified active devices
    await this.fcmService.sendSignalNotification(signal);

    return signal;
  }
}

