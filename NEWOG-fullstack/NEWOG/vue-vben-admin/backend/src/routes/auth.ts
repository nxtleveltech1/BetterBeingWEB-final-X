import { Router } from 'express';
import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';

const router = Router();
const prisma = new PrismaClient();

// POST /auth/login { email, password }
router.post('/login', async (req, res) => {
  const { email, password } = req.body;
  const user = await prisma.user.findUnique({ where: { email } });
  if (!user) return res.status(401).json({ error: 'Invalid email or password' });
  const isMatch = await bcrypt.compare(password, user.password);
  if (!isMatch) return res.status(401).json({ error: 'Invalid email or password' });
  const token = jwt.sign(
    { userId: user.id, role: user.role },
    process.env.STACK_SECRET_SERVER_KEY || 'SECRET_KEY',
    { expiresIn: '7d' }
  );
  res.json({ token });
});

export default router;

