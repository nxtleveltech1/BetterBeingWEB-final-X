import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Menu, X, Leaf, ShoppingBag, User } from "lucide-react";

export const Header = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-lg border-b border-border/50">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 rounded-full border-2 border-[#C1581B] flex items-center justify-center bg-white">
              <span className="text-[#C1581B] font-bold text-lg">BB</span>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-[#C1581B]">Better Being</h1>
              <p className="text-xs text-muted-foreground">Natural Wellness Solutions</p>
            </div>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <a href="/" className="text-foreground hover:text-primary transition-colors">Home</a>
            <a href="/products" className="text-foreground hover:text-primary transition-colors">Products</a>
            <a href="/community" className="text-foreground hover:text-primary transition-colors">Community</a>
            <a href="/farming" className="text-foreground hover:text-primary transition-colors">Farming</a>
            <a href="/testimonials" className="text-foreground hover:text-primary transition-colors">Reviews</a>
          </nav>

          {/* Desktop Actions */}
          <div className="hidden md:flex items-center space-x-4">
            <Button variant="ghost" size="sm">
              <User className="w-4 h-4 mr-2" />
              Login
            </Button>
            <Button variant="default" size="sm" className="shadow-wellness">
              <ShoppingBag className="w-4 h-4 mr-2" />
              Shop Now
            </Button>
          </div>

          {/* Mobile Menu Button */}
          <Button
            variant="ghost"
            size="sm"
            className="md:hidden"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
          >
            {isMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </Button>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden mt-4 pb-4 border-t border-border/50">
            <nav className="flex flex-col space-y-4 mt-4">
              <a href="/" className="text-foreground hover:text-primary transition-colors">Home</a>
              <a href="/products" className="text-foreground hover:text-primary transition-colors">Products</a>
              <a href="/community" className="text-foreground hover:text-primary transition-colors">Community</a>
              <a href="/farming" className="text-foreground hover:text-primary transition-colors">Farming</a>
              <a href="/testimonials" className="text-foreground hover:text-primary transition-colors">Reviews</a>
              <a href="/store-locator" className="text-foreground hover:text-primary transition-colors">Store Locator</a>
              <a href="/become-stockist" className="text-foreground hover:text-primary transition-colors">Become Stockist</a>
              <div className="flex flex-col space-y-2 pt-4">
                <Button variant="ghost" size="sm">
                  <User className="w-4 h-4 mr-2" />
                  Login
                </Button>
                <Button variant="default" size="sm">
                  <ShoppingBag className="w-4 h-4 mr-2" />
                  Shop Now
                </Button>
              </div>
            </nav>
          </div>
        )}
      </div>
    </header>
  );
};
