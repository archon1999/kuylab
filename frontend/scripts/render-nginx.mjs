import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync } from 'node:fs';
import { parse } from 'parse5';

// Permit only the exact startup scripts emitted by this build. Do not weaken
// script-src with unsafe-inline: the theme/splash scripts run before React.
const html = readFileSync(new URL('../dist/index.html', import.meta.url), 'utf8');
const hashes = [];
function visit(node) {
  if (node.tagName === 'script' && !node.attrs.some((attribute) => attribute.name === 'src')) {
    const source = node.childNodes.map((child) => child.value || '').join('');
    if (source.trim()) hashes.push(`'sha256-${createHash('sha256').update(source).digest('base64')}'`);
  }
  for (const child of node.childNodes || []) visit(child);
  if (node.content) visit(node.content);
}
visit(parse(html));
if (hashes.length !== 2) throw new Error('Review the CSP policy when startup scripts change.');
const template = readFileSync(new URL('../deploy/nginx.conf', import.meta.url), 'utf8');
if (!template.includes('__BOOT_CSP_HASHES__')) throw new Error('Missing CSP placeholder.');
writeFileSync(new URL('../nginx.conf', import.meta.url), template.replace('__BOOT_CSP_HASHES__', hashes.join(' ')));
