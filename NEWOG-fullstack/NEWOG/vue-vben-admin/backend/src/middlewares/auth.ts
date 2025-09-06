import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';

// Add TS typing for req.user
export function authMiddleware(req: Request & { user?: any }, res: Response, next: NextFunction) {
  const header = req.headers['authorization'];
  const token = header && header.split(' ')[1];
  if (!token) return res.status(401).json({ error: 'Auth required' });
  try {
    const secret = process.env.STACK_SECRET_SERVER_KEY || 'SECRET_KEY';
    const user = jwt.verify(token, secret);
    req.user = user;
    next();
  } catch {
    res.status(401).json({ error: 'Invalid token' });
  }
}

