import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3802,
    proxy: {
      '/api': {
        target: 'http://localhost:8802',
        changeOrigin: true,
      },
      '/outputs': {
        target: 'http://localhost:8802',
        changeOrigin: true,
      },
      '/uploads': {
        target: 'http://localhost:8802',
        changeOrigin: true,
      },
    },
  },
})
