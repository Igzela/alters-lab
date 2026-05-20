import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/product': 'http://localhost:8000',
      '/provider-dialogue': 'http://localhost:8000',
      '/provider-gateway': 'http://localhost:8000',
      '/calibration-loop': 'http://localhost:8000',
      '/rubric-delta': 'http://localhost:8000',
      '/checkpoint-regeneration': 'http://localhost:8000',
      '/storage-boundary': 'http://localhost:8000',
      '/user-workflow': 'http://localhost:8000',
      '/phase5-closeout': 'http://localhost:8000',
    },
  },
})
