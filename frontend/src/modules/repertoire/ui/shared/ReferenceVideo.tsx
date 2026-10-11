import { useTranslation } from '@shared/i18n';
import { useState } from 'react';
import type { Arrangement } from '../../domain';

export default function ReferenceVideo({ arrangement }: { arrangement?: Arrangement }) {
  const tr = useTranslation();
  const [open, setOpen] = useState(false);
  if (!arrangement?.reference_video_url) return null;
  let id = '';
  try {
    const url = new URL(arrangement.reference_video_url);
    if (['www.youtube.com', 'youtube.com', 'youtu.be'].includes(url.hostname))
      id = url.hostname === 'youtu.be' ? url.pathname.slice(1) : url.searchParams.get('v') || '';
  } catch {
    return null;
  }
  if (!/^[a-zA-Z0-9_-]{11}$/.test(id)) return null;
  return (
    <details className="reference-video" onToggle={(event) => setOpen(event.currentTarget.open)}>
      <summary>{tr('Tanlangan aranjirovka ijrosini ko‘rish')}</summary>
      {open && (
        <iframe
          src={`https://www.youtube-nocookie.com/embed/${id}`}
          title={tr(`${arrangement.title} — ijro namunasi`)}
          loading="lazy"
          allow="encrypted-media; picture-in-picture"
          referrerPolicy="strict-origin-when-cross-origin"
          allowFullScreen
        />
      )}
      <p>
        {tr(
          'Avval tinglang. Qiyin joyni vaqt belgisi bilan qayd eting, so‘ng shu parchani sekin mashq qiling.',
        )}
      </p>
    </details>
  );
}
