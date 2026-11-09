import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// The dev server proxies /v1 to the FastAPI backend so the frontend never needs to know
// the API host, and so the app works unchanged behind a single origin in production.
export default defineConfig({
  plugins: [react()],
  server: {
    host: '127.0.0.1',
    port: 5173,
    proxy: {
      '/v1': {
        target: process.env.SHAIDA_API || 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
  },
})
