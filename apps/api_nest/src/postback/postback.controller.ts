import { Controller, Get, Query, Req, BadRequestException, Ip, HttpCode, HttpStatus } from '@nestjs/common';
import { ApiTags, ApiOperation } from '@nestjs/swagger';
import { ConfigService } from '@nestjs/config';
import { PostbackService } from './postback.service';
import { Platform } from '@prisma/client';

@ApiTags('postback')
@Controller('api/postback')
export class PostbackController {
  constructor(
    private readonly postbackService: PostbackService,
    private readonly configService: ConfigService,
  ) {}

  @Get()
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ summary: 'Generic postback endpoint for Quotex and other platforms' })
  async handlePostback(@Query() query: any, @Req() req, @Ip() ip: string) {
    // Log postback for debugging
    console.log('Postback received:', {
      ip,
      query,
      timestamp: new Date().toISOString(),
    });

    // Basic IP validation (optional, can be enhanced)
    const allowedIps = this.configService.get<string>('POSTBACK_ALLOWED_IPS', '');
    if (allowedIps && !allowedIps.split(',').includes(ip)) {
      console.warn(`Postback from unauthorized IP: ${ip}`);
      // Don't throw error, just log - Quotex might use different IPs
    }

    // Determine platform from query parameters or default to QUOTEX
    // For now, handleQuotexPostback works for Quotex format
    // If needed, we can add platform detection later
    
    // Handle Quotex postback format
    // Format: ?status={status}&{status}=true&eid={event_id}&cid={click_id}&sid={site_id}&lid={lid}&uid={trader_id}...
    return this.postbackService.handleQuotexPostback(query);
  }

  @Get('quotex')
  @ApiOperation({ summary: 'Quotex partner postback endpoint (legacy)' })
  async handleQuotexPostback(@Query() query: any, @Req() req, @Ip() ip: string) {
    const allowedIps = this.configService.get<string>('POSTBACK_ALLOWED_IPS', '');
    if (allowedIps && !allowedIps.split(',').includes(ip)) {
      console.warn(`Postback from unauthorized IP: ${ip}`);
    }

    return this.postbackService.handleQuotexPostback(query);
  }

  @Get('pocket-option')
  @ApiOperation({ summary: 'Pocket Option partner postback endpoint' })
  async handlePocketOptionPostback(@Query() query: any, @Req() req, @Ip() ip: string) {
    const allowedIps = this.configService.get<string>('POSTBACK_ALLOWED_IPS', '');
    if (allowedIps && !allowedIps.split(',').includes(ip)) {
      console.warn(`Postback from unauthorized IP: ${ip}`);
    }

    return this.postbackService.handlePostback(Platform.POCKET_OPTION, query);
  }
}

