import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/board/',
  build: {
    outDir: 'dist',
    emptyDirBeforeWrite: true,
  },
  server: {
    port: 5173,
    proxy: {
      '/support/api': {
        target: 'http://localhost:7000',
        changeOrigin: true,
      },
    },
  },
})
