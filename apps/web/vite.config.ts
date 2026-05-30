import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/product': 'http://localhost:18790',
      '/local-app': 'http://localhost:18790',
      '/runtime-layout': 'http://localhost:18790',
      '/provider-config': 'http://localhost:18790',
      '/provider-dialogue': 'http://localhost:18790',
      '/provider-gateway': 'http://localhost:18790',
      '/obsidian-weekly-note': 'http://localhost:18790',
      '/weekly-review': 'http://localhost:18790',
      '/weekly-review-assistant': 'http://localhost:18790',
      '/action-alignment': 'http://localhost:18790',
      '/alter-dialogue': 'http://localhost:18790',
      '/calibration-loop': 'http://localhost:18790',
      '/rubric-delta': 'http://localhost:18790',
      '/checkpoint-regeneration': 'http://localhost:18790',
      '/pattern-review': 'http://localhost:18790',
      '/behavior-validation': 'http://localhost:18790',
      '/p6-data-retention': 'http://localhost:18790',
      '/storage-boundary': 'http://localhost:18790',
      '/user-workflow': 'http://localhost:18790',
      '/phase5-closeout': 'http://localhost:18790',
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    css: true,
  },
})
