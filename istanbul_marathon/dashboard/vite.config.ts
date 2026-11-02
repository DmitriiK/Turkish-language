import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: process.env.NODE_ENV === 'production' ? '/Turkish-language/marathon/' : '/',
  server: {
    port: 3001,
  },
  build: {
    outDir: 'dist',
  },
})
