// frontend-react/vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react' // Or @vitejs/plugin-react-swc if you chose SWC

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173, // Or your preferred port
    proxy: {
      // Proxy API requests to your FastAPI backend
      '/api': {
        target: 'http://localhost:8000', // Your FastAPI backend URL
        changeOrigin: true,
        // secure: false, // Uncomment if your backend is not HTTPS and you encounter issues
      },
    },
  },
})
