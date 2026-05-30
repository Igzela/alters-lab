import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/product': 'http://localhost:8000',
      '/local-app': 'http://localhost:8000',
      '/runtime-layout': 'http://localhost:8000',
      '/provider-config': 'http://localhost:8000',
      '/provider-dialogue': 'http://localhost:8000',
      '/provider-gateway': 'http://localhost:8000',
      '/obsidian-weekly-note': 'http://localhost:8000',
      '/weekly-review': 'http://localhost:8000',
      '/weekly-review-assistant': 'http://localhost:8000',
      '/action-alignment': 'http://localhost:8000',
      '/alter-dialogue': 'http://localhost:8000',
      '/calibration-loop': 'http://localhost:8000',
      '/rubric-delta': 'http://localhost:8000',
      '/checkpoint-regeneration': 'http://localhost:8000',
      '/pattern-review': 'http://localhost:8000',
      '/behavior-validation': 'http://localhost:8000',
      '/p6-data-retention': 'http://localhost:8000',
      '/storage-boundary': 'http://localhost:8000',
      '/user-workflow': 'http://localhost:8000',
      '/phase5-closeout': 'http://localhost:8000',
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    css: true,
  },
})
