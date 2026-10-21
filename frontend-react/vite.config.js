import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// In dev, /api/* is proxied to the FastAPI backend.
// In Docker, nginx does the same job (see nginx.conf).
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 3000,
    proxy: {
      "/api": {
        target: process.env.API_TARGET || "http://localhost:8000",
        changeOrigin: true,
        rewrite: (p) => p.replace(/^\/api/, ""),
      },
    },
  },
});
