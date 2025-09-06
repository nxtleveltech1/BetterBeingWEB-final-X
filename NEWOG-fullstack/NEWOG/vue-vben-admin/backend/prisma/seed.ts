import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcrypt';

const prisma = new PrismaClient();
const ADMIN_EMAIL = process.env.ADMIN_EMAIL || 'admin@betterbeing.com';
const DEFAULT_PASSWORD = process.env.ADMIN_PASSWORD || 'admin123';

async function main() {
  const pwHash = await bcrypt.hash(DEFAULT_PASSWORD, 10);
  await prisma.user.upsert({
    where: { email: ADMIN_EMAIL },
    update: {},
    create: {
      email: ADMIN_EMAIL,
      password: pwHash,
      name: 'Admin User',
      role: 'admin',
    },
  });
  console.log('Admin seeded:', ADMIN_EMAIL);
}

main().finally(() => prisma.$disconnect());

