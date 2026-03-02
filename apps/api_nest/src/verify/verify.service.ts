import { Injectable, Logger } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { Platform, AccountStatus } from '@prisma/client';
import { PostbackService } from '../postback/postback.service';
import { ConfigService } from '@nestjs/config';

export enum VerificationStatus {
  VERIFIED_ACTIVE = 'VERIFIED_ACTIVE',
  VERIFIED_NO_DEPOSIT = 'VERIFIED_NO_DEPOSIT',
  NOT_UNDER_TEAM = 'NOT_UNDER_TEAM',
}

@Injectable()
export class VerifyService {
  private readonly logger = new Logger(VerifyService.name);

  constructor(
    private prisma: PrismaService,
    private postbackService: PostbackService,
    private configService: ConfigService,
  ) {}

  async verifyAccount(
    platform: Platform,
    accountId: string,
    deviceId: string,
    postbackUrl?: string,
    lid?: string,
    clickId?: string,
    siteId?: string,
  ): Promise<{
    status: VerificationStatus;
    message_ar: string;
    message_en: string;
  }> {
    // First, try to find account in database
    let account = await this.prisma.account.findUnique({
      where: {
        platform_accountId: {
          platform,
          accountId,
        },
      },
    });

    // If account not found and postback URL is provided, verify via postback
    if (!account && platform === Platform.QUOTEX && postbackUrl) {
      this.logger.log(`Account not found in DB, verifying via postback: accountId=${accountId}`);
      
      try {
        // Only verify via postback if URL is not a placeholder (example.com)
        if (!postbackUrl.includes('example.com')) {
          // Call postback to check if user exists and is registered
          const postbackResult = await this.postbackService.verifyPostbackViaAccountId(
            accountId,
            postbackUrl,
            lid,
            clickId,
            siteId,
          );

          if (postbackResult.success && postbackResult.account) {
            // Account found via postback, use it
            account = postbackResult.account;
            this.logger.log(`Account verified via postback: accountId=${accountId}, status=${account.status}`);
          } else {
            // Account not found via postback either
            this.logger.warn(`Account not found via postback: accountId=${accountId}`);
            return {
              status: VerificationStatus.NOT_UNDER_TEAM,
              message_ar: 'لم يتم العثور على الحساب. يرجى التسجيل مجاناً للحصول على إشارات مجانية.',
              message_en: 'Account not found. Please register for free to get free signals.',
            };
          }
        } else {
          // Postback URL is a placeholder, skip postback verification
          this.logger.warn(`Postback URL is a placeholder (example.com), skipping postback verification for accountId=${accountId}`);
        }
      } catch (error) {
        this.logger.error(`Postback verification failed: ${error.message}`);
        // If postback fails, log but don't block - might be network issue
        // User should be added to DB via actual postback from Quotex
      }
    }

    if (!account) {
      return {
        status: VerificationStatus.NOT_UNDER_TEAM,
        message_ar: 'لم يتم العثور على الحساب. يرجى التسجيل مجاناً للحصول على إشارات مجانية.',
        message_en: 'Account not found. Please register for free to get free signals.',
      };
    }

    // Link device to account
    const device = await this.prisma.device.findUnique({
      where: { deviceId },
    });

    if (device) {
      await this.prisma.deviceAccount.upsert({
        where: {
          deviceId_accountId: {
            deviceId: device.id,
            accountId: account.id,
          },
        },
        update: {},
        create: {
          deviceId: device.id,
          accountId: account.id,
        },
      });
    }

    // Check status
    // Only allow access for accounts with DEPOSITED status (has balance)
    if (account.status === AccountStatus.DEPOSITED) {
      return {
        status: VerificationStatus.VERIFIED_ACTIVE,
        message_ar: 'تم التحقق من حسابك بنجاح! يمكنك الآن الوصول إلى جميع الإشارات.',
        message_en: 'Your account has been verified successfully! You can now access all signals.',
      };
    }

    // REGISTERED and NO_DEPOSIT statuses require deposit
    if (account.status === AccountStatus.REGISTERED || account.status === AccountStatus.NO_DEPOSIT) {
      return {
        status: VerificationStatus.VERIFIED_NO_DEPOSIT,
        message_ar: 'تم التحقق من حسابك، لكن يلزم إيداع. يرجى إيداع الأموال للوصول إلى الإشارات.',
        message_en: 'Your account is verified, but a deposit is required. Please deposit funds to access signals.',
      };
    }

    return {
      status: VerificationStatus.NOT_UNDER_TEAM,
      message_ar: 'لم يتم العثور على الحساب. يرجى التسجيل مجاناً للحصول على إشارات مجانية.',
      message_en: 'Account not found. Please register for free to get free signals.',
    };
  }
}

