import { PrismaClient, Platform, Direction, NewsStatus, AccountStatus } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
  console.log('Seeding database...');

  // Create sample accounts
  const account1 = await prisma.account.upsert({
    where: {
      platform_accountId: {
        platform: Platform.QUOTEX,
        accountId: 'TEST_ACTIVE_123',
      },
    },
    update: {},
    create: {
      platform: Platform.QUOTEX,
      accountId: 'TEST_ACTIVE_123',
      status: AccountStatus.DEPOSITED,
      lastDepositAmount: 100.0,
      lastDepositAt: new Date(),
    },
  });

  const account2 = await prisma.account.upsert({
    where: {
      platform_accountId: {
        platform: Platform.QUOTEX,
        accountId: 'TEST_NO_DEPOSIT_456',
      },
    },
    update: {},
    create: {
      platform: Platform.QUOTEX,
      accountId: 'TEST_NO_DEPOSIT_456',
      status: AccountStatus.NO_DEPOSIT,
    },
  });

  // Create sample signals
  const signals = [
    {
      platform: Platform.QUOTEX,
      asset: 'EUR/USD',
      direction: Direction.CALL,
      expirySeconds: 60,
      confidence: 75,
      newsStatus: NewsStatus.SAFE,
      active: true,
    },
    {
      platform: Platform.QUOTEX,
      asset: 'GBP/USD',
      direction: Direction.PUT,
      expirySeconds: 300,
      confidence: 80,
      newsStatus: NewsStatus.WARNING,
      active: true,
    },
    {
      platform: Platform.POCKET_OPTION,
      asset: 'BTC/USD',
      direction: Direction.CALL,
      expirySeconds: 180,
      confidence: 70,
      newsStatus: NewsStatus.SAFE,
      active: true,
    },
  ];

  for (const signal of signals) {
    await prisma.signal.create({
      data: signal,
    });
  }

  console.log('Seed completed!');
  console.log('Test accounts:');
  console.log('- TEST_ACTIVE_123 (QUOTEX) - DEPOSITED');
  console.log('- TEST_NO_DEPOSIT_456 (QUOTEX) - NO_DEPOSIT');
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });

