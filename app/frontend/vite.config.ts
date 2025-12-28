import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: true, // needed for docker
    strictPort: true,
    port: 5173,
    allowedHosts: [
      'localhost',
      '127.0.0.1',
      'basmati.app',
      'www.basmati.app',
      '.basmati.app' // wildcard for subdomains
    ],
    watch: {
      usePolling: true // needed for some docker environments
    }
  }
})

