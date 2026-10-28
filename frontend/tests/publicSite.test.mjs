import assert from 'node:assert/strict';
import test from 'node:test';
import { runInNewContext } from 'node:vm';
import { parse } from 'parse5';
import { content, languages, origin, paths } from '../public-site/content.mjs';
import {
  pages,
  renderPage,
  render404,
  renderRobots,
  renderSitemap,
  renderDirectory,
  isAppPath,
} from '../public-site/site.mjs';
import { motionDuration, motionEasing } from '../src/shared/ui/motion.ts';
import { landingMotionScript } from '../public-site/motion.mjs';

test('landing motion can pause, stops in hidden tabs and reveals content without depending on React', () => {
  const root = { dataset: {} },
    preview = { dataset: {} },
    below = { dataset: {}, getBoundingClientRect: () => ({ top: 1500 }) };
  const listeners = {},
    attributes = {};
  const toggle = {
    dataset: { pauseLabel: 'Pause', resumeLabel: 'Resume' },
    setAttribute: (name, value) => (attributes[name] = value),
    addEventListener: (_event, callback) => (listeners.click = callback),
  };
  const document = {
    documentElement: root,
    hidden: false,
    querySelector: (selector) => (selector === '.preview' ? preview : toggle),
    querySelectorAll: (selector) => (selector.includes('pending') ? [below] : [below]),
    addEventListener: (name, callback) => (listeners[name] = callback),
  };
  let observer;
  class Observer {
    constructor(callback) {
      this.callback = callback;
      this.observed = [];
      observer = this;
    }
    observe(node) {
      this.observed.push(node);
    }
    unobserve(node) {
      this.observed = this.observed.filter((value) => value !== node);
    }
  }
  const media = {
    matches: false,
    addEventListener: (_event, callback) => (listeners.motion = callback),
  };
  runInNewContext(landingMotionScript, {
    document,
    matchMedia: () => media,
    window: { IntersectionObserver: Observer },
    IntersectionObserver: Observer,
    innerHeight: 800,
  });
  assert.equal(below.dataset.reveal, 'pending');
  listeners.click();
  assert.equal(root.dataset.landingPaused, 'true');
  assert.equal(attributes['aria-label'], 'Resume');
  observer.callback([{ isIntersecting: true, target: below }]);
  assert.equal(below.dataset.reveal, 'visible');
  document.hidden = true;
  listeners.visibilitychange();
  assert.equal(root.dataset.landingHidden, 'true');
  media.matches = true;
  listeners.motion();
  assert.equal(toggle.hidden, true);
  assert.equal(root.dataset.landingPaused, 'true');
});

test('reduced motion or missing observers cannot hide public content; removed hero copy stays absent in every language', () => {
  for (const reduced of [false, true]) {
    const root = { dataset: {} },
      node = { dataset: {} };
    const toggle = {
      dataset: { pauseLabel: 'Pause', resumeLabel: 'Resume' },
      setAttribute() {},
      addEventListener() {},
    };
    runInNewContext(landingMotionScript, {
      document: {
        documentElement: root,
        querySelector: () => toggle,
        querySelectorAll: () => [node],
        addEventListener() {},
      },
      matchMedia: () => ({ matches: reduced }),
      window: {},
    });
    assert.notEqual(node.dataset.reveal, 'pending');
    assert.equal(root.dataset.landingPaused, String(reduced));
  }
  for (const locale of languages) {
    const html = renderPage(locale, 'home');
    assert.equal(
      elements(parse(html), 'p').some((node) =>
        (attribute(node, 'class') || '').includes('hero-note'),
      ),
      false,
    );
    assert.ok(!text(elements(parse(html), 'main')[0]).includes('undefined'));
  }
});

