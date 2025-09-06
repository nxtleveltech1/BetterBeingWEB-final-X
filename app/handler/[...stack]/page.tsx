import { StackHandler } from "@stackframe/stack";

// Build-safe Stack Auth handler
export default function Handler(props: unknown) {
  // During build phase or when Stack Auth is not configured, return mock UI
  if (process.env.NODE_ENV !== 'development' && !process.env.NEXT_PUBLIC_STACK_PROJECT_ID) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-honey-100 to-cream-100">
        <div className="max-w-md mx-auto text-center p-8 bg-white rounded-lg shadow-lg">
          <h1 className="text-2xl font-bold text-chocolate-800 mb-4">Authentication Service</h1>
          <p className="text-chocolate-600 mb-6">
            Authentication is currently being configured. Please check back soon.
          </p>
          <div className="text-sm text-chocolate-500">
            Stack Auth configuration required
          </div>
        </div>
      </div>
    );
  }

  // Only import and use Stack Auth when environment is properly configured
  try {
    const { stackServerApp } = require("../../../stack");
    return <StackHandler fullPage app={stackServerApp} routeProps={props} />;
  } catch (error) {
    console.warn('Stack Auth configuration error:', error);
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-honey-100 to-cream-100">
        <div className="max-w-md mx-auto text-center p-8 bg-white rounded-lg shadow-lg">
          <h1 className="text-2xl font-bold text-chocolate-800 mb-4">Authentication Unavailable</h1>
          <p className="text-chocolate-600 mb-6">
            Authentication service is temporarily unavailable.
          </p>
          <div className="text-sm text-chocolate-500">
            Please contact support if this persists
          </div>
        </div>
      </div>
    );
  }
}
