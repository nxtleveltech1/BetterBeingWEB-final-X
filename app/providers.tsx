"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactNode, useState } from "react";
import { CartProviderOptimized } from "@/contexts/CartContextOptimized";

export default function Providers({ children }: { children: ReactNode }) {
  const [queryClient] = useState(() => new QueryClient());
  return (
    <QueryClientProvider client={queryClient}>
      <CartProviderOptimized>
        {children}
      </CartProviderOptimized>
    </QueryClientProvider>
  );
}
