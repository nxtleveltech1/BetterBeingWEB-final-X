import React from 'react';
import { Link } from 'react-router-dom';
import { Facebook, Twitter, Instagram, Youtube } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';

const FooterPrimary = () => {
  return (
    <footer className="bg-gray-900 text-gray-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="space-y-4">
            <h3 className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
              Better Being
            </h3>
            <p className="text-sm">
              Your journey to wellness starts here. Discover premium supplements and wellness products.
            </p>
            <div className="flex space-x-4">
              <a href="#" className="hover:text-white transition-colors">
                <Facebook className="h-5 w-5" />
              </a>
              <a href="#" className="hover:text-white transition-colors">
                <Twitter className="h-5 w-5" />
              </a>
              <a href="#" className="hover:text-white transition-colors">
                <Instagram className="h-5 w-5" />
              </a>
              <a href="#" className="hover:text-white transition-colors">
                <Youtube className="h-5 w-5" />
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-lg font-semibold text-white mb-4">Quick Links</h4>
            <ul className="space-y-2">
              <li>
                <Link to="/products" className="hover:text-white transition-colors">
                  Products
                </Link>
              </li>
              <li>
                <Link to="/wellness" className="hover:text-white transition-colors">
                  Wellness Hub
                </Link>
              </li>
              <li>
                <Link to="/blog" className="hover:text-white transition-colors">
                  Blog
                </Link>
              </li>
              <li>
                <Link to="/community" className="hover:text-white transition-colors">
                  Community
                </Link>
              </li>
              <li>
                <Link to="/farming" className="hover:text-white transition-colors">
                  Farming Solutions
                </Link>
              </li>
              <li>
                <Link to="/about" className="hover:text-white transition-colors">
                  About Us
                </Link>
              </li>
              <li>
                <Link to="/contact" className="hover:text-white transition-colors">
                  Contact
                </Link>
              </li>
            </ul>
          </div>

          {/* Services & Support */}
          <div>
            <h4 className="text-lg font-semibold text-white mb-4">Services & Support</h4>
            <ul className="space-y-2">
              <li>
                <Link to="/account" className="hover:text-white transition-colors">
                  My Account
                </Link>
              </li>
              <li>
                <Link to="/shipping" className="hover:text-white transition-colors">
                  Shipping Info
                </Link>
              </li>
              <li>
                <Link to="/refund-policy" className="hover:text-white transition-colors">
                  Refund Policy
                </Link>
              </li>
              <li>
                <Link to="/store-locator" className="hover:text-white transition-colors">
                  Store Locator
                </Link>
              </li>
              <li>
                <Link to="/testimonials" className="hover:text-white transition-colors">
                  Testimonials
                </Link>
              </li>
              <li>
                <Link to="/become-stockist" className="hover:text-white transition-colors">
                  Become a Stockist
                </Link>
              </li>
            </ul>
          </div>

          {/* Newsletter */}
          <div>
            <h4 className="text-lg font-semibold text-white mb-4">Stay Updated</h4>
            <p className="text-sm mb-4">
              Subscribe to our newsletter for wellness tips and exclusive offers.
            </p>
            <form className="space-y-2">
              <Input
                type="email"
                placeholder="Your email"
                className="bg-gray-800 border-gray-700 text-white placeholder-gray-400"
              />
              <Button className="w-full bg-purple-600 hover:bg-purple-700">
                Subscribe
              </Button>
            </form>
          </div>
        </div>

        <div className="mt-12 pt-8 border-t border-gray-800">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <p className="text-sm">
              © 2024 Better Being. All rights reserved.
            </p>
            <div className="flex flex-wrap gap-4 mt-4 md:mt-0 text-sm">
              <Link to="/privacy" className="hover:text-white transition-colors">
                Privacy Policy
              </Link>
              <Link to="/terms" className="hover:text-white transition-colors">
                Terms of Service
              </Link>
              <Link to="/refund-policy" className="hover:text-white transition-colors">
                Refund Policy
              </Link>
              <Link to="/marketing" className="hover:text-white transition-colors">
                Marketing Partners
              </Link>
              <Link to="/investors-pool" className="hover:text-white transition-colors">
                Investors
              </Link>
              <Link to="/tech" className="hover:text-white transition-colors">
                Technology
              </Link>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default FooterPrimary;
export { FooterPrimary };