import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import publicSite from './public-site/vite.mjs';
const publicShell = [
  '/favicon.svg',
  '/licenses.html',
  '/audio/salamander/LICENSE.txt',
  '/audio/splendid/LICENSE.txt',
  '/audio/dattorro.worklet.js',
  '/fonts/licenses/alan-sans-OFL.txt',
  '/fonts/licenses/lora-OFL.txt',
  '/fonts/licenses/inter-OFL.txt',
];
export default defineConfig({
  plugins: [
    publicSite(),
    react(),
    {
      name: 'curated-studio-offline',
      configureServer(server) {
        server.middlewares.use((req, res, next) => {
          if (req.url === '/sw.js') {
            res.setHeader('Content-Type', 'application/javascript');
            res.setHeader('Cache-Control', 'no-cache');
            res.end(
              readFileSync(new URL('./scripts/studio-sw.js', import.meta.url), 'utf8').replace(
                '__REVISION__',
                'dev',
              ),
            );
          } else if (req.url === '/offline-shell.json') {
            res.setHeader('Content-Type', 'application/json');
            res.end(JSON.stringify(['/studio.html', ...publicShell]));
          } else next();
        });
      },
      generateBundle(_options, bundle) {
        const paths = [
          ...new Set([
            '/',
            '/index.html',
            ...publicShell,
            ...Object.keys(bundle).map((path) => '/' + path),
          ]),
        ];
        const revision = createHash('sha256')
          .update(JSON.stringify(paths))
          .digest('hex')
          .slice(0, 12);
        this.emitFile({
          type: 'asset',
          fileName: 'offline-shell.json',
          source: JSON.stringify(paths),
        });
        this.emitFile({
          type: 'asset',
          fileName: 'sw.js',
          source: readFileSync(new URL('./scripts/studio-sw.js', import.meta.url), 'utf8').replace(
            '__REVISION__',
            revision,
          ),
        });
      },
    },
  ],
  resolve: {
    alias: {
      '@app': decodeURIComponent(
        new URL('./src/app', import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1'),
      ),
      '@modules': decodeURIComponent(
        new URL('./src/modules', import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1'),
      ),
      '@shared': decodeURIComponent(
        new URL('./src/shared', import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1'),
      ),
    },
  },
  server: { port: 5173, proxy: { '/api': 'http://127.0.0.1:8000' } },
  preview: { port: 4173, proxy: { '/api': 'http://127.0.0.1:8000' } },
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          // Keep the stable React runtime cached independently from product changes.
          if (/\/node_modules\/(react|react-dom|scheduler)\//.test(id)) return 'react-vendor';
        },
      },
    },
  },
});
