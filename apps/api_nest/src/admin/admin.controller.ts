import { Controller, Post, Body, UseGuards, Get, Put, Delete, Query, Param } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiSecurity } from '@nestjs/swagger';
import { AdminGuard } from './admin.guard';
import { SignalsService, CreateSignalDto } from '../signals/signals.service';
import { AdminService } from './admin.service';
import { Platform, AccountStatus } from '@prisma/client';
import { IsEnum, IsString, IsOptional, IsNumber, IsArray, ValidateNested } from 'class-validator';
import { Type } from 'class-transformer';

class AddAccountDto {
  @IsEnum(Platform)
  platform: Platform;

  @IsString()
  accountId: string;

  @IsEnum(AccountStatus)
  @IsOptional()
  status?: AccountStatus;

  @IsNumber()
  @IsOptional()
  lastDepositAmount?: number;

  @IsOptional()
  lastDepositAt?: Date;
}

class BulkAddAccountDto {
  @IsArray()
  @ValidateNested({ each: true })
  @Type(() => AddAccountDto)
  accounts: AddAccountDto[];
}

class UpdateAccountStatusDto {
  @IsEnum(AccountStatus)
  status: AccountStatus;
}

@ApiTags('admin')
@Controller('api/admin')
@UseGuards(AdminGuard)
@ApiSecurity('admin-api-key')
export class AdminController {
  constructor(
    private readonly signalsService: SignalsService,
    private readonly adminService: AdminService,
  ) {}

  @Post('signals')
  @ApiOperation({ summary: 'Create a new signal (admin only)' })
  async createSignal(@Body() dto: CreateSignalDto) {
    return this.signalsService.createSignal(dto);
  }

  @Get('accounts')
  @ApiOperation({ summary: 'List all accounts (admin only)' })
  async getAccounts(@Query('platform') platform?: Platform) {
    return this.adminService.getAllAccounts(platform);
  }

  @Post('accounts')
  @ApiOperation({ summary: 'Add account manually (for old users)' })
  async addAccount(@Body() dto: AddAccountDto) {
    return this.adminService.addAccount(
      dto.platform,
      dto.accountId,
      dto.status,
      dto.lastDepositAmount,
      dto.lastDepositAt,
    );
  }

  @Post('accounts/bulk')
  @ApiOperation({ summary: 'Bulk add accounts (for importing old users)' })
  async bulkAddAccounts(@Body() dto: BulkAddAccountDto) {
    return this.adminService.bulkAddAccounts(dto.accounts);
  }

  @Put('accounts/:platform/:accountId/status')
  @ApiOperation({ summary: 'Update account status' })
  async updateAccountStatus(
    @Param('platform') platform: Platform,
    @Param('accountId') accountId: string,
    @Body() dto: UpdateAccountStatusDto,
  ) {
    return this.adminService.updateAccountStatus(platform, accountId, dto.status);
  }

  @Delete('accounts/:platform/:accountId')
  @ApiOperation({ summary: 'Delete account' })
  async deleteAccount(
    @Param('platform') platform: Platform,
    @Param('accountId') accountId: string,
  ) {
    return this.adminService.deleteAccount(platform, accountId);
  }
}

