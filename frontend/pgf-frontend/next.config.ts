import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  images: {
    remotePatterns: [
      { protocol: "http", hostname: "localhost", port: "4566", pathname: "/**" },
    ],
  },
  
};

export default nextConfig;


module.exports = {
  experimental: {
    serverActions: {
      allowedOrigins: ["http://localhost:3000", "http://127.0.0.1:3000"],
    },
    allowedDevOrigins: ["127.0.0.1", "localhost"],
  },
};
