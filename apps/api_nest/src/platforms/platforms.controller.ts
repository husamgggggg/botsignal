import { Controller, Get, Param } from '@nestjs/common';
import { ApiTags, ApiOperation } from '@nestjs/swagger';
import { SkipThrottle } from '@nestjs/throttler';
import { ConfigService } from '@nestjs/config';

@ApiTags('platforms')
@Controller('api/platforms')
@SkipThrottle()
export class PlatformsController {
  constructor(private configService: ConfigService) {}

  @Get()
  @ApiOperation({ summary: 'Get available platforms with affiliate links and deep links' })
  getPlatforms() {
    return {
      platforms: [
        {
          id: 'QUOTEX',
          name: 'Quotex',
          nameAr: 'كووتكس',
          affiliateUrl: this.configService.get<string>('QUOTEX_AFFILIATE_URL', 'https://broker-qx.pro/sign-up/?lid=1549667'),
          deepLink: this.configService.get<string>('QUOTEX_DEEP_LINK', 'quotex://'),
        },
        {
          id: 'POCKET_OPTION',
          name: 'Pocket Option',
          nameAr: 'بوكيت أوبشن',
          affiliateUrl: this.configService.get<string>('POCKET_OPTION_AFFILIATE_URL', ''),
          deepLink: this.configService.get<string>('POCKET_OPTION_DEEP_LINK', 'pocketoption://'),
        },
      ],
    };
  }

  @Get(':platformId/postback')
  @ApiOperation({ summary: 'Get postback configuration for a platform' })
  getPostbackConfig(@Param('platformId') platformId: string) {
    if (platformId.toUpperCase() === 'QUOTEX') {
      return {
        postbackUrl: this.configService.get<string>('QUOTEX_POSTBACK_URL', ''),
        lid: this.configService.get<string>('QUOTEX_LID', '1549667'),
        clickId: this.configService.get<string>('QUOTEX_CLICK_ID', ''),
        siteId: this.configService.get<string>('QUOTEX_SITE_ID', ''),
      };
    }
    return null;
  }
}

