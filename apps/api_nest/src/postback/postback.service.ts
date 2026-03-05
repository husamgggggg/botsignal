import { Injectable, BadRequestException, Logger } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { Platform, AccountStatus } from '@prisma/client';
import axios, { AxiosInstance } from 'axios';

@Injectable()
export class PostbackService {
  private readonly logger = new Logger(PostbackService.name);
  private readonly httpClient: AxiosInstance;

  constructor(private prisma: PrismaService) {
    this.httpClient = axios.create({
      timeout: 10000,
      validateStatus: (status) => status < 500,
    });
  }

  /**
   * Handle Quotex postback format
   * Format: ?status={status}&{status}=true&eid={event_id}&cid={click_id}&sid={site_id}&lid={lid}&uid={trader_id}&country={country}&sumdep={sumdep}&sumwithdraw={sumwithdraw}
   * 
   * This function saves ALL users registered through the affiliate link to the database
   */
  async handleQuotexPostback(query: any) {
    // Extract trader ID (uid) - this is the Account ID
    const accountId = query.uid || query.trader_id;
    if (!accountId) {
      this.logger.warn('Quotex postback missing uid (trader_id)', query);
      return { success: false, message: 'Missing uid (trader_id)' };
    }

    // Extract affiliate link information
    const lid = query.lid || null; // Link ID
    const cid = query.cid || query.click_id || null; // Click ID
    const sid = query.sid || query.site_id || null; // Site ID
    const eid = query.eid || query.event_id || null; // Event ID
    const country = query.country || null;

    // Save raw postback event (always save for tracking)
    try {
      await this.prisma.postbackEvent.create({
        data: {
          platform: Platform.QUOTEX,
          eventType: query.status || 'unknown',
          payload: {
            ...query,
            accountId,
            lid,
            cid,
            sid,
            eid,
            country,
            processedAt: new Date().toISOString(),
          } as any,
        },
      });
      this.logger.log(`Postback event saved: accountId=${accountId}, eventType=${query.status || 'unknown'}`);
    } catch (err) {
      this.logger.error('Failed to save postback event', err);
    }

    // Determine status based on Quotex postback format
    // Check registration status (reg or conf)
    const isRegistered = 
      query.reg === 'true' || 
      query.reg === true || 
      query.reg === '1' ||
      query.status === 'reg' || 
      query.conf === 'true' || 
      query.conf === true || 
      query.conf === '1' ||
      query.status === 'conf';
    
    // Check deposit status
    const hasFirstDeposit = 
      query.ftd === 'true' || 
      query.ftd === true || 
      query.ftd === '1' ||
      query.status === 'ftd';
    
    const hasDeposit = 
      query.dep === 'true' || 
      query.dep === true || 
      query.dep === '1' ||
      query.status === 'dep' || 
      hasFirstDeposit;
    
    const hasWithdrawal = 
      query.withdrawal === 'true' || 
      query.withdrawal === true || 
      query.withdrawal === '1' ||
      query.status === 'withdrawal';

    // Extract deposit and withdrawal amounts
    const depositAmount = parseFloat(query.sumdep || '0') || 0;
    const withdrawalAmount = parseFloat(query.sumwithdraw || '0') || 0;

    // Determine account status
    let accountStatus: AccountStatus = AccountStatus.NO_DEPOSIT;
    if (hasDeposit || hasFirstDeposit) {
      accountStatus = AccountStatus.DEPOSITED;
    } else if (isRegistered) {
      accountStatus = AccountStatus.REGISTERED;
    }

    // IMPORTANT: Always save/update the account in database
    // This ensures ALL users registered through affiliate link are saved
    try {
      const account = await this.prisma.account.upsert({
        where: {
          platform_accountId: {
            platform: Platform.QUOTEX,
            accountId: String(accountId),
          },
        },
        update: {
          status: accountStatus,
          lastDepositAmount: depositAmount > 0 ? depositAmount : undefined,
          lastDepositAt: (hasDeposit || hasFirstDeposit) ? new Date() : undefined,
          updatedAt: new Date(),
        },
        create: {
          platform: Platform.QUOTEX,
          accountId: String(accountId),
          status: accountStatus,
          lastDepositAmount: depositAmount > 0 ? depositAmount : undefined,
          lastDepositAt: (hasDeposit || hasFirstDeposit) ? new Date() : undefined,
        },
      });

      this.logger.log(`✅ Account saved/updated: accountId=${accountId}, status=${accountStatus}, registered=${isRegistered}, hasDeposit=${hasDeposit}, lid=${lid}`);

      return { 
        success: true,
        accountId,
        status: accountStatus,
        isRegistered,
        hasDeposit,
        hasFirstDeposit,
        depositAmount,
        lid,
        message: 'Account saved successfully',
      };
    } catch (err) {
      this.logger.error(`❌ Failed to save account: accountId=${accountId}`, err);
      throw new BadRequestException(`Failed to save account: ${err.message}`);
    }
  }

