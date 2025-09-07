'use client';

import { ReactNode, useEffect, useState } from 'react';
import ClientBoundary from './components/ClientBoundary';

// Lazy load Stack Auth components to prevent build-time issues
const StackProvider = (() => {
  try {
    // Only import on client-side
    if (typeof window !== 'undefined') {
      return require('@stackframe/stack').StackProvider;
    }
    return null;
  } catch (error) {
    console.warn('Stack Auth not available:', error);
    return null;
  }
})();

const StackClientApp = (() => {
  try {
    if (typeof window !== 'undefined') {
      return require('@stackframe/stack').StackClientApp;
    }
    return null;
  } catch (error) {
    console.warn('Stack Auth not available:', error);
    return null;
  }
})();

interface StackAuthProviderProps {
  children: ReactNode;
}

function StackAuthContent({ children }: StackAuthProviderProps) {
  const [stackApp, setStackApp] = useState<any>(null);

  useEffect(() => {
    // Initialize Stack Auth only on client-side with proper environment
    if (
      typeof window !== 'undefined' && 
      StackClientApp && 
      process.env.NEXT_PUBLIC_STACK_PROJECT_ID &&
      process.env.NEXT_PUBLIC_STACK_PUBLISHABLE_CLIENT_KEY
    ) {
      try {
        const app = new StackClientApp({
          tokenStore: 'nextjs-cookie',
          projectId: process.env.NEXT_PUBLIC_STACK_PROJECT_ID,
          publishableClientKey: process.env.NEXT_PUBLIC_STACK_PUBLISHABLE_CLIENT_KEY,
          urls: {
            signIn: '/auth/login',
            afterSignIn: '/account',
            afterSignUp: '/account',
            signUp: '/auth/register',
          },
        });
        setStackApp(app);
      } catch (error) {
        console.error('Failed to initialize Stack Auth:', error);
      }
    }
  }, []);

  // If Stack Auth is available and configured, use provider
  if (stackApp && StackProvider) {
    return (
      <StackProvider app={stackApp}>
        {children}
      </StackProvider>
    );
  }

  // Fallback: render children without provider
  return <>{children}</>;
}

export default function StackAuthProvider({ children }: StackAuthProviderProps) {
  return (
    <ClientBoundary fallback={<>{children}</>}>
      <StackAuthContent>{children}</StackAuthContent>
    </ClientBoundary>
  );
}