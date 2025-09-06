import { Router } from 'express';
import { PrismaClient } from '@prisma/client';
import { authMiddleware } from '../middlewares/auth';

const router = Router();
const prisma = new PrismaClient();

// FEEDBACK CREATE & LIST
router.get('/', authMiddleware, async (req, res) => {
  const feedback = await prisma.feedback.findMany();
  res.json(feedback);
});
router.post('/', authMiddleware, async (req, res) => {
  const { message } = req.body;
  const entry = await prisma.feedback.create({ data: { message, userId: req.user.userId } });
  res.status(201).json(entry);
});

export default router;

