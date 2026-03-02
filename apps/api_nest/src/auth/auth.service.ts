import { Injectable } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { PrismaService } from '../prisma/prisma.service';

@Injectable()
export class AuthService {
  constructor(
    private prisma: PrismaService,
    private jwtService: JwtService,
  ) {}

  async registerDevice(deviceId: string, fcmToken?: string) {
    const device = await this.prisma.device.upsert({
      where: { deviceId },
      update: {
        lastSeenAt: new Date(),
        ...(fcmToken && { fcmToken }),
      },
      create: {
        deviceId,
        fcmToken,
        lastSeenAt: new Date(),
      },
    });

    const token = this.jwtService.sign({
      sub: device.id,
      deviceId: device.deviceId,
    });

    return {
      token,
      deviceId: device.deviceId,
    };
  }

  async updateFcmToken(deviceId: string, fcmToken: string) {
    await this.prisma.device.updateMany({
      where: { deviceId },
      data: { fcmToken },
    });
  }

  async validateDevice(deviceId: string) {
    const device = await this.prisma.device.findUnique({
      where: { deviceId },
    });
    return device;
  }
}

