'use client';

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html>
      <body>
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center space-y-4">
            <h2 className="text-2xl font-bold">Something went wrong!</h2>
            <button onClick={() => reset()} className="px-6 py-3 bg-gray-200 hover:bg-gray-300">
              Try again
            </button>
          </div>
        </div>
      </body>
    </html>
  );
}