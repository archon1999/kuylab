import {
  fontAssets,
  findPage,
  isAppPath,
  renderPage,
  render404,
  renderRobots,
  renderSitemap,
  renderDirectory,
} from './site.mjs';
import { readFileSync } from 'node:fs';

export default function publicSite() {
  return {
    name: 'kuylab-public-site',
    configurePreviewServer(server) {
      server.middlewares.use((req, res, next) => {
        const url = new URL(req.url || '/', 'http://localhost');
        if (url.pathname === '/' && url.searchParams.has('page')) {
          res.writeHead(302, { Location: '/studio' + url.search });
          return res.end();
        }
        if (isAppPath(url.pathname)) {
          res.setHeader('Content-Type', 'text/html; charset=utf-8');
          res.setHeader('X-Robots-Tag', 'noindex, follow');
          return res.end(readFileSync(new URL('../dist/studio.html', import.meta.url), 'utf8'));
        }
        if (findPage(url.pathname + '/')) {
          res.writeHead(308, { Location: url.pathname + '/' + url.search });
          return res.end();
        }
        if (
          !findPage(url.pathname) &&
          !url.pathname.includes('.') &&
          !url.pathname.startsWith('/api/')
        ) {
          res.statusCode = 404;
          res.setHeader('Content-Type', 'text/html; charset=utf-8');
          return res.end(render404());
        }
        next();
      });
    },
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        const url = new URL(req.url || '/', 'http://localhost');
        if (url.pathname === '/' && url.searchParams.has('page')) return next();
        const page = findPage(url.pathname);
        if (!page && findPage(url.pathname + '/')) {
          res.writeHead(308, { Location: url.pathname + '/' + url.search });
          return res.end();
        }
        const font = fontAssets.find(({ path }) => path === url.pathname);
        const robots = url.pathname === '/robots.txt';
        const sitemap = url.pathname === '/sitemap.xml';
        const directory = url.pathname === '/llms.txt';
        if (font || page || robots || sitemap || directory) {
          res.setHeader(
            'Content-Type',
            font
              ? 'font/woff2'
              : robots || directory
                ? 'text/plain; charset=utf-8'
                : sitemap
                  ? 'application/xml; charset=utf-8'
                  : 'text/html; charset=utf-8',
          );
          res.end(
            font
              ? font.bytes
              : page
                ? renderPage(page.language, page.key)
                : robots
                  ? renderRobots()
                  : sitemap
                    ? renderSitemap()
                    : renderDirectory(),
          );
        } else if (url.pathname === '/studio.html') {
          req.url = '/index.html';
          next();
        } else if (
          !isAppPath(url.pathname) &&
          !url.pathname.includes('.') &&
          !url.pathname.startsWith('/@') &&
          !url.pathname.startsWith('/src/') &&
          !url.pathname.startsWith('/api/')
        ) {
          res.statusCode = 404;
          res.setHeader('Content-Type', 'text/html; charset=utf-8');
          res.end(render404());
        } else next();
      });
    },
  };
}
