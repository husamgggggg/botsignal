import { Controller, Post, Body, UseGuards, Request } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiBearerAuth } from '@nestjs/swagger';
import { AuthService } from './auth.service';
import { JwtAuthGuard } from './jwt-auth.guard';

@ApiTags('auth')
@Controller('api/auth')
export class AuthController {
  constructor(private readonly authService: AuthService) {}

  @Post('register')
  @ApiOperation({ summary: 'Register device and get access token' })
  async register(@Body() body: { deviceId: string; fcmToken?: string }) {
    return this.authService.registerDevice(body.deviceId, body.fcmToken);
  }

  @Post('fcm-token')
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({ summary: 'Update FCM token for push notifications' })
  async updateFcmToken(@Request() req, @Body() body: { fcmToken: string }) {
    await this.authService.updateFcmToken(req.user.deviceId, body.fcmToken);
    return { success: true };
  }
}

