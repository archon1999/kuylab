import { useTranslation } from '@shared/i18n';

export default function Fingering({ text }: { text: string }) {
  const tr = useTranslation();
  const parts = text.split(/(\b[1-5](?:[–−-][1-5])+\b)/);
  return (
    <aside className="studio-fingering" aria-label={tr('Barmoqlash')}>
      <h3>{tr('Barmoqlash')}</h3>
      <p>
        {parts.map((part, index) =>
          /^[1-5](?:[–−-][1-5])+$/.test(part) ? (
            <span className="studio-finger-sequence" aria-label={part} key={index}>
              <span aria-hidden="true">
                {part.split(/[–−-]/).map((finger, position) => (
                  <b key={position}>{finger}</b>
                ))}
              </span>
            </span>
          ) : (
            part
          ),
        )}
      </p>
    </aside>
  );
}
