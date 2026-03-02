import { Controller, Post, Body, UseGuards } from '@nestjs/common';
import { ApiTags, ApiOperation } from '@nestjs/swagger';
import { ThrottlerGuard } from '@nestjs/throttler';
import { VerifyService } from './verify.service';
import { IsEnum, IsString } from 'class-validator';
import { Platform } from '@prisma/client';

class VerifyDto {
  @IsEnum(Platform)
  platform: Platform;

  @IsString()
  accountId: string;

  @IsString()
  deviceId: string;

  postbackUrl?: string;
  lid?: string;
  clickId?: string;
  siteId?: string;
}

@ApiTags('verify')
@Controller('api/verify')
@UseGuards(ThrottlerGuard)
export class VerifyController {
  constructor(private readonly verifyService: VerifyService) {}

  @Post()
  @ApiOperation({ summary: 'Verify account status' })
  async verify(@Body() dto: VerifyDto) {
    return this.verifyService.verifyAccount(
      dto.platform,
      dto.accountId,
      dto.deviceId,
      dto.postbackUrl,
      dto.lid,
      dto.clickId,
      dto.siteId,
    );
  }
}

