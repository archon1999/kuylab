import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync } from 'node:fs';

// Permit only the exact startup scripts emitted by this build. Do not weaken
// script-src with unsafe-inline: the theme/splash scripts run before React.
const html = readFileSync(new URL('../dist/index.html', import.meta.url), 'utf8');
const hashes = [...html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script\s*>/gi)]
  .filter(([, attributes, source]) => !/\bsrc\s*=/i.test(attributes) && source.trim())
  .map(([, , source]) => {
    const digest = createHash('sha256').update(source.replace(/\r\n?/g, '\n')).digest('base64');
    return `'sha256-${digest}'`;
  });
if (hashes.length !== 2) throw new Error('Review the CSP policy when startup scripts change.');
const template = readFileSync(new URL('../deploy/nginx.conf', import.meta.url), 'utf8');
if (!template.includes('__BOOT_CSP_HASHES__')) throw new Error('Missing CSP placeholder.');
writeFileSync(new URL('../nginx.conf', import.meta.url), template.replace('__BOOT_CSP_HASHES__', hashes.join(' ')));
