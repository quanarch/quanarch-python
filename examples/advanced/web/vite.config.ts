import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

const QUANAR = process.env.QUANAR_URL ?? 'http://localhost:3000';

// The client only knows the quanar, under /api. Its own pages keep every other path,
// even ones a quan also listens to, such as /orders.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5180,
    proxy: {
      '/api': { target: QUANAR, rewrite: (path) => path.replace(/^\/api/, '') },
    },
  },
});
