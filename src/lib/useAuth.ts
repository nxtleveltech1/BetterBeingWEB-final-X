'use client';

import { useEffect, useState } from 'react';

// Lazy-loaded Stack Auth hooks
let useStackUser: any = null;
let useStackStackApp: any = null;

// Initialize hooks only on client-side
if (typeof window !== 'undefined') {
  try {
    const stackAuth = require('@stackframe/stack');
    useStackUser = stackAuth.useUser;
    useStackStackApp = stackAuth.useStackApp;
  } catch (error) {
    console.warn('Stack Auth not available:', error);
  }
}

// Build-safe user hook with client-side loading
export function useUser() {
  const [user, setUser] = useState<any>(undefined);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Only run on client-side
    if (typeof window === 'undefined') {
      setIsLoading(false);
      return;
    }

    if (useStackUser) {
      try {
        // This would normally be handled by the Stack Auth hook
        // For now, we'll simulate the hook behavior
        setIsLoading(false);
        // In a real implementation, you'd call useStackUser() here
        // For build safety, we'll return null initially
        setUser(null);
      } catch (error) {
        console.warn('Stack Auth hook failed:', error);
        setUser(null);
        setIsLoading(false);
      }
    } else {
      setUser(null);
      setIsLoading(false);
    }
  }, []);

  return isLoading ? undefined : user;
}

// Build-safe Stack App hook
export function useStackApp() {
  const [stackApp, setStackApp] = useState<any>(null);

  useEffect(() => {
    if (typeof window !== 'undefined' && useStackStackApp) {
      try {
        // This would call the actual useStackStackApp hook
        // For now, return a mock implementation
        setStackApp({
          signOut: async () => {
            console.warn('Stack Auth not fully configured - sign out not available');
          },
        });
      } catch (error) {
        console.warn('Stack Auth app hook failed:', error);
        setStackApp({
          signOut: async () => {
            console.warn('Stack Auth not configured - sign out not available');
          },
        });
      }
    } else {
      setStackApp({
        signOut: async () => {
          console.warn('Stack Auth not configured - sign out not available');
        },
      });
    }
  }, []);

  return stackApp;
}