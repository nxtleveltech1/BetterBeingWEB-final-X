'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { CheckCircle, Package, Mail, ArrowRight, Download, Calendar } from 'lucide-react';

// Mock order data - would come from API/database
const mockOrder = {
  orderNumber: 'ORD-' + Math.random().toString().substr(2, 6),
  orderDate: new Date().toLocaleDateString('en-ZA'),
  expectedDelivery: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toLocaleDateString('en-ZA'),
  email: 'customer@example.com',
  total: 299.97,
  items: [
    { name: 'Organic Ashwagandha Capsules', quantity: 2, price: 89.99 },
    { name: 'Himalayan Shilajit Resin', quantity: 1, price: 149.99 }
  ]
};

export default function CheckoutSuccessPage() {
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    setIsLoaded(true);
  }, []);

  if (!isLoaded) {
    return (
      <div className="min-h-screen bg-[#F9E7C9] flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#ba7500]"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#F9E7C9] py-8">
      <div className="max-w-4xl mx-auto px-6">
        {/* Success Header */}
        <div className="text-center mb-8">
          <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4 border-4 border-green-500">
            <CheckCircle className="w-10 h-10 text-green-500" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Order Confirmed!</h1>
          <p className="text-gray-600 text-lg">Thank you for your purchase. Your order has been successfully placed.</p>
        </div>

        {/* Order Details Card */}
        <div className="bg-white rounded-xl shadow-lg overflow-hidden mb-8">
          {/* Order Summary Header */}
          <div className="bg-[#ba7500] text-white p-6">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-xl font-bold mb-1">Order #{mockOrder.orderNumber}</h2>
                <p className="opacity-90">Placed on {mockOrder.orderDate}</p>
              </div>
              <div className="text-right">
                <p className="text-sm opacity-90">Total</p>
                <p className="text-2xl font-bold">R{mockOrder.total.toFixed(2)}</p>
              </div>
            </div>
          </div>

          {/* Order Details Content */}
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {/* Order Items */}
              <div>
                <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <Package className="w-5 h-5 text-[#ba7500]" />
                  Items Ordered
                </h3>
                <div className="space-y-3">
                  {mockOrder.items.map((item, index) => (
                    <div key={index} className="flex justify-between items-center py-2 border-b border-gray-100">
                      <div>
                        <p className="font-medium text-gray-900">{item.name}</p>
                        <p className="text-sm text-gray-600">Quantity: {item.quantity}</p>
                      </div>
                      <p className="font-semibold text-[#ba7500]">R{(item.price * item.quantity).toFixed(2)}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Delivery Information */}
              <div>
                <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <Calendar className="w-5 h-5 text-[#ba7500]" />
                  Delivery Information
                </h3>
                <div className="space-y-3">
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <p className="text-sm text-green-800 font-medium mb-1">Expected Delivery</p>
                    <p className="text-lg font-bold text-green-900">{mockOrder.expectedDelivery}</p>
                    <p className="text-sm text-green-700 mt-1">2-3 business days</p>
                  </div>
                  
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Mail className="w-4 h-4 text-blue-600" />
                      <p className="text-sm text-blue-800 font-medium">Confirmation Email Sent</p>
                    </div>
                    <p className="text-sm text-blue-700">
                      We've sent order confirmation and tracking details to {mockOrder.email}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Next Steps */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <h3 className="font-semibold text-gray-900 mb-4">What happens next?</h3>
          <div className="space-y-4">
            <div className="flex items-start gap-4">
              <div className="w-8 h-8 bg-[#ba7500] text-white rounded-full flex items-center justify-center flex-shrink-0 text-sm font-bold">
                1
              </div>
              <div>
                <p className="font-medium text-gray-900">Order Processing</p>
                <p className="text-gray-600 text-sm">We're preparing your wellness products with care and attention.</p>
              </div>
            </div>
            
            <div className="flex items-start gap-4">
              <div className="w-8 h-8 bg-[#ba7500] text-white rounded-full flex items-center justify-center flex-shrink-0 text-sm font-bold">
                2
              </div>
              <div>
                <p className="font-medium text-gray-900">Quality Check & Packaging</p>
                <p className="text-gray-600 text-sm">Each item is carefully inspected and securely packaged for shipping.</p>
              </div>
            </div>
            
            <div className="flex items-start gap-4">
              <div className="w-8 h-8 bg-[#ba7500] text-white rounded-full flex items-center justify-center flex-shrink-0 text-sm font-bold">
                3
              </div>
              <div>
                <p className="font-medium text-gray-900">Shipping & Tracking</p>
                <p className="text-gray-600 text-sm">You'll receive tracking information via email once your order ships.</p>
              </div>
            </div>
            
            <div className="flex items-start gap-4">
              <div className="w-8 h-8 bg-green-500 text-white rounded-full flex items-center justify-center flex-shrink-0 text-sm font-bold">
                4
              </div>
              <div>
                <p className="font-medium text-gray-900">Delivery</p>
                <p className="text-gray-600 text-sm">Your wellness journey continues with premium products at your door.</p>
              </div>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/account"
            className="bg-[#ba7500] text-white px-6 py-3 rounded-lg hover:bg-[#ba7500]/90 transition-colors text-center flex items-center justify-center gap-2"
          >
            <Package className="w-5 h-5" />
            View Order History
          </Link>
          
          <Link
            href="/products"
            className="border-2 border-[#ba7500] text-[#ba7500] px-6 py-3 rounded-lg hover:bg-[#ba7500] hover:text-white transition-colors text-center flex items-center justify-center gap-2"
          >
            Continue Shopping
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>

        {/* Support Information */}
        <div className="text-center mt-8 p-4 bg-gray-50 rounded-lg">
          <p className="text-gray-600 text-sm mb-2">
            Need help with your order? Have questions about our products?
          </p>
          <Link
            href="/contact"
            className="text-[#ba7500] hover:text-[#ba7500]/80 font-medium text-sm"
          >
            Contact Our Wellness Support Team
          </Link>
        </div>
      </div>
    </div>
  );
}