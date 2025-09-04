import { StackClientApp } from '@stackframe/stack';

export const stackApp = new StackClientApp({
  tokenStore: 'nextjs-cookie',
  projectId: process.env.NEXT_PUBLIC_STACK_PROJECT_ID!,
  publishableClientKey: process.env.NEXT_PUBLIC_STACK_PUBLISHABLE_CLIENT_KEY!,
  urls: {
    signIn: '/auth/login',
    afterSignIn: '/account',
    afterSignUp: '/account',
    signUp: '/auth/signup',
  },
});