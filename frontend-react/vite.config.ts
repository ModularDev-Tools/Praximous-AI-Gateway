// frontend-react/vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173, // You can choose another port if you like
    proxy: {
      // Proxy API requests to your FastAPI backend
      '/api': {
        target: 'http://localhost:8000', // Your FastAPI backend URL
        changeOrigin: true,
        // secure: false, // Uncomment if your backend is not HTTPS
      },
    },
  },
})
