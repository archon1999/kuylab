import assert from 'node:assert/strict';
import test from 'node:test';
import { parse } from 'parse5';
import { content, languages, origin, paths } from '../public-site/content.mjs';
import { pages, renderPage, render404, renderRobots, renderSitemap, renderDirectory, isAppPath } from '../public-site/site.mjs';

function elements(node, tag) { return [...(node.tagName === tag ? [node] : []), ...(node.childNodes || []).flatMap(child => elements(child, tag))]; }
function attribute(node, name) { return node.attrs.find(item => item.name === name)?.value; }
function text(node) { return node.value || (node.childNodes || []).map(text).join(''); }

test('all localized public pages expose complete crawlable HTML and reciprocal canonical language links', () => {
  const titles = new Set();
  for (const { language, key, path } of pages) {
    const html = renderPage(language, key), document = parse(html);
    assert.equal(attribute(elements(document, 'html')[0], 'lang'), language);
    const title = text(elements(document, 'title')[0]);
    assert.ok(title.includes('KuyLab'));
    assert.ok(!titles.has(title), 'Each page needs a unique title');
    titles.add(title);
    assert.equal(elements(document, 'h1').length, 1);
    assert.equal(elements(document, 'main').length, 1);
    const links = elements(document, 'link');
    assert.equal(attribute(links.find(link => attribute(link, 'rel') === 'canonical'), 'href'), origin + path);
    for (const locale of [...languages, 'x-default']) {
      const alternate = links.find(link => attribute(link, 'hreflang') === locale);
      assert.equal(attribute(alternate, 'href'), origin + paths[key][locale === 'x-default' ? 'uz' : locale]);
    }
    const scripts = elements(document, 'script');
    assert.equal(scripts.some(script => attribute(script, 'src')), false, 'Public pages need no React download');
    assert.ok(!html.includes('/src/main.tsx') && !html.includes('boot-screen'));
    const graph = JSON.parse(text(scripts.find(script => attribute(script, 'type') === 'application/ld+json')))['@graph'];
    const webPage = graph.find(item => item['@id'] === origin + path + '#page');
    assert.equal(webPage.name, title);
    assert.equal(webPage.inLanguage, language);
    const description = elements(document, 'meta').find(meta => attribute(meta, 'name') === 'description');
    assert.equal(webPage.description, attribute(description, 'content'));
    if (!['home', 'privacy'].includes(key)) {
      assert.equal(webPage['@type'], 'LearningResource');
      assert.ok(content[language].guides[key].sections.length >= 6);
      for (const [, paragraph] of content[language].guides[key].sections) {
        assert.ok(text(elements(document, 'article')[0]).includes(paragraph));
      }
    }
    for (const link of elements(document, 'a')) {
      const href = attribute(link, 'href');
      if (href?.startsWith('/') && href !== '/licenses.html') {
        assert.ok(isAppPath(href) || pages.some(page => page.path === href.split('#')[0]), `Broken public link: ${href}`);
      }
    }
  }
  assert.equal(titles.size, 15);
});

test('crawler resources list only public canonical content and keep the studio out of the sitemap', () => {
  const sitemap = renderSitemap();
  assert.equal([...sitemap.matchAll(/<loc>/g)].length, 15);
  for (const { path } of pages) assert.ok(sitemap.includes(`<loc>${origin + path}</loc>`));
  assert.ok(!sitemap.includes('/studio') && !sitemap.includes('/api/') && !sitemap.includes('/practice'));
  const robots = renderRobots();
  assert.ok(robots.includes(`Sitemap: ${origin}/sitemap.xml`));
  assert.ok(robots.includes('Disallow: /api/'));
  assert.ok(!robots.includes('Disallow: /studio'), 'Crawlers must be able to see the studio noindex');
  assert.ok(renderDirectory().startsWith('# KuyLab\n'));
  const notFound = parse(render404());
  assert.ok(elements(notFound, 'meta').some(meta => attribute(meta, 'name') === 'robots' && attribute(meta, 'content').startsWith('noindex')));
  assert.equal(elements(notFound, 'header').length, 0);
});
