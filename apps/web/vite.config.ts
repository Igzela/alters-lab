import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      // Proxy API requests to backend. Prefixes derived from OpenAPI routes.
      // Any path starting with a prefix below → forwarded to FastAPI.
      // Paths without a prefix (/, /src/*, /assets/*) stay with Vite.
      // To add a new prefix: just add one line below.
      '/action': 'http://localhost:18790',
      '/alter': 'http://localhost:18790',
      '/alters': 'http://localhost:18790',
      '/archive': 'http://localhost:18790',
      '/behavior': 'http://localhost:18790',
      '/branches': 'http://localhost:18790',
      '/calibration': 'http://localhost:18790',
      '/checkpoint': 'http://localhost:18790',
      '/cycle': 'http://localhost:18790',
      '/draft': 'http://localhost:18790',
      '/evidence': 'http://localhost:18790',
      '/generation': 'http://localhost:18790',
      '/health': 'http://localhost:18790',
      '/local-app': 'http://localhost:18790',
      '/obsidian': 'http://localhost:18790',
      '/p6': 'http://localhost:18790',
      '/pattern': 'http://localhost:18790',
      '/phase': 'http://localhost:18790',
      '/predictor': 'http://localhost:18790',
      '/product': 'http://localhost:18790',
      '/public': 'http://localhost:18790',
      '/promotion': 'http://localhost:18790',
      '/provider': 'http://localhost:18790',
      '/rubric': 'http://localhost:18790',
      '/runtime': 'http://localhost:18790',
      '/self': 'http://localhost:18790',
      '/snapshot': 'http://localhost:18790',
      '/storage': 'http://localhost:18790',
      '/user': 'http://localhost:18790',
      '/weekly': 'http://localhost:18790',
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    css: true,
  },
})
