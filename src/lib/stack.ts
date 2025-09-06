import { StackClientApp } from '@stackframe/stack';

// Check if we're in build mode and provide valid dummy values to prevent build failures
const isBuild = process.env.NEXT_PHASE === 'phase-production-build';

// Use valid dummy values that Stack Auth will accept
const projectId = process.env.NEXT_PUBLIC_STACK_PROJECT_ID || (isBuild ? 'st_tcuTCuGSEeaE' : 'demo-project-id');
const publishableKey = process.env.NEXT_PUBLIC_STACK_PUBLISHABLE_CLIENT_KEY || (isBuild ? 'st_tcuTCuGSEeaE_pk' : 'demo-client-key');

export const stackApp = new StackClientApp({
  tokenStore: 'nextjs-cookie',
  projectId: projectId,
  publishableClientKey: publishableKey,
  urls: {
    signIn: '/auth/login',
    afterSignIn: '/account',
    afterSignUp: '/account',
    signUp: '/auth/signup',
  },
});