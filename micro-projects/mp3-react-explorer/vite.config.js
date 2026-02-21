import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  // IMPORTANT: Must match the GitHub Pages subdirectory exactly.
  // Change to '/' for root-domain deploy.
  base: '/micro-projects/mp3-react-explorer/',
});
