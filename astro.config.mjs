// @ts-check
import { defineConfig } from 'astro/config';

import db from '@astrojs/db';

import tailwindcss from '@tailwindcss/vite';

import react from '@astrojs/react';

// https://astro.build/config
export default defineConfig({
  integrations: [db(), react()],

  vite: {
    plugins: [tailwindcss()],
    server: {
      watch: {
        ignored: ['**/data/**', '**/backend/**', '**/.venv/**', '**/node_modules/**']
      }
    }
  }
});