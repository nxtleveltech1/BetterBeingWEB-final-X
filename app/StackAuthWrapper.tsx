'use client';

import { ReactNode } from 'react';
import { MockStackProvider } from './mockStackAuth';

// Simple wrapper that uses mock Stack Auth during build/deployment
export default function StackAuthWrapper({ children }: { children: ReactNode }) {
  // Use mock Stack Auth provider to maintain component compatibility
  // TODO: Re-enable real Stack Auth when environment variables are properly configured
  return (
    <MockStackProvider>
      {children}
    </MockStackProvider>
  );
}