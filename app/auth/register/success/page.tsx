'use client';

import Link from "next/link";
import { 
  CheckCircle, 
  Mail, 
  ArrowRight,
  Leaf,
  Clock,
  Shield
} from "lucide-react";

export default function RegisterSuccess() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[var(--color-neutral-50)] to-[var(--color-neutral-100)]">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-[var(--color-neutral-200)]">
        <div className="container mx-auto px-4 py-4">
          <Link href="/" className="flex items-center space-x-3 group">
            <div className="w-10 h-10 bg-gradient-to-br from-[var(--bb-mahogany)] to-[var(--bb-citron)] rounded-lg flex items-center justify-center shadow-wellness">
              <Leaf className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-heading font-bold text-[var(--color-neutral-900)] tracking-brand">
              BETTER BEING
            </span>
          </Link>
        </div>
      </header>

      <div className="pt-16 pb-20">
        <div className="container mx-auto px-4">
          <div className="max-w-2xl mx-auto text-center">
            {/* Success Icon */}
            <div className="w-24 h-24 bg-gradient-to-br from-green-400 to-green-600 rounded-full flex items-center justify-center mx-auto mb-8 shadow-lg">
              <CheckCircle className="w-12 h-12 text-white" />
            </div>

            {/* Success Message */}
            <h1 className="text-4xl font-heading font-bold text-[var(--color-neutral-900)] mb-4">
              Welcome to Better Being!
            </h1>
            <p className="text-xl text-[var(--color-neutral-600)] mb-8 leading-relaxed">
              Your account has been successfully created. We've sent a verification email to your inbox.
            </p>

            {/* Verification Steps */}
            <div className="bg-white rounded-2xl p-8 mb-8 border border-[var(--color-neutral-200)] shadow-sm">
              <h2 className="text-2xl font-heading font-semibold text-[var(--color-neutral-900)] mb-6">
                Next Steps
              </h2>
              
              <div className="space-y-6 text-left">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                    <Mail className="w-6 h-6 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-[var(--color-neutral-900)] mb-1">
                      Check Your Email
                    </h3>
                    <p className="text-[var(--color-neutral-600)]">
                      We've sent a verification link to your email address. Click the link to verify your account.
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center flex-shrink-0">
                    <Clock className="w-6 h-6 text-orange-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-[var(--color-neutral-900)] mb-1">
                      Verification Time
                    </h3>
                    <p className="text-[var(--color-neutral-600)]">
                      The verification link is valid for 24 hours. Please verify your email within this time.
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
                    <Shield className="w-6 h-6 text-green-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-[var(--color-neutral-900)] mb-1">
                      Secure Account
                    </h3>
                    <p className="text-[var(--color-neutral-600)]">
                      Email verification helps us keep your account secure and ensures you receive important updates.
                    </p>
                  </div>
                </div>
              </div>

              {/* Didn't Receive Email */}
              <div className="mt-8 pt-6 border-t border-[var(--color-neutral-200)]">
                <p className="text-[var(--color-neutral-600)] text-sm mb-4">
                  Didn't receive the email? Check your spam folder or:
                </p>
                <button className="text-[var(--bb-mahogany)] hover:text-[var(--bb-citron)] text-sm font-medium transition-colors">
                  Resend verification email
                </button>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/auth/login"
                className="btn-primary px-8 py-3 text-lg"
              >
                Sign In Now
                <ArrowRight className="w-5 h-5 ml-2" />
              </Link>
              
              <Link
                href="/products"
                className="btn-secondary px-8 py-3 text-lg"
              >
                Browse Products
              </Link>
            </div>

            {/* Support */}
            <div className="mt-12 pt-8 border-t border-[var(--color-neutral-200)]">
              <p className="text-[var(--color-neutral-600)]">
                Need help?{' '}
                <Link href="/support" className="text-[var(--bb-mahogany)] hover:text-[var(--bb-citron)] font-medium hover:underline">
                  Contact our support team
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}