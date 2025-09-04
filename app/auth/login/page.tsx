'use client';

import { useUser, SignIn } from '@stackframe/stack';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import Link from "next/link";
import { Leaf } from "lucide-react";
import { stackApp } from "@/lib/stack";

export default function Login() {
  const user = useUser();
  const router = useRouter();
  
  // Redirect to account page if user is logged in
  useEffect(() => {
    if (user) {
      router.push('/account');
    }
  }, [user, router]);

  // Show loading while redirecting
  if (user) {
    return (
      <div className="min-h-screen bg-[#F9E7C9] flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#ba7500] mx-auto mb-4"></div>
          <p className="text-lg mb-4">Redirecting to your account...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#F9E7C9]">
      {/* Header */}
      <header className="bg-[#F9E7C9]/80 backdrop-blur-sm border-b border-[#ba7500]/20">
        <div className="container mx-auto px-4 py-4">
          <Link href="/" className="flex items-center space-x-3 group">
            <div className="w-10 h-10 bg-gradient-to-br from-[#ba7500] to-[#C4C240] rounded-lg flex items-center justify-center">
              <Leaf className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-[#ba7500]">
              BETTER BEING
            </span>
          </Link>
        </div>
      </header>

      <div className="pt-12 pb-16">
        <div className="container mx-auto px-4">
          <div className="max-w-md mx-auto">
            {/* Header */}
            <div className="text-center mb-8">
              <div className="w-16 h-16 bg-gradient-to-br from-[#ba7500] to-[#C4C240] rounded-xl flex items-center justify-center mx-auto mb-4">
                <Leaf className="h-8 w-8 text-white" />
              </div>
              <h1 className="text-3xl font-bold text-[#ba7500] mb-2">
                Welcome Back
              </h1>
              <p className="text-[#7A7771]">
                Sign in to your Better Being account
              </p>
            </div>

            {/* Stack Auth Login Component */}
            <div className="bg-white/50 backdrop-blur-sm border border-[#ba7500]/20 rounded-lg p-8">
              <div className="text-center mb-6">
                <h2 className="text-2xl font-semibold text-[#ba7500] mb-2">
                  Sign In
                </h2>
                <p className="text-[#7A7771] text-sm">
                  Enter your credentials to access your account
                </p>
              </div>

              {/* Stack Auth SignIn Component */}
              <div className="stack-auth-container">
                <SignIn />
              </div>

              {/* Back to Home */}
              <div className="mt-6 text-center">
                <Link
                  href="/"
                  className="text-sm text-[#7A7771] hover:text-[#ba7500] hover:underline"
                >
                  ← Back to Home
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
