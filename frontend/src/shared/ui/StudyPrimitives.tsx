import { useTranslation } from '@shared/i18n';
export function Keyboard({
  active = [],
  compact = false,
}: {
  active?: string[];
  compact?: boolean;
}) {
  const tr = useTranslation();
  const whites = ['C', 'D', 'E', 'F', 'G', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'A', 'B'];
  return (
    <div
      className={`keyboard ${compact ? 'compact' : ''}`}
      aria-label={tr('Ikki oktavali klavish sxemasi')}
    >
      {whites.map((note, i) => (
        <div
          key={i}
          className={`white-key ${active.includes(note) || active.includes(`${note}${4 + Math.floor(i / 7)}`) ? 'active' : ''}`}
        >
          <span>
            {note}
            {note === 'C' ? 4 + Math.floor(i / 7) : ''}
          </span>
          {!['E', 'B'].includes(note) && <div className="black-key" />}
        </div>
      ))}
    </div>
  );
}
export function SectionHeading({
  eyebrow,
  title,
  description,
  action,
}: {
  eyebrow?: string;
  title: string;
  description?: string;
  action?: React.ReactNode;
}) {
  const tr = useTranslation();
  return (
    <div className="section-heading">
      <div>
        {eyebrow && <div className="eyebrow">{tr(eyebrow)}</div>}
        <h1>{tr(title)}</h1>
        {description && <p>{tr(description)}</p>}
      </div>
      {action}
    </div>
  );
}
