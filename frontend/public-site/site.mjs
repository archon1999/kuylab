import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { content, languages, origin, paths, reviewed } from './content.mjs';
import { motionDuration, motionEasing } from '../src/shared/ui/motion.ts';
import { landingMotionScript } from './motion.mjs';

const escape = (value) =>
  String(value).replace(
    /[&<>"']/g,
    (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char],
  );
const json = (value) => JSON.stringify(value).replace(/</g, '\\u003c');
const arrow =
  '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path d="M4 12h15m-6-6 6 6-6 6" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>';
const themeScript = `(()=>{
const root=document.documentElement;
root.style.setProperty('--motion-duration',${JSON.stringify(motionDuration + 'ms')});
root.style.setProperty('--motion-easing',${JSON.stringify(motionEasing)});
try{root.dataset.mode=localStorage.getItem('guest:kuylab-theme')||localStorage.getItem('kuylab-theme')||(matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light')}catch{}
let mode=root.dataset.mode||'light',active,revision=0;
document.addEventListener('DOMContentLoaded',()=>{document.querySelector('[data-theme]')?.addEventListener('click',()=>{
mode=mode==='dark'?'light':'dark';const next=mode,ticket=++revision;active?.skipTransition();
const update=()=>{if(ticket!==revision)return;root.dataset.mode=next;try{localStorage.setItem('guest:kuylab-theme',next);localStorage.setItem('kuylab-theme',next)}catch{}};
if(!document.startViewTransition||matchMedia('(prefers-reduced-motion:reduce)').matches){active=undefined;delete root.dataset.themeTransition;update();return}
root.dataset.themeTransition='true';const transition=document.startViewTransition(update);active=transition;
transition.ready.catch(()=>{});transition.finished.catch(()=>{}).finally(()=>{if(active===transition){active=undefined;delete root.dataset.themeTransition}});
})});
})()`;
const cssSource =
  readFileSync(new URL('./style.css', import.meta.url), 'utf8') +
  readFileSync(new URL('../src/app/styles/motion.css', import.meta.url), 'utf8');
export const style = cssSource
  .replace(/\/\*[\s\S]*?\*\//g, '')
  .replace(/\s+/g, ' ')
  .replace(/\s*([{}:;,])\s*/g, '$1')
  .trim();
export const fontAssets = [
  ['alan', '@fontsource-variable/alan-sans/files/alan-sans-latin-wght-normal.woff2'],
  ['lora', '@fontsource-variable/lora/files/lora-latin-wght-normal.woff2'],
  ['cyrillic', '@fontsource-variable/inter/files/inter-cyrillic-wght-normal.woff2'],
  ['lora-cyrillic', '@fontsource-variable/lora/files/lora-cyrillic-wght-normal.woff2'],
].map(([name, file]) => {
  const bytes = readFileSync(new URL('../node_modules/' + file, import.meta.url));
  const hash = createHash('sha256').update(bytes).digest('hex').slice(0, 12);
  return { name, bytes, path: `/assets/public-${name}-${hash}.woff2` };
});
const font = (name) => fontAssets.find((item) => item.name === name).path;
const fontCss = `@font-face{font-family:Alan;src:url('${font('alan')}') format('woff2');font-style:normal;font-weight:300 900;font-display:optional}@font-face{font-family:Lora;src:url('${font('lora')}') format('woff2');font-style:normal;font-weight:400 700;font-display:optional}@font-face{font-family:InterCyr;src:url('${font('cyrillic')}') format('woff2');font-style:normal;font-weight:100 900;font-display:optional;unicode-range:U+0400-045F,U+0490-0491,U+04B0-04B1,U+2116}@font-face{font-family:Lora;src:url('${font('lora-cyrillic')}') format('woff2');font-style:normal;font-weight:400 700;font-display:optional;unicode-range:U+0400-045F,U+0490-0491,U+04B0-04B1,U+2116}`;

export const pages = languages.flatMap((language) =>
  Object.keys(paths).map((key) => ({ language, key, path: paths[key][language] })),
);
export function findPage(pathname) {
  return pages.find((page) => page.path === pathname);
}
export function isAppPath(pathname) {
  return /^\/(studio(?:\.html)?|compositions|practice|lessons|study|exercises|theory|statistics|settings|404)(\/|$)/.test(
    pathname,
  );
}

function brand(language) {
  return `<a class="brand" href="${paths.home[language]}" aria-label="KuyLab — ${escape(content[language].home)}"><img src="/favicon.svg" width="44" height="44" alt="" fetchpriority="low"><span>KuyLab</span></a>`;
}
function header(language, key) {
  const t = content[language];
  return `<a class="skip" href="#main">${t.skip}</a><header class="header wrap">${brand(language)}<nav class="main-nav" aria-label="${escape(t.guidesLabel)}"><a href="${paths.home[language]}#method">${t.methodLabel}</a><a href="${paths.home[language]}#guides">${t.guidesLabel}</a></nav><div class="header-actions"><nav class="languages" aria-label="${language === 'uz' ? 'Til' : language === 'ru' ? 'Язык' : 'Language'}">${languages.map((locale) => `<a href="${paths[key][locale]}" lang="${locale}" hreflang="${locale}"${locale === language ? ' aria-current="page"' : ''}>${locale.toUpperCase()}</a>`).join('')}</nav><button class="theme" type="button" data-theme aria-label="${t.theme}"><svg class="moon" viewBox="0 0 24 24" width="21" height="21" aria-hidden="true"><path d="M20 15.3A8.4 8.4 0 0 1 8.7 4a8.4 8.4 0 1 0 11.3 11.3Z" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/></svg><svg class="sun" viewBox="0 0 24 24" width="21" height="21" aria-hidden="true"><circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" stroke-width="1.7"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1.4 1.4m11.2 11.2L19 19M5 19l1.4-1.4M17.6 6.4 19 5" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></svg></button><a class="header-login" href="/studio">${t.login}${arrow}</a></div></header>`;
}
function preview(t) {
  const whiteKeys = Array.from(
    { length: 21 },
    (_, i) => `<rect x="${i * 24}" y="236" width="23" height="82" rx="2" fill="#eeece8"/>`,
  ).join('');
  const blackKeys = Array.from({ length: 20 }, (_, i) =>
    [0, 1, 3, 4, 5].includes(i % 7)
      ? `<rect x="${i * 24 + 17}" y="236" width="13" height="51" rx="2" fill="#171323"/>`
      : '',
  ).join('');
  const notes = [
    [72, 100, 130, 'E', 'l'],
    [144, 35, 80, 'A', 'l'],
    [216, 150, 70, 'C', 'l'],
    [288, 180, 57, 'C', 'r'],
    [312, 110, 58, 'D', 'r'],
    [336, 38, 58, 'E', 'r'],
    [384, -25, 45, 'G', 'r'],
  ];
  return `<figure class="preview" data-reveal><div class="preview-heading"><span><i class="preview-status" aria-hidden="true"></i>${escape(t.preview)}</span><button class="preview-motion" type="button" data-preview-motion data-pause-label="${escape(t.pauseMotion)}" data-resume-label="${escape(t.resumeMotion)}" aria-label="${escape(t.pauseMotion)}" aria-pressed="false"><svg class="motion-pause" viewBox="0 0 20 20" width="16" height="16" aria-hidden="true"><path d="M7 5v10m6-10v10" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/></svg><svg class="motion-play" viewBox="0 0 20 20" width="16" height="16" aria-hidden="true"><path d="m7 4 9 6-9 6Z" fill="currentColor"/></svg></button></div><svg viewBox="0 0 504 318" role="img" aria-label="${escape(t.previewAlt)}"><defs><linearGradient id="left" x2="0" y2="1"><stop stop-color="#f3a6d1"/><stop offset="1" stop-color="#bd77a5"/></linearGradient><linearGradient id="right" x2="0" y2="1"><stop stop-color="#a1e8f6"/><stop offset="1" stop-color="#7db7df"/></linearGradient><clipPath id="demo-roll"><rect width="504" height="235"/></clipPath></defs><path d="M72 0v236M144 0v236M216 0v236M288 0v236M360 0v236M432 0v236" stroke="#ffffff" opacity=".045"/><g clip-path="url(#demo-roll)">${notes.map(([x, y, h, name, hand], index) => `<g class="demo-note" style="--note-delay:-${index * 0.78}s"><rect x="${x}" y="${y}" width="21" height="${h}" rx="10" fill="url(#${hand === 'l' ? 'left' : 'right'})"/><text x="${x + 10.5}" y="${y + h - 10}" text-anchor="middle" font-size="12" font-weight="700" fill="#211932">${name}</text></g>`).join('')}</g><path d="M0 235h504" stroke="#b98966" stroke-width="2"/>${whiteKeys}${blackKeys}<rect class="demo-key" x="288" y="236" width="23" height="82" rx="2" fill="#8cc9e7" opacity=".8"/></svg><figcaption><span><i class="preview-piece-icon" aria-hidden="true">♪</i>${escape(t.piece)}</span><span>${escape(t.pieceMeta)}</span></figcaption></figure>`;
}
function cards(language, exclude) {
  const t = content[language];
  return `<div class="guide-grid">${['piano', 'theory', 'exercises']
    .filter((key) => key !== exclude)
    .map(
      (key, i) =>
        `<a class="guide" href="${paths[key][language]}"><span class="guide-number" aria-hidden="true">0${i + 1}</span><h3>${escape(t.guides[key].title)}</h3><p>${escape(t.guides[key].description)}</p><span class="read">${t.read}${arrow}</span></a>`,
    )
    .join('')}</div>`;
}
function homeContent(language) {
  const t = content[language];
  return `<main id="main" class="landing"><section class="hero wrap"><div class="hero-aura" aria-hidden="true"></div><svg class="hero-score" viewBox="0 0 1200 340" fill="none" aria-hidden="true"><g stroke="currentColor">${[0, 16, 32, 48, 64].map((y) => `<path d="M-80 ${190 + y}C240 ${30 + y} 340 ${310 + y} 700 ${160 + y}S1080 ${100 + y} 1280 ${-20 + y}"/>`).join('')}</g><g fill="currentColor"><ellipse cx="240" cy="196" rx="13" ry="8" transform="rotate(-20 240 196)"/><path d="M251 194v-68l44-12v65h-3v-51l-37 10v56Z"/><ellipse cx="282" cy="181" rx="13" ry="8" transform="rotate(-20 282 181)"/><ellipse cx="987" cy="125" rx="13" ry="8" transform="rotate(-20 987 125)"/><path d="M998 124V58h3v67Z"/></g></svg><div class="hero-copy"><h1>${escape(t.headline)}</h1><p class="lead">${escape(t.intro)}</p><div class="hero-actions"><a class="button" href="/studio">${t.open}${arrow}</a><a class="hero-method" href="#method">${t.methodLabel}<span aria-hidden="true">↓</span></a></div></div>${preview(t)}</section><section class="section wrap method" id="method"><h2 data-reveal>${escape(t.methodTitle)}</h2><div class="feature-grid">${t.features.map(([title, text], i) => `<div class="feature-card" data-reveal><span class="step" aria-hidden="true">${String(i + 1).padStart(2, '0')}</span><h3>${escape(title)}</h3><p>${escape(text)}</p></div>`).join('')}</div></section><section class="section guides-section" id="guides"><div class="wrap"><h2 data-reveal>${escape(t.guidesTitle)}</h2><p class="section-intro">${escape(t.guidesIntro)}</p><div data-reveal>${cards(language)}</div></div></section><section class="section wrap faq" data-reveal><div><h2>${t.faqTitle}</h2><p class="muted">${escape(t.about)}</p></div><div>${t.faqs.map(([question, answer]) => `<details><summary>${escape(question)}<span aria-hidden="true">+</span></summary><p>${escape(answer)}</p></details>`).join('')}</div></section><section class="closing wrap" data-reveal><h2>${escape(t.cta)}</h2><a class="button" href="/studio">${t.open}${arrow}</a></section></main>`;
}
function home(language) {
  return homeContent(language) + `<script>${landingMotionScript}</script>`;
}
function article(language, key) {
  const t = content[language];
  const guide = t.guides[key];
  return `<main id="main" class="article wrap"><nav class="breadcrumb" aria-label="${escape(t.home)}"><a href="${paths.home[language]}">${t.home}</a><span aria-hidden="true">/</span><span>${key === 'privacy' ? t.privacyLabel : t.guidesLabel}</span></nav><article><header class="article-heading"><h1>${escape(guide.title)}</h1><p class="lead">${escape(guide.intro)}</p><p class="small muted">${t.updated}: <time datetime="${reviewed}">${reviewed.split('-').reverse().join('.')}</time> · KuyLab</p></header><div class="article-body">${guide.sections.map(([title, paragraph]) => `<section><h2>${escape(title)}</h2><p>${escape(paragraph)}</p></section>`).join('')}${guide.exercise ? `<aside class="exercise"><h2>${escape(guide.exercise[0])}</h2><p>${escape(guide.exercise[1])}</p><a class="text-link" href="/studio">${t.open}${arrow}</a></aside>` : `<p><a class="text-link" href="https://github.com/archon1999/kuylab/issues">GitHub · ${t.sourceLabel}${arrow}</a></p>`}</div></article>${key !== 'privacy' ? `<section class="related"><h2>${t.guidesLabel}</h2>${cards(language, key)}</section>` : ''}</main>`;
}
function footer(language) {
  const t = content[language];
  return `<footer class="footer wrap"><span>© ${reviewed.slice(0, 4)} KuyLab</span><nav aria-label="KuyLab"><a href="${paths.privacy[language]}">${t.privacyLabel}</a><a href="/licenses.html">${t.licensesLabel}</a><a href="https://github.com/archon1999/kuylab">${t.sourceLabel}</a></nav></footer>`;
}
export function renderPage(language, key) {
  const t = content[language];
  const isHome = key === 'home';
  const title = isHome ? t.title : t.guides[key].title + ' — KuyLab';
  const description = isHome ? t.description : t.guides[key].description;
  const url = origin + paths[key][language];
  const website = {
    '@type': 'WebSite',
    '@id': origin + '/#website',
    name: 'KuyLab',
    url: origin + '/',
    inLanguage: languages,
    publisher: { '@id': origin + '/#organization' },
  };
  const page = {
    '@type': isHome || key === 'privacy' ? 'WebPage' : 'LearningResource',
    '@id': url + '#page',
    url,
    name: title,
    description,
    inLanguage: language,
    isPartOf: { '@id': origin + '/#website' },
    dateModified: reviewed,
    publisher: { '@id': origin + '/#organization' },
    ...(isHome || key === 'privacy'
      ? {}
      : {
          learningResourceType: 'Guide',
          educationalUse: 'Self-study',
          author: { '@id': origin + '/#organization' },
          isAccessibleForFree: true,
        }),
  };
  const graph = [
    {
      '@type': 'Organization',
      '@id': origin + '/#organization',
      name: 'KuyLab',
      url: origin + '/',
      logo: {
        '@type': 'ImageObject',
        url: origin + '/brand/icon-512.png',
        width: 512,
        height: 512,
      },
      sameAs: ['https://github.com/archon1999/kuylab'],
    },
    website,
    page,
  ];
  if (!isHome)
    graph.push({
      '@type': 'BreadcrumbList',
      itemListElement: [
        { '@type': 'ListItem', position: 1, name: t.home, item: origin + paths.home[language] },
        { '@type': 'ListItem', position: 2, name: t.guides[key].title, item: url },
      ],
    });
  const preloads = (language === 'ru' ? ['cyrillic', 'lora-cyrillic'] : ['alan', 'lora'])
    .map(
      (name) => `<link rel="preload" href="${font(name)}" as="font" type="font/woff2" crossorigin>`,
    )
    .join('');
  return `<!doctype html><html lang="${language}"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${escape(title)}</title><meta name="description" content="${escape(description)}"><meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1"><link rel="canonical" href="${url}">${languages.map((locale) => `<link rel="alternate" hreflang="${locale}" href="${origin + paths[key][locale]}">`).join('')}<link rel="alternate" hreflang="x-default" href="${origin + paths[key].uz}"><meta property="og:type" content="${isHome ? 'website' : 'article'}"><meta property="og:site_name" content="KuyLab"><meta property="og:title" content="${escape(title)}"><meta property="og:description" content="${escape(description)}"><meta property="og:url" content="${url}"><meta property="og:locale" content="${{ uz: 'uz_UZ', ru: 'ru_RU', en: 'en_US' }[language]}"><meta property="og:image" content="${origin}/brand/kuylab-social.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="KuyLab — Piano, practice, theory"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="${escape(title)}"><meta name="twitter:description" content="${escape(description)}"><meta name="twitter:image" content="${origin}/brand/kuylab-social.png"><meta name="theme-color" content="#faf8f5"><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="icon" href="/favicon.ico" sizes="any"><link rel="apple-touch-icon" href="/brand/apple-touch-icon.png"><link rel="manifest" href="/site.webmanifest">${preloads}<style>${fontCss}${style}</style><script>${themeScript}</script><script type="application/ld+json">${json({ '@context': 'https://schema.org', '@graph': graph })}</script></head><body>${header(language, key)}${isHome ? home(language) : article(language, key)}${footer(language)}</body></html>`;
}
export function render404() {
  return `<!doctype html><html lang="uz"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,follow"><title>Sahifa topilmadi — KuyLab</title><link rel="icon" href="/favicon.svg"><style>${fontCss}${style}</style><script>${themeScript}</script></head><body><main class="not-found" id="main">${brand('uz')}<span class="muted">404</span><h1>Sahifa topilmadi</h1><p class="muted">Bu manzil o‘zgargan yoki mavjud emas.</p><a class="button" href="/">Bosh sahifa${arrow}</a></main></body></html>`;
}
export function renderRobots() {
  return `User-agent: *\nAllow: /\nDisallow: /api/\nDisallow: /admin/\nDisallow: /media/\nDisallow: /audio/\n\nSitemap: ${origin}/sitemap.xml\n`;
}
export function renderSitemap() {
  return `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">${pages.map(({ language, key, path }) => `<url><loc>${origin + path}</loc><lastmod>${reviewed}</lastmod>${languages.map((locale) => `<xhtml:link rel="alternate" hreflang="${locale}" href="${origin + paths[key][locale]}"/>`).join('')}<xhtml:link rel="alternate" hreflang="x-default" href="${origin + paths[key].uz}"/></url>`).join('')}</urlset>\n`;
}
export function renderDirectory() {
  return `# KuyLab\n\n> KuyLab is an online piano-learning studio with a falling-note MIDI player, composition lessons, independent exercises and practical music theory. Available in Uzbek, Russian and English.\n\n## Public guides\n\n${pages
    .filter(({ key }) => key !== 'privacy')
    .map(
      ({ language, key, path }) =>
        `- [${key === 'home' ? content[language].title : content[language].guides[key].title}](${origin + path}): ${key === 'home' ? content[language].description : content[language].guides[key].description}`,
    )
    .join(
      '\n',
    )}\n\n## About and privacy\n\n- [Privacy](${origin + paths.privacy.en}): account data, cookies and offline storage.\n- [Source code](https://github.com/archon1999/kuylab): implementation and issue tracker.\n- [Licenses](${origin}/licenses.html): software, fonts and piano samples.\n\nThe studio at /studio requires an account. Private account and learning data are not public resources. This directory describes available content; it does not grant rights to third-party compositions or recordings.\n`;
}
