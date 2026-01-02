import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/static/support_board/',
  build: {
    outDir: 'support_board/static/support_board',
    emptyDirBeforeWrite: true,
    manifest: true,
    rollupOptions: {
      input: 'src/main.jsx',
    },
  },
})
