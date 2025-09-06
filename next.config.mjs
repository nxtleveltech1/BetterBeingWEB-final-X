// Next.js Configuration for ES Modules

/** @type {import("next").NextConfig} */
const nextConfig = {
  images: {
    domains: ["localhost"],
  },
  typescript: {
    ignoreBuildErrors: false,
  },
  eslint: {
    ignoreDuringBuilds: false,
  },
  async rewrites() {
    const target = process.env.NEXT_PUBLIC_API_URL;
    // Proxy frontend /api/* -> backend API when env is set
    if (target) {
      return [
        {
          source: '/api/:path*',
          destination: `${target}/:path*`,
        },
      ];
    }
    return [];
  },
}

export default nextConfig
