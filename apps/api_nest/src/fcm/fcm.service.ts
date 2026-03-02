import { Injectable, OnModuleInit } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { PrismaService } from '../prisma/prisma.service';
import * as admin from 'firebase-admin';
import { Signal, AccountStatus } from '@prisma/client';

@Injectable()
export class FcmService implements OnModuleInit {
  private firebaseApp: admin.app.App | null = null;

  constructor(
    private configService: ConfigService,
    private prisma: PrismaService,
  ) {}

  onModuleInit() {
    const projectId = this.configService.get<string>('FIREBASE_PROJECT_ID');
    const privateKey = this.configService.get<string>('FIREBASE_PRIVATE_KEY')?.replace(/\\n/g, '\n');
    const clientEmail = this.configService.get<string>('FIREBASE_CLIENT_EMAIL');

    // Check if Firebase credentials are provided and valid
    if (!projectId || !privateKey || !clientEmail) {
      console.warn('⚠️ Firebase credentials not configured. Push notifications will be disabled.');
      return;
    }

    // Check if credentials are placeholder values
    if (
      projectId.includes('your-firebase') ||
      privateKey.includes('your-firebase') ||
      clientEmail.includes('your-firebase') ||
      projectId === '' ||
      privateKey === '' ||
      clientEmail === ''
    ) {
      console.warn('⚠️ Firebase credentials are placeholders. Push notifications will be disabled.');
      return;
    }

    try {
      this.firebaseApp = admin.initializeApp({
        credential: admin.credential.cert({
          projectId,
          privateKey,
          clientEmail,
        }),
      });
      console.log('✅ Firebase Admin initialized');
    } catch (error) {
      console.warn('⚠️ Firebase Admin initialization failed. Push notifications will be disabled.');
      console.warn('   Error:', error instanceof Error ? error.message : String(error));
      this.firebaseApp = null;
    }
  }

  async sendSignalNotification(signal: Signal) {
    if (!this.firebaseApp) {
      console.warn('Firebase not initialized, skipping push notification');
      return;
    }

    // Get all devices with verified active accounts
    const devices = await this.prisma.device.findMany({
      where: {
        fcmToken: { not: null },
        accounts: {
          some: {
            account: {
              status: AccountStatus.DEPOSITED,
            },
          },
        },
      },
    });

    const message = {
      notification: {
        title: 'إشارة جديدة / New Signal',
        body: `${signal.asset} - ${signal.direction} (${signal.confidence}%)`,
      },
      data: {
        signalId: signal.id,
        asset: signal.asset,
        direction: signal.direction,
        expirySeconds: signal.expirySeconds.toString(),
        confidence: signal.confidence.toString(),
      },
    };

    const results = [];
    for (const device of devices) {
      if (device.fcmToken) {
        try {
          const result = await admin.messaging().send({
            ...message,
            token: device.fcmToken,
          });
          results.push({ deviceId: device.deviceId, success: true, result });

          // Log notification
          await this.prisma.notificationLog.create({
            data: {
              signalId: signal.id,
              fcmResponse: result as any,
            },
          });
        } catch (error) {
          console.error(`Failed to send notification to device ${device.deviceId}:`, error);
          results.push({ deviceId: device.deviceId, success: false, error: String(error) });
        }
      }
    }

    return results;
  }
}

