import { Router } from 'express';
import authRoutes from './auth';
import userRoutes from './users';
import contentRoutes from './content';
import feedbackRoutes from './feedback';

const router = Router();

router.use('/auth', authRoutes);
router.use('/user', userRoutes);
router.use('/content', contentRoutes);
router.use('/feedback', feedbackRoutes);

export default router;