  async handlePostback(platform: Platform, payload: any) {
    // Save raw postback event
    await this.prisma.postbackEvent.create({
      data: {
        platform,
        eventType: payload.event_type || payload.eventType || 'unknown',
        payload: payload as any,
      },
    });

    // Extract account ID (varies by platform)
    const accountId = payload.click_id || payload.user_id || payload.account_id || payload.accountId;
    if (!accountId) {
      throw new BadRequestException('Missing account identifier in postback');
    }

    // Handle different event types
    const eventType = payload.event_type || payload.eventType || '';
    const depositAmount = parseFloat(payload.deposit_amount || payload.depositAmount || '0') || 0;

    if (eventType === 'registration' || eventType === 'register' || eventType === 'signup') {
      // User registered under our affiliate
      await this.prisma.account.upsert({
        where: {
          platform_accountId: {
            platform,
            accountId: String(accountId),
          },
        },
        update: {
          status: AccountStatus.REGISTERED,
        },
        create: {
          platform,
          accountId: String(accountId),
          status: AccountStatus.REGISTERED,
        },
      });
    } else if (eventType === 'deposit' || eventType === 'first_deposit' || depositAmount > 0) {
      // User made a deposit
      await this.prisma.account.upsert({
        where: {
          platform_accountId: {
            platform,
            accountId: String(accountId),
          },
        },
        update: {
          status: AccountStatus.DEPOSITED,
          lastDepositAmount: depositAmount,
          lastDepositAt: new Date(),
        },
        create: {
          platform,
          accountId: String(accountId),
          status: AccountStatus.DEPOSITED,
          lastDepositAmount: depositAmount,
          lastDepositAt: new Date(),
        },
      });
    }

    return { success: true };
  }

  /**
   * Verify account via postback by calling postback URL directly
   * Used for old users who are not in database yet
   */
  async verifyPostbackViaAccountId(
    accountId: string,
    postbackUrl: string,
    lid?: string,
    clickId?: string,
    siteId?: string,
  ): Promise<{
    success: boolean;
    account?: any;
    isRegistered?: boolean;
    hasDeposit?: boolean;
  }> {
    try {
      // Build postback URL with account ID
      const url = new URL(postbackUrl);
      url.searchParams.set('uid', accountId);
      if (lid) url.searchParams.set('lid', lid);
      if (clickId) url.searchParams.set('cid', clickId);
      if (siteId) url.searchParams.set('sid', siteId);

      // Call postback URL
      const response = await this.httpClient.get(url.toString());

      // Parse response - postback may return JSON, XML, or query parameters
      let data: any;
      try {
        data = response.data;
        // If response is a string, try to parse as query parameters
        if (typeof data === 'string') {
          try {
            const responseUrl = new URL(data);
            data = Object.fromEntries(responseUrl.searchParams);
          } catch {
            // If not a URL, try to parse as JSON
            try {
              data = JSON.parse(data);
            } catch {
              data = { raw: data };
            }
          }
        }
      } catch (e) {
        // If parsing fails, use query parameters from original URL
        data = Object.fromEntries(url.searchParams);
      }

      // Check registration and deposit status
      const isRegistered = this._checkRegistrationStatus(data);
      const hasDeposit = this._checkBalanceStatus(data);

      // If user is registered, save to database
      if (isRegistered) {
        let accountStatus: AccountStatus = AccountStatus.REGISTERED;
        if (hasDeposit) {
          accountStatus = AccountStatus.DEPOSITED;
        }

        const account = await this.prisma.account.upsert({
          where: {
            platform_accountId: {
              platform: Platform.QUOTEX,
              accountId: String(accountId),
            },
          },
          update: {
            status: accountStatus,
          },
          create: {
            platform: Platform.QUOTEX,
            accountId: String(accountId),
            status: accountStatus,
          },
        });

        this.logger.log(`✅ Old user added to database via postback: accountId=${accountId}, status=${accountStatus}`);

        return {
          success: true,
          account,
          isRegistered,
          hasDeposit,
        };
      }

      return {
        success: false,
        isRegistered: false,
        hasDeposit: false,
      };
    } catch (e: any) {
      this.logger.error(`❌ Postback verification failed for accountId=${accountId}: ${e.message}`);
      return {
        success: false,
      };
    }
  }

  /**
   * Check if user is registered (reg or conf status)
   */
  private _checkRegistrationStatus(postbackData: any): boolean {
    if (typeof postbackData === 'object' && postbackData !== null) {
      const status = String(postbackData.status || '').toLowerCase();
      const reg = String(postbackData.reg || '').toLowerCase();
      const conf = String(postbackData.conf || '').toLowerCase();

      return (
        status === 'reg' ||
        status === 'conf' ||
        reg === 'true' ||
        reg === '1' ||
        conf === 'true' ||
        conf === '1'
      );
    }
    return false;
  }

  /**
   * Check if user has balance (ftd or dep status)
   */
  private _checkBalanceStatus(postbackData: any): boolean {
    if (typeof postbackData === 'object' && postbackData !== null) {
      const status = String(postbackData.status || '').toLowerCase();
      const ftd = String(postbackData.ftd || '').toLowerCase();
      const dep = String(postbackData.dep || '').toLowerCase();

      return (
        status === 'ftd' ||
        status === 'dep' ||
        ftd === 'true' ||
        ftd === '1' ||
        dep === 'true' ||
        dep === '1'
      );
    }
    return false;
  }
}

