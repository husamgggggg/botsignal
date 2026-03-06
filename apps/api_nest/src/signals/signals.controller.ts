import { Controller, Get, Post, Body, Query, UseGuards, Request } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiBearerAuth } from '@nestjs/swagger';
import { SignalsService, CreateSignalDto } from './signals.service';
import { JwtAuthGuard } from '../auth/jwt-auth.guard';
import { Platform } from '@prisma/client';

@ApiTags('signals')
@Controller('api/signals')
export class SignalsController {
  constructor(private readonly signalsService: SignalsService) {}

  @Get()
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({ summary: 'Get active signals (requires verified active account)' })
  async getSignals(@Request() req, @Query('platform') platform?: Platform) {
    return this.signalsService.getSignals(req.user.deviceId, platform);
  }

  @Get('debug/all')
  @ApiOperation({ summary: 'Get all active signals (debug endpoint, no auth required)' })
  async getAllSignals() {
    return this.signalsService.getAllActiveSignals();
  }
}