test('public theme controls share studio motion timing and finish both switch directions', async () => {
  const html = parse(renderPage('uz', 'home'));
  const script = text(elements(html, 'script').find((node) => !attribute(node, 'type')));
  const root = { dataset: {}, style: { setProperty: (key, value) => properties.set(key, value) } };
  const properties = new Map(),
    storage = new Map();
  let ready, click;
  const transitions = [];
  const document = {
    documentElement: root,
    addEventListener: (_name, listener) => (ready = listener),
    querySelector: () => ({ addEventListener: (_name, listener) => (click = listener) }),
    startViewTransition(update) {
      update();
      let finish;
      const transition = {
        ready: Promise.resolve(),
        finished: new Promise((resolve) => (finish = resolve)),
        finish: () => finish(),
        skipTransition() {},
      };
      transitions.push(transition);
      return transition;
    },
  };
  runInNewContext(script, {
    document,
    localStorage: {
      getItem: (key) => storage.get(key),
      setItem: (key, value) => storage.set(key, value),
    },
    matchMedia: () => ({ matches: false }),
  });
  assert.equal(properties.get('--motion-duration'), `${motionDuration}ms`);
  assert.equal(properties.get('--motion-easing'), motionEasing);
  ready();
  click();
  assert.equal(root.dataset.mode, 'dark');
  transitions[0].finish();
  await new Promise((resolve) => setImmediate(resolve));
  assert.equal(root.dataset.themeTransition, undefined);
  click();
  assert.equal(root.dataset.mode, 'light');
  transitions[1].finish();
  await new Promise((resolve) => setImmediate(resolve));
  assert.equal(root.dataset.themeTransition, undefined);
  assert.equal(storage.get('guest:kuylab-theme'), 'light');
});

function elements(node, tag) {
  return [
    ...(node.tagName === tag ? [node] : []),
    ...(node.childNodes || []).flatMap((child) => elements(child, tag)),
  ];
}
function attribute(node, name) {
  return node.attrs.find((item) => item.name === name)?.value;
}
function text(node) {
  return node.value || (node.childNodes || []).map(text).join('');
}

test('all localized public pages expose complete crawlable HTML and reciprocal canonical language links', () => {
  const titles = new Set();
  for (const { language, key, path } of pages) {
    const html = renderPage(language, key),
      document = parse(html);
    assert.equal(attribute(elements(document, 'html')[0], 'lang'), language);
    const title = text(elements(document, 'title')[0]);
    assert.ok(title.includes('KuyLab'));
    assert.ok(!titles.has(title), 'Each page needs a unique title');
    titles.add(title);
    assert.equal(elements(document, 'h1').length, 1);
    assert.equal(elements(document, 'main').length, 1);
    const links = elements(document, 'link');
    assert.equal(
      attribute(
        links.find((link) => attribute(link, 'rel') === 'canonical'),
        'href',
      ),
      origin + path,
    );
    for (const locale of [...languages, 'x-default']) {
      const alternate = links.find((link) => attribute(link, 'hreflang') === locale);
      assert.equal(
        attribute(alternate, 'href'),
        origin + paths[key][locale === 'x-default' ? 'uz' : locale],
      );
    }
    const scripts = elements(document, 'script');
    assert.equal(
      scripts.some((script) => attribute(script, 'src')),
      false,
      'Public pages need no React download',
    );
    assert.ok(!html.includes('/src/main.tsx') && !html.includes('boot-screen'));
    const graph = JSON.parse(
      text(scripts.find((script) => attribute(script, 'type') === 'application/ld+json')),
    )['@graph'];
    const webPage = graph.find((item) => item['@id'] === origin + path + '#page');
    assert.equal(webPage.name, title);
    assert.equal(webPage.inLanguage, language);
    const description = elements(document, 'meta').find(
      (meta) => attribute(meta, 'name') === 'description',
    );
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
        assert.ok(
          isAppPath(href) || pages.some((page) => page.path === href.split('#')[0]),
          `Broken public link: ${href}`,
        );
      }
    }
  }
  assert.equal(titles.size, 15);
});

test('crawler resources list only public canonical content and keep the studio out of the sitemap', () => {
  const sitemap = renderSitemap();
  assert.equal([...sitemap.matchAll(/<loc>/g)].length, 15);
  for (const { path } of pages) assert.ok(sitemap.includes(`<loc>${origin + path}</loc>`));
  assert.ok(
    !sitemap.includes('/studio') && !sitemap.includes('/api/') && !sitemap.includes('/practice'),
  );
  const robots = renderRobots();
  assert.ok(robots.includes(`Sitemap: ${origin}/sitemap.xml`));
  assert.ok(robots.includes('Disallow: /api/'));
  assert.ok(
    !robots.includes('Disallow: /studio'),
    'Crawlers must be able to see the studio noindex',
  );
  assert.ok(renderDirectory().startsWith('# KuyLab\n'));
  const notFound = parse(render404());
  assert.ok(
    elements(notFound, 'meta').some(
      (meta) =>
        attribute(meta, 'name') === 'robots' && attribute(meta, 'content').startsWith('noindex'),
    ),
  );
  assert.equal(elements(notFound, 'header').length, 0);
});
