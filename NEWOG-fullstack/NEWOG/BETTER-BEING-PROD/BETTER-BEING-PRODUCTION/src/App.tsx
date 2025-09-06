import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "@/contexts/AuthContext";
import { CartProvider } from "@/contexts/CartContext";
import Index from "./pages/Index";
import NotFound from "./pages/NotFound";
import Products from "./pages/Products";
import ProductDetail from "./pages/ProductDetail";
// New pages from Our Grounds analysis
import BecomeStockist from "./pages/BecomeStockist";
import Marketing from "./pages/Marketing";
import Tech from "./pages/Tech";
import InvestorsPool from "./pages/InvestorsPool";
import Testimonials from "./pages/Testimonials";
import StoreLocator from "./pages/StoreLocator";
import RefundPolicy from "./pages/RefundPolicy";
import Farming from "./pages/Farming";
import Community from "./pages/Community";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <AuthProvider>
      <CartProvider>
        <TooltipProvider>
          <Toaster />
          <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Index />} />
          <Route path="/products" element={<Products />} />
          <Route path="/product/:id" element={<ProductDetail />} />
          
          {/* New routes from Our Grounds scraping */}
          <Route path="/become-stockist" element={<BecomeStockist />} />
          <Route path="/marketing" element={<Marketing />} />
          <Route path="/tech" element={<Tech />} />
          <Route path="/investors-pool" element={<InvestorsPool />} />
          <Route path="/testimonials" element={<Testimonials />} />
          <Route path="/store-locator" element={<StoreLocator />} />
          <Route path="/refund-policy" element={<RefundPolicy />} />
          <Route path="/farming" element={<Farming />} />
          <Route path="/community" element={<Community />} />

          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
        </TooltipProvider>
      </CartProvider>
    </AuthProvider>
  </QueryClientProvider>
);

export default App;
