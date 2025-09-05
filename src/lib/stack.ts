import { StackClientApp } from '@stackframe/stack';

export const stackApp = new StackClientApp({
  tokenStore: 'nextjs-cookie',
  projectId: process.env.NEXT_PUBLIC_STACK_PROJECT_ID || 'demo-project-id',
  publishableClientKey: process.env.NEXT_PUBLIC_STACK_PUBLISHABLE_CLIENT_KEY || 'demo-client-key',
  urls: {
    signIn: '/auth/login',
    afterSignIn: '/account',
    afterSignUp: '/account',
    signUp: '/auth/signup',
  },
});