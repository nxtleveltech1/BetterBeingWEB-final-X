'use client';

import { ReactNode } from 'react';
import { MockStackProvider } from './mockStackAuth';
import { stackApp } from '@/lib/stack';

export default function StackAuthWrapper({ children }: { children: ReactNode }) {
  // If Stack Auth env vars are configured, wrap the app in the real provider.
  // Otherwise, fall back to a mock provider to keep the UI working without auth.
  const hasStackEnv = Boolean(process.env.NEXT_PUBLIC_STACK_PROJECT_ID);

  if (hasStackEnv) {
    const { StackProvider } = require('@stackframe/stack');
    return (
      <StackProvider app={stackApp}>
        {children}
      </StackProvider>
    );
  }

  return (
    <MockStackProvider>
      {children}
    </MockStackProvider>
  );
}
