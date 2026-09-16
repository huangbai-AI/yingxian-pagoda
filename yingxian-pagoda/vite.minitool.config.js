import {defineConfig} from 'vite';
import {resolve} from 'path';

// Mini-tool build: classic IIFE script, relative paths, single bundle
export default defineConfig({
  base: './',
  publicDir: 'minitool-assets',
  build: {
    outDir: 'minitool-dist',
    assetsInlineLimit: 0,
    target: ['es2017', 'chrome61'],
    cssCodeSplit: false,
    rollupOptions: {
      input: resolve(__dirname, 'minitool/index.html'),
      output: {
        format: 'iife',
        inlineDynamicImports: true,
        entryFileNames: 'app.js',
        assetFileNames: (assetInfo) => {
          const name = assetInfo.name || '';
          if (name.endsWith('.css')) return '[name][extname]';
          return 'assets/[name][extname]';
        },
      },
    },
  },
});
