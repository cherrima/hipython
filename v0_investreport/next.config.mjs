/** @type {import('next').NextConfig} */
const nextConfig = {
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },

  allowedDevOrigins: ['127.0.0.1', 'localhost'], // 동일 서버 간 통신 허용
}

export default nextConfig
