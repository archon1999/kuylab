import {
  FavoriteBorderRounded,
  LibraryMusicOutlined,
  MusicNoteRounded,
  PianoOutlined,
  QueueMusicRounded,
  GraphicEqRounded,
  SearchRounded,
} from '@mui/icons-material';
import { Button } from '@mui/material';
import './emptyState.css';

const icons = {
  favorites: MusicNoteRounded,
  recent: QueueMusicRounded,
  search: LibraryMusicOutlined,
  library: LibraryMusicOutlined,
  lessons: PianoOutlined,
  activity: GraphicEqRounded,
};

export default function EmptyState({
  kind = 'library',
  title,
  description,
  action,
  compact = false,
}: {
  kind?: keyof typeof icons;
  title: string;
  description?: string;
  action?: { label: string; onClick: () => void };
  compact?: boolean;
}) {
  const Icon = icons[kind];
  return (
    <section className={`empty-state${compact ? ' empty-state-compact' : ''}`}>
      <div className="empty-state-icon" aria-hidden="true">
        <Icon />
        {kind === 'favorites' && <FavoriteBorderRounded className="empty-state-badge" />}
        {kind === 'search' && <SearchRounded className="empty-state-badge" />}
      </div>
      <h3>{title}</h3>
      {description && <p>{description}</p>}
      {action && <Button onClick={action.onClick}>{action.label}</Button>}
    </section>
  );
}
