import { Router } from 'express';
import { PrismaClient } from '@prisma/client';
import { authMiddleware } from '../middlewares/auth';

const router = Router();
const prisma = new PrismaClient();

// CONTENT CRUD
router.get('/', authMiddleware, async (req, res) => {
  const content = await prisma.content.findMany();
  res.json(content);
});
router.post('/', authMiddleware, async (req, res) => {
  if (req.user.role !== 'admin') return res.status(403).json({ error: 'Admin only' });
  const { title, body, published } = req.body;
  const record = await prisma.content.create({ data: { title, body, published: !!published, userId: req.user.userId } });
  res.status(201).json(record);
});

export default router;

