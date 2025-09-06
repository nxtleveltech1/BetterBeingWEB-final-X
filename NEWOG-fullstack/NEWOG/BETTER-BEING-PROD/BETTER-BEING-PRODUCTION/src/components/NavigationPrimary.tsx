import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Search, ShoppingCart, Heart, User, Menu, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { useAuth } from '@/contexts/AuthContext';
import { useCart } from '@/contexts/CartContext';

const NavigationPrimary = () => {
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const { cartItems } = useCart();

  useEffect(() => {
    const handleScroll = () => {
      const isScrolled = window.scrollY > 50;
      if (isScrolled !== scrolled) {
        setScrolled(isScrolled);
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, [scrolled]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/products?search=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  const cartItemCount = cartItems?.length || 0;

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled
          ? 'bg-white/90 backdrop-blur-md shadow-lg border-b border-gray-200/20'
          : 'bg-transparent'
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <div className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
              Better Being
            </div>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            <Link to="/products" className="text-gray-700 hover:text-purple-600 transition-colors">
              Products
            </Link>
            <Link to="/wellness" className="text-gray-700 hover:text-purple-600 transition-colors">
              Wellness
            </Link>
            <Link to="/blog" className="text-gray-700 hover:text-purple-600 transition-colors">
              Blog
            </Link>
            <Link to="/about" className="text-gray-700 hover:text-purple-600 transition-colors">
              About
            </Link>
            <Link to="/community" className="text-gray-700 hover:text-purple-600 transition-colors">
              Community
            </Link>
            <Link to="/contact" className="text-gray-700 hover:text-purple-600 transition-colors">
              Contact
            </Link>
          </div>

          {/* Desktop Actions */}
          <div className="hidden md:flex items-center space-x-4">
            <form onSubmit={handleSearch} className="relative">
              <Input
                type="search"
                placeholder="Search..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 pr-4 py-2 w-64 bg-white/80 backdrop-blur-sm"
              />
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            </form>

            <Link to="/wishlist">
              <Button variant="ghost" size="icon">
                <Heart className="h-5 w-5" />
              </Button>
            </Link>

            <Link to="/cart">
              <Button variant="ghost" size="icon" className="relative">
                <ShoppingCart className="h-5 w-5" />
                {cartItemCount > 0 && (
                  <Badge variant="destructive" className="absolute -top-1 -right-1 h-5 w-5 p-0 flex items-center justify-center">
                    {cartItemCount}
                  </Badge>
                )}
              </Button>
            </Link>

            {user ? (
              <div className="flex items-center space-x-2">
                <Link to="/account">
                  <Button variant="ghost" size="icon">
                    <User className="h-5 w-5" />
                  </Button>
                </Link>
                <Button variant="ghost" size="sm" onClick={logout}>
                  Logout
                </Button>
              </div>
            ) : (
              <Link to="/login">
                <Button variant="default" size="sm">
                  Sign In
                </Button>
              </Link>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-white/95 backdrop-blur-md border-t border-gray-200/20">
          <div className="px-4 pt-2 pb-3 space-y-1">
            <Link
              to="/products"
              className="block px-3 py-2 text-base font-medium text-gray-700 hover:text-purple-600"
              onClick={() => setMobileMenuOpen(false)}
            >
              Products
            </Link>
            <Link
              to="/wellness"
              className="block px-3 py-2 text-base font-medium text-gray-700 hover:text-purple-600"
              onClick={() => setMobileMenuOpen(false)}
            >
              Wellness
            </Link>
            <Link
              to="/blog"
              className="block px-3 py-2 text-base font-medium text-gray-700 hover:text-purple-600"
              onClick={() => setMobileMenuOpen(false)}
            >
              Blog
            </Link>
            <Link
              to="/about"
              className="block px-3 py-2 text-base font-medium text-gray-700 hover:text-purple-600"
              onClick={() => setMobileMenuOpen(false)}
            >
              About
            </Link>
            <Link
              to="/community"
              className="block px-3 py-2 text-base font-medium text-gray-700 hover:text-purple-600"
              onClick={() => setMobileMenuOpen(false)}
            >
              Community
            </Link>
            <Link
              to="/contact"
              className="block px-3 py-2 text-base font-medium text-gray-700 hover:text-purple-600"
              onClick={() => setMobileMenuOpen(false)}
            >
              Contact
            </Link>
            
            {/* Additional Pages */}
            <div className="border-t border-gray-200/20 pt-2 mt-2">
              <Link
                to="/farming"
                className="block px-3 py-2 text-sm font-medium text-gray-600 hover:text-purple-600"
                onClick={() => setMobileMenuOpen(false)}
              >
                Farming Solutions
              </Link>
              <Link
                to="/store-locator"
                className="block px-3 py-2 text-sm font-medium text-gray-600 hover:text-purple-600"
                onClick={() => setMobileMenuOpen(false)}
              >
                Store Locator
              </Link>
              <Link
                to="/become-stockist"
                className="block px-3 py-2 text-sm font-medium text-gray-600 hover:text-purple-600"
                onClick={() => setMobileMenuOpen(false)}
              >
                Become a Stockist
              </Link>
              <Link
                to="/testimonials"
                className="block px-3 py-2 text-sm font-medium text-gray-600 hover:text-purple-600"
                onClick={() => setMobileMenuOpen(false)}
              >
                Testimonials
              </Link>
            </div>
          </div>
          <div className="px-4 pb-3 border-t border-gray-200/20">
            <form onSubmit={handleSearch} className="mb-3">
              <Input
                type="search"
                placeholder="Search..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full"
              />
            </form>
            <div className="flex items-center justify-between">
              <div className="flex space-x-2">
                <Link to="/wishlist">
                  <Button variant="ghost" size="icon">
                    <Heart className="h-5 w-5" />
                  </Button>
                </Link>
                <Link to="/cart">
                  <Button variant="ghost" size="icon" className="relative">
                    <ShoppingCart className="h-5 w-5" />
                    {cartItemCount > 0 && (
                      <Badge variant="destructive" className="absolute -top-1 -right-1 h-5 w-5 p-0 flex items-center justify-center">
                        {cartItemCount}
                      </Badge>
                    )}
                  </Button>
                </Link>
              </div>
              {user ? (
                <div className="flex items-center space-x-2">
                  <Link to="/account">
                    <Button variant="ghost" size="icon">
                      <User className="h-5 w-5" />
                    </Button>
                  </Link>
                  <Button variant="ghost" size="sm" onClick={logout}>
                    Logout
                  </Button>
                </div>
              ) : (
                <Link to="/login">
                  <Button variant="default" size="sm">
                    Sign In
                  </Button>
                </Link>
              )}
            </div>
          </div>
        </div>
      )}
    </nav>
  );
};

// Export a wrapper component that includes the spacer
export const NavigationWithSpacer = () => {
  return (
    <>
      <NavigationPrimary />
      <div className="h-16" /> {/* Spacer to prevent content from hiding behind fixed nav */}
    </>
  );
};

export default NavigationPrimary;
export { NavigationPrimary };