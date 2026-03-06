import { PrismaClient, AccountStatus } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
  console.log('🔍 Checking devices and accounts...\n');

  // Get all devices
  const devices = await prisma.device.findMany({
    include: {
      accounts: {
        include: {
          account: true,
        },
      },
    },
    orderBy: {
      lastSeenAt: 'desc',
    },
    take: 10,
  });

  console.log(`Found ${devices.length} device(s):\n`);

  for (const device of devices) {
    console.log(`📱 Device: ${device.deviceId}`);
    console.log(`   Last seen: ${device.lastSeenAt}`);
    console.log(`   Linked accounts: ${device.accounts.length}`);

    if (device.accounts.length === 0) {
      console.log('   ⚠️  No accounts linked!');
    } else {
      for (const da of device.accounts) {
        const account = da.account;
        const status = account.status === AccountStatus.DEPOSITED ? '✅' : '⚠️';
        console.log(`   ${status} ${account.platform} - ${account.accountId} (${account.status})`);
      }
    }

    // Check if device can see signals
    const hasActiveAccount = device.accounts.some(
      (da) => da.account.status === AccountStatus.DEPOSITED,
    );

    if (hasActiveAccount) {
      console.log('   ✅ Can see signals');
    } else {
      console.log('   ❌ Cannot see signals (no DEPOSITED account)');
    }

    console.log('');
  }

  // Get all accounts
  console.log('\n📊 All accounts:\n');
  const accounts = await prisma.account.findMany({
    orderBy: {
      createdAt: 'desc',
    },
  });

  for (const account of accounts) {
    const linkedDevices = await prisma.deviceAccount.count({
      where: { accountId: account.id },
    });
    const status = account.status === AccountStatus.DEPOSITED ? '✅' : '⚠️';
    console.log(
      `${status} ${account.platform} - ${account.accountId} (${account.status}) - Linked to ${linkedDevices} device(s)`,
    );
  }

  // Get test account
  console.log('\n\n🧪 Test Account Status:\n');
  const testAccount = await prisma.account.findUnique({
    where: {
      platform_accountId: {
        platform: 'QUOTEX',
        accountId: 'TEST_ACTIVE_123',
      },
    },
    include: {
      devices: {
        include: {
          device: true,
        },
      },
    },
  });

  if (testAccount) {
    console.log(`✅ Test account found: TEST_ACTIVE_123`);
    console.log(`   Status: ${testAccount.status}`);
    console.log(`   Linked to ${testAccount.devices.length} device(s)`);

    if (testAccount.devices.length === 0) {
      console.log('   ⚠️  Not linked to any device!');
      console.log('\n💡 To link test account to a device:');
      console.log('   1. Open the app and verify account with ID: TEST_ACTIVE_123');
      console.log('   2. Or use Admin API to link manually');
    } else {
      for (const da of testAccount.devices) {
        console.log(`   📱 Linked to device: ${da.device.deviceId}`);
      }
    }
  } else {
    console.log('❌ Test account not found!');
    console.log('   Run: npm run prisma:seed');
  }

  // Count active signals
  const activeSignals = await prisma.signal.count({
    where: { active: true },
  });
  console.log(`\n\n📈 Active signals: ${activeSignals}`);
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });

