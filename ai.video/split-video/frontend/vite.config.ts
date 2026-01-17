import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3801,
    proxy: {
      '/api': {
        target: 'http://localhost:8801',
        changeOrigin: true,
      },
    },
  },
})
