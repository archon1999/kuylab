import { landingContent, repertoire } from './landing-content.mjs';
import { demoNotes } from './demo-score.mjs';
import { pianoKeyLayout } from '../src/modules/practice/domain/studioTransport.ts';
import { paths } from './content.mjs';
import { demoBootstrapScript, landingMotionScript } from './motion.mjs';

const escape = (value) =>
  String(value).replace(
    /[&<>"']/g,
    (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char],
  );
const icon = (path, extra = '') =>
  `<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" ${extra}>${path}</svg>`;
const arrow = icon('<path d="M4 12h16m-6-6 6 6-6 6"/>');
const play = icon('<path d="m9 5 11 7-11 7Z" fill="currentColor" stroke="none"/>');
const note = icon(
  '<path d="M10 18V5l10-2v13M10 9l10-2"/><ellipse cx="6.5" cy="18.5" rx="3.5" ry="2.5"/><ellipse cx="16.5" cy="16.5" rx="3.5" ry="2.5"/>',
);

function scorePoster(label) {
  const keys = pianoKeyLayout(1000, 36, 84);
  const byPitch = new Map(keys.map((key) => [key.pitch, key]));
  return `<svg class="demo-poster" viewBox="0 0 1000 330" preserveAspectRatio="none" role="img" aria-label="${escape(label)}"><defs><linearGradient id="demo-left" x2="0" y2="1"><stop stop-color="#f4add1"/><stop offset="1" stop-color="#c978a1"/></linearGradient><linearGradient id="demo-right" x2="0" y2="1"><stop stop-color="#a1e9f5"/><stop offset="1" stop-color="#78b7de"/></linearGradient><clipPath id="poster-roll"><path d="M0 0h1000v254H0Z"/></clipPath></defs><path fill="#241c37" d="M0 0h1000v330H0Z"/>${keys
    .filter((key) => key.white)
    .map((key) => `<path d="M${key.x} 0v254" stroke="#ffffff" opacity=".04"/>`)
    .join('')}<g clip-path="url(#poster-roll)">${demoNotes
    .filter(([, onset]) => onset < 5)
    .map(([pitch, onset, duration, , hand]) => {
      const key = byPitch.get(pitch);
      const h = Math.max(6, duration * 50.8);
      return `<rect x="${key.x + 2}" y="${254 - onset * 50.8 - h}" width="${key.width - 4}" height="${h}" rx="${Math.min(10, (key.width - 4) / 2)}" fill="url(#demo-${hand ? 'right' : 'left'})"/>`;
    })
    .join('')}</g>${[true, false]
    .map((white) =>
      keys
        .filter((key) => key.white === white)
        .map(
          (key) =>
            `<rect x="${key.x + 0.5}" y="254" width="${key.width - 1}" height="${white ? 75 : 48}" rx="2" fill="${white ? '#f5f1ec' : '#15101f'}"/>`,
        )
        .join(''),
    )
    .join('')}<path d="M0 254h1000" stroke="#dba57e"/></svg>`;
}

function demo(t, l) {
  return `<figure class="landing-demo" id="listen" data-demo data-state="idle" data-play="${escape(l.play)}" data-pause="${escape(l.pause)}" data-completed="${escape(l.completed)}" data-mute="${escape(l.mute)}" data-unmute="${escape(l.unmute)}" aria-label="${escape(l.demo)}">
    <div class="demo-heading"><div class="demo-title">${note}<span><strong>Still</strong><small>Winter Sonata</small></span></div><span class="demo-sample">${escape(l.sample)}</span><button class="demo-icon demo-control" type="button" data-demo-toggle aria-label="${escape(l.play)}"><span class="icon-play">${play}</span><span class="icon-pause">${icon('<path d="M9 5v14M16 5v14"/>')}</span></button></div>
    <div class="demo-stage">${scorePoster(t.previewAlt)}<canvas aria-hidden="true"></canvas><div class="demo-overlay"><button class="demo-start demo-control" type="button" data-demo-start aria-label="${escape(l.play)}"><span class="demo-start-circle">${play}${icon('<path d="M18 7a8 8 0 1 0 2 5M18 3v4h-4"/>', 'class="icon-replay"')}</span><span class="demo-start-label">${escape(l.demo)}</span></button><span class="demo-loading" role="status">${escape(l.loading)}</span><p class="demo-error" data-demo-error role="alert" hidden>${escape(l.error)}</p></div></div>
    <div class="demo-progress" aria-hidden="true"><span data-demo-progress></span></div><figcaption class="demo-footer"><span class="demo-hands"><span><i></i>${escape(l.left)}</span><span><i></i>${escape(l.right)}</span></span><div class="demo-speeds demo-control" role="group" aria-label="${escape(l.speed)}">${[0.5, 0.75, 1].map((speed) => `<button type="button" data-demo-speed="${speed}" aria-pressed="${speed === 1}" aria-label="${escape(l.speed)} ${speed * 100}%">${speed}×</button>`).join('')}</div><span class="demo-clock" aria-hidden="true"><span data-demo-clock>0:00</span><span> / 0:16</span></span><button class="demo-icon demo-mute demo-control" type="button" data-demo-mute aria-label="${escape(l.mute)}" aria-pressed="false">${icon('<path d="m11 5-6 4H2v6h3l6 4ZM15 8a6 6 0 0 1 0 8M18 5a10 10 0 0 1 0 14"/>')}<span class="mute-line"></span></button></figcaption>
  </figure>`;
}

function midiIllustration() {
  const keys = pianoKeyLayout(360, 60, 84);
  return `<div class="midi-art" aria-hidden="true"><div class="midi-signal"><span>USB MIDI</span><span class="midi-signal-dots"><i></i><i></i><i></i><i></i><i></i></span>${icon('<rect x="4" y="3" width="16" height="12" rx="2"/><path d="M8 21h8m-4-6v6"/>')}</div><div class="midi-chord"><span>C</span><span>E</span><span>G</span></div><svg viewBox="0 0 360 120">${[
    true,
    false,
  ]
    .map((white) =>
      keys
        .filter((key) => key.white === white)
        .map(
          (key) =>
            `<rect x="${key.x + 0.6}" y="0" width="${key.width - 1.2}" height="${white ? 119 : 74}" rx="3" fill="${[60, 64, 67].includes(key.pitch) ? '#dba57e' : white ? '#f5f1ec' : '#21192e'}"/>`,
        )
        .join(''),
    )
    .join('')}</svg></div>`;
}

export function renderLanding(language, t, demoModuleUrl) {
  const l = landingContent[language];
  const featureIcons = [
    icon('<path d="m9 5 11 7-11 7Z"/>'),
    icon('<path d="M12 5C8 2 4 3 2 4v15c3-2 6-2 10 0 4-2 7-2 10 0V4c-3-1-6-2-10 1Zm0 0v14"/>'),
    icon(
      '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M7 3v11h3V3m4 0v11h3V3M9 14v7m6-7v7"/>',
    ),
  ];
  return `<main id="main" class="landing">
    <section class="landing-hero wrap"><div class="hero-lines" aria-hidden="true">${[0, 1, 2, 3, 4].map((index) => `<i style="--line-index:${index}"></i>`).join('')}</div><div class="landing-hero-copy"><h1>${escape(l.first)}<em>${escape(l.accent)}</em></h1><p class="lead">${escape(l.intro)}</p><div class="landing-hero-actions"><a class="button" href="/studio">${escape(t.open)}${arrow}</a><a class="text-link" href="#listen" data-demo-trigger>${play}${escape(l.try)}</a></div></div>${demo(t, l)}<div class="landing-facts">${[103, 198, 48, 24].map((count, index) => `<div><strong>${count}</strong><span>${escape(l.facts[index])}</span></div>`).join('')}</div></section>
    <section class="section wrap repertoire" id="repertoire"><div class="landing-section-head" data-reveal><div><span class="eyebrow">${escape(l.repertoireLabel)}</span><h2>${escape(l.repertoireTitle)}</h2><p class="section-intro">${escape(l.repertoireIntro)}</p></div><a class="text-link" href="/compositions">${escape(l.allPieces)}${arrow}</a></div><div class="repertoire-grid">${repertoire.map((piece, index) => `<a class="repertoire-piece" href="/compositions/${piece.slug}" data-reveal><span class="piece-symbol piece-symbol-${piece.tag}" aria-hidden="true">${note}</span><span class="piece-copy"><small>${escape(l.tags[piece.tag])}</small><h3>${escape(piece.title)}</h3><span>${escape(piece.artist)}</span></span>${arrow}<span class="piece-index" aria-hidden="true">${String(index + 1).padStart(2, '0')}</span></a>`).join('')}</div></section>
    <section class="section wrap method" id="method"><div class="landing-section-head" data-reveal><div><span class="eyebrow">${escape(l.methodLabel)}</span><h2>${escape(t.methodTitle)}</h2></div></div><div class="feature-grid">${t.features.map(([title, description], index) => `<div class="feature-card" data-reveal><div class="feature-top">${featureIcons[index]}<span class="step">0${index + 1}</span></div><h3>${escape(title)}</h3><p>${escape(description)}</p></div>`).join('')}</div></section>
    <section class="section wrap midi-section"><div class="midi-panel" data-reveal><div><span class="eyebrow">${escape(l.midiLabel)}</span><h2>${escape(l.midiTitle)}</h2><p>${escape(l.midiText)}</p><p class="midi-detail">${escape(l.midiDetail)}</p><a class="text-link" href="/piano">${escape(l.midiAction)}${arrow}</a></div>${midiIllustration()}</div></section>
    <section class="section guides-section" id="guides"><div class="wrap"><span class="eyebrow">${escape(l.guidesLabel)}</span><h2 data-reveal>${escape(t.guidesTitle)}</h2><p class="section-intro">${escape(t.guidesIntro)}</p><div class="guide-grid">${['piano', 'theory', 'exercises'].map((key, index) => `<a class="guide" href="${paths[key][language]}" data-reveal><span class="guide-number" aria-hidden="true">0${index + 1}</span><h3>${escape(t.guides[key].title)}</h3><p>${escape(t.guides[key].description)}</p><span class="read">${escape(t.read)}${arrow}</span></a>`).join('')}</div></div></section>
    <section class="section wrap faq"><div data-reveal><h2>${escape(t.faqTitle)}</h2><p class="muted">${escape(t.about)}</p></div><div data-reveal>${t.faqs.map(([question, answer]) => `<details><summary>${escape(question)}<span aria-hidden="true">+</span></summary><p>${escape(answer)}</p></details>`).join('')}</div></section>
    <section class="closing wrap" data-reveal><div><h2>${escape(t.cta)}</h2><p>${escape(l.closingText)}</p></div><a class="button" href="/studio">${escape(t.open)}${arrow}</a></section>
  </main><script>${landingMotionScript}</script><script type="module">${demoBootstrapScript(demoModuleUrl)}</script>`;
}
