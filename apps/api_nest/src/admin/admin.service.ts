import { Injectable, BadRequestException, Logger } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { Platform, AccountStatus } from '@prisma/client';

@Injectable()
export class AdminService {
  private readonly logger = new Logger(AdminService.name);

  constructor(private prisma: PrismaService) {}

  /**
   * Get all accounts
   */
  async getAllAccounts(platform?: Platform) {
    const where: any = {};
    if (platform) {
      where.platform = platform;
    }

    return this.prisma.account.findMany({
      where,
      orderBy: { createdAt: 'desc' },
    });
  }

  /**
   * Add account manually (for old users)
   */
  async addAccount(
    platform: Platform,
    accountId: string,
    status: AccountStatus = AccountStatus.REGISTERED,
    lastDepositAmount?: number,
    lastDepositAt?: Date,
  ) {
    try {
      const account = await this.prisma.account.upsert({
        where: {
          platform_accountId: {
            platform,
            accountId,
          },
        },
        update: {
          status,
          lastDepositAmount,
          lastDepositAt,
        },
        create: {
          platform,
          accountId,
          status,
          lastDepositAmount,
          lastDepositAt,
        },
      });

      this.logger.log(`✅ Account added/updated manually: accountId=${accountId}, platform=${platform}, status=${status}`);

      return account;
    } catch (error: any) {
      this.logger.error(`❌ Failed to add account: ${error.message}`);
      throw new BadRequestException(`Failed to add account: ${error.message}`);
    }
  }

  /**
   * Bulk add accounts (for importing old users)
   */
  async bulkAddAccounts(accounts: Array<{
    platform: Platform;
    accountId: string;
    status?: AccountStatus;
    lastDepositAmount?: number;
    lastDepositAt?: Date;
  }>) {
    const results = [];
    const errors = [];

    for (const accountData of accounts) {
      try {
        const account = await this.addAccount(
          accountData.platform,
          accountData.accountId,
          accountData.status || AccountStatus.REGISTERED,
          accountData.lastDepositAmount,
          accountData.lastDepositAt,
        );
        results.push(account);
      } catch (error: any) {
        errors.push({
          accountId: accountData.accountId,
          error: error.message,
        });
      }
    }

    return {
      success: results.length,
      failed: errors.length,
      results,
      errors,
    };
  }

  /**
   * Update account status
   */
  async updateAccountStatus(
    platform: Platform,
    accountId: string,
    status: AccountStatus,
  ) {
    const account = await this.prisma.account.findUnique({
      where: {
        platform_accountId: {
          platform,
          accountId,
        },
      },
    });

    if (!account) {
      throw new BadRequestException('Account not found');
    }

    return this.prisma.account.update({
      where: { id: account.id },
      data: { status },
    });
  }

  /**
   * Delete account
   */
  async deleteAccount(platform: Platform, accountId: string) {
    const account = await this.prisma.account.findUnique({
      where: {
        platform_accountId: {
          platform,
          accountId,
        },
      },
    });

    if (!account) {
      throw new BadRequestException('Account not found');
    }

    await this.prisma.account.delete({
      where: { id: account.id },
    });

    return { success: true, message: 'Account deleted' };
  }
}

