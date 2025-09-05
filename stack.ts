import { StackServerApp } from '@stackframe/stack';

export const stackServerApp = new StackServerApp({
  tokenStore: 'nextjs-cookie', 
  projectId: process.env.NEXT_PUBLIC_STACK_PROJECT_ID || 'demo-project-id',
  publishableClientKey: process.env.NEXT_PUBLIC_STACK_PUBLISHABLE_CLIENT_KEY || 'demo-client-key',
  secretServerKey: process.env.STACK_SECRET_SERVER_KEY || 'demo-secret-key',
});