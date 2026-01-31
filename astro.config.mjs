// @ts-check
import { defineConfig } from 'astro/config';

import db from '@astrojs/db';

import tailwindcss from '@tailwindcss/vite';

// https://astro.build/config
export default defineConfig({
  integrations: [db()],

  vite: {
    plugins: [tailwindcss()],
    server: {
      watch: {
        ignored: ['**/data/**', '**/backend/**', '**/.venv/**', '**/node_modules/**']
      }
    }
  }
});