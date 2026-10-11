import { useRepertoire } from '@modules/repertoire';
import { ArrowForwardRounded, PianoRounded } from '@mui/icons-material';
import { Tab, Tabs } from '@mui/material';
import { useTranslation } from '@shared/i18n';
import { navigate } from '@shared/routing';
import { Keyboard, SectionHeading } from '@shared/ui/StudyPrimitives';
import { useState } from 'react';
const exercises = [
  {
    title: 'Ritm: teng puls',
    subtitle: 'Bitta nota, barqaror zarb',
    notes: 'C · C · C · C',
    text: 'Puls — musiqaning muntazam urishi. Ritm — notalarning shu puls bo‘ylab turli davomiylikda joylashishi. Metronom bilan C notasini har zarbda chaling. Keyin har zarbda ikkita teng nota chaling.',
    task: '60 BPM da 8 zarb. So‘ng “1-va, 2-va” sanab, har zarbga 2 nota.',
    highlight: ['C'],
    duration: '4 daqiqa',
  },
  {
    title: 'Interval: quloq va masofa',
    subtitle: 'Ikki nota orasidagi masofa',
    notes: 'C → D · C → E · C → G',
    text: 'Interval ikki tovush orasidagi masofadir. Eng kichik klavish qadami — yarim ton. C–D orasida 2 yarim ton, C–E orasida 4, C–G orasida 7 yarim ton bor. Shu masofani klavishda ko‘ring va eshiting.',
    task: 'C–D, C–E, C–G juftlarini navbat bilan chaling. Har birini ovoz chiqarib ayting.',
    highlight: ['C', 'D', 'E', 'G'],
    duration: '5 daqiqa',
  },
  {
    title: 'Akkord: uch tovushli tayanch',
    subtitle: 'Major va minor uchlik',
    notes: 'C–E–G · A–C–E',
    text: 'Uchlik akkord asosiy nota, tersiya va kvintadan tuziladi. C major: C–E–G (4 + 3 yarim ton). A minor: A–C–E (3 + 4 yarim ton). Har bir tovushni alohida, keyin uchalasini birga chaling.',
    task: 'C major va A minorni 4 zarbdan chaling. Tovush hissidagi farqni kuzating.',
    highlight: ['C', 'E', 'G', 'A'],
    duration: '5 daqiqa',
  },
];

export default function TheoryPage() {
  const tr = useTranslation();
  const [theoryTab, setTheoryTab] = useState(0);
  const { current } = useRepertoire();
  return (
    <>
      <SectionHeading eyebrow={tr('BILGANINGIZNI TUSHUNING')} title={tr('Nazariya')} />
      <Tabs
        value={theoryTab}
        onChange={(_, v) => setTheoryTab(v)}
        aria-label={tr('Nazariya mavzulari')}
        variant="scrollable"
        scrollButtons="auto"
        allowScrollButtonsMobile
        sx={{ mb: 3, borderBottom: '1px solid var(--ui-line)' }}
      >
        <Tab id="theory-tab-0" aria-controls="theory-panel-0" label={tr('01 · Ritm va puls')} />
        <Tab id="theory-tab-1" aria-controls="theory-panel-1" label={tr('02 · Intervallar')} />
        <Tab id="theory-tab-2" aria-controls="theory-panel-2" label={tr('03 · Akkordlar')} />
      </Tabs>
      <div
        className="theory-grid"
        role="tabpanel"
        id={`theory-panel-${theoryTab}`}
        aria-labelledby={`theory-tab-${theoryTab}`}
      >
        <article className="theory-card panel">
          <div className="theory-intro">
            <span className="pill">{tr('ASOSIY TUSHUNCHA')}</span>
            <h2>{tr(exercises[theoryTab].title)}</h2>
            <p>{tr(exercises[theoryTab].text)}</p>
          </div>
          <div className="theory-notation">{exercises[theoryTab].notes}</div>
          <Keyboard active={exercises[theoryTab].highlight} />
          <p className="keyboard-caption">
            {tr('Yorqin klavishlar — mashqdagi tovushlar. Bu ikki oktavali sxema.')}
          </p>
        </article>
        <aside>
          <div className="theory-exercise panel">
            <div className="insight-icon">
              <PianoRounded />
            </div>
            <span className="eyebrow">
              {tr('HOZIR SINAB KO‘RING · ')}
              {tr(exercises[theoryTab].duration)}
            </span>
            <h3>{tr(exercises[theoryTab].subtitle)}</h3>
            <p>{tr(exercises[theoryTab].task)}</p>
          </div>
          <div className="theory-connection panel">
            <span className="eyebrow">{tr('KOMPOZITSIYAGA BOG‘LASH')}</span>
            <h3>{tr(current.title)}</h3>
            <p>{tr('Tushunchalarni asarning o‘zidan olingan darslarda sinab ko‘ring.')}</p>
            <button className="text-link" onClick={() => navigate('detail')}>
              {tr('Kompozitsiya rejasi ')}
              <ArrowForwardRounded sx={{ fontSize: 17 }} />
            </button>
          </div>
        </aside>
      </div>
    </>
  );
}
