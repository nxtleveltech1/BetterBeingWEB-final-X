import { StackServerApp } from '@stackframe/stack';

// Build-safe Stack Auth configuration
const isDevelopment = process.env.NODE_ENV === 'development';
const isBuild = process.env.NEXT_PHASE === 'phase-production-build' || process.env.NODE_ENV === 'production';

// During build phase, provide minimal mock configuration that won't fail validation
const projectId = process.env.NEXT_PUBLIC_STACK_PROJECT_ID || 'build-mock-project-id';
const publishableKey = process.env.NEXT_PUBLIC_STACK_PUBLISHABLE_CLIENT_KEY || 'build-mock-publishable-key';
const secretKey = process.env.STACK_SECRET_SERVER_KEY || 'build-mock-secret-key';

// Only export when not in build phase or when properly configured
export const stackServerApp = (() => {
  try {
    // During build phase with missing env vars, create minimal instance
    if (isBuild && !process.env.NEXT_PUBLIC_STACK_PROJECT_ID) {
      console.log('Stack Auth: Using build-time mock configuration');
      
      // Create mock app that won't cause validation errors during build
      return {
        url: '/handler',
        projectId: 'build-mock',
        // Minimal methods needed for build compatibility
        validateToken: () => Promise.resolve(null),
        signOut: () => Promise.resolve(),
      } as any; // Type assertion for build compatibility
    }
    
    return new StackServerApp({
      tokenStore: 'nextjs-cookie',
      projectId,
      publishableClientKey: publishableKey,
      secretServerKey: secretKey,
    });
  } catch (error) {
    console.warn('Stack Auth initialization failed:', error);
    // Return mock object to prevent build failures
    return {
      url: '/handler',
      projectId: 'error-fallback',
      validateToken: () => Promise.resolve(null),
      signOut: () => Promise.resolve(),
    } as any;
  }
})();