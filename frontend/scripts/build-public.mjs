import { createHash } from 'node:crypto';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  pages,
  fontAssets,
  renderPage,
  render404,
  renderRobots,
  renderSitemap,
  renderDirectory,
} from '../public-site/site.mjs';

const dist = fileURLToPath(new URL('../dist/', import.meta.url));
function write(path, value) {
  const destination = join(dist, path);
  mkdirSync(dirname(destination), { recursive: true });
  writeFileSync(destination, value);
}
const app = readFileSync(join(dist, 'index.html'), 'utf8').replace(
  '<title>',
  '<meta name="robots" content="noindex,follow"><title>',
);
write('studio.html', app);
const manifest = JSON.parse(readFileSync(join(dist, '.vite/manifest.json'), 'utf8'));
const demoModuleUrl = '/' + manifest['public-site/demo.ts'].file;
for (const asset of fontAssets) write(asset.path.slice(1), asset.bytes);
for (const { language, key, path } of pages)
  write(path.slice(1) + 'index.html', renderPage(language, key, { demoModuleUrl }));
write('404.html', render404());
write('robots.txt', renderRobots());
write('sitemap.xml', renderSitemap());
write('llms.txt', renderDirectory());
write(
  'site.webmanifest',
  JSON.stringify({
    name: 'KuyLab',
    short_name: 'KuyLab',
    id: '/studio',
    start_url: '/studio',
    scope: '/',
    display: 'standalone',
    background_color: '#faf8f5',
    theme_color: '#ae784d',
    lang: 'uz',
    icons: [
      { src: '/brand/icon-192.png', sizes: '192x192', type: 'image/png' },
      { src: '/brand/icon-512.png', sizes: '512x512', type: 'image/png' },
    ],
  }),
);

// Keep offline app HTML separate from public pages. Never precache private API responses.
// Vite knows the original app assets; append the public HTML only after prerendering.
const oldPaths = JSON.parse(readFileSync(join(dist, 'offline-shell.json'), 'utf8'));
const shell = [
  ...new Set([
    ...oldPaths.filter((path) => path !== '/' && path !== '/index.html'),
    '/studio.html',
    '/',
    '/index.html',
    '/404.html',
    '/site.webmanifest',
    '/brand/icon-192.png',
    ...pages.map(({ path }) => path),
    ...fontAssets.map(({ path }) => path),
  ]),
].sort();
const revision = createHash('sha256');
for (const path of shell) {
  const file = join(dist, path.endsWith('/') ? path + 'index.html' : path);
  revision.update(path).update(readFileSync(file));
}
const digest = revision.digest('hex').slice(0, 16);
write('offline-shell.json', JSON.stringify(shell));
write(
  'sw.js',
  readFileSync(new URL('./studio-sw.js', import.meta.url), 'utf8').replace('__REVISION__', digest),
);
console.log(
  `Prerendered ${pages.length} public pages; app shell /studio.html; offline revision ${digest}.`,
);
