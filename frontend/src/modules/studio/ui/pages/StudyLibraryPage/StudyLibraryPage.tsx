import EmptyState from '@shared/ui/EmptyState';
import { useActivity } from '@modules/activity';
import { FavoriteBorderRounded, SearchRounded } from '@mui/icons-material';
import {
  Button,
  FormControl,
  InputAdornment,
  InputLabel,
  MenuItem,
  Select,
  TextField,
} from '@mui/material';
import { useTranslation } from '@shared/i18n';
import { useRoute } from '@shared/routing';
import { useState } from 'react';
import { useStudio } from '../../../application';
import { emptyFilter, filterStudyItems, type StudyFilter } from '../../../domain';
import { Heading, StudyCard } from '../../shared/StudioParts';
import '../../studio.css';
export default function StudyLibraryPage() {
  const { page } = useRoute();
  return <StudyLibrary key={page} theory={page === 'theory'} />;
}
function StudyLibrary({ theory }: { theory: boolean }) {
  const { catalog } = useStudio();
  const tr = useTranslation();
  const { favorites } = useActivity();
  const [filter, setFilter] = useState<StudyFilter>(emptyFilter);
  if (!catalog) return null;
  const items = theory ? catalog.theory : catalog.exercises;
  const shown = filterStudyItems(items, filter, favorites);
  const categories = catalog.categories.filter((category) =>
    items.some((item) => item.category === category.id),
  );
  const goals = catalog.goals.filter((goal) => items.some((item) => item.goals.includes(goal.id)));
  return (
    <div className="studio-page">
      <Heading title={tr(theory ? 'Amaliy nazariya' : 'Mashqlar')} />
      <div className="studio-library-filters">
        <TextField
          label={tr('Qidirish')}
          value={filter.query}
          onChange={(event) => setFilter((value) => ({ ...value, query: event.target.value }))}
          slotProps={{
            input: {
              startAdornment: (
                <InputAdornment position="start">
                  <SearchRounded />
                </InputAdornment>
              ),
            },
          }}
        />
        <FormControl>
          <InputLabel id="studio-category-label">{tr('Turi')}</InputLabel>
          <Select
            labelId="studio-category-label"
            label={tr('Turi')}
            value={filter.category}
            onChange={(event) => setFilter((value) => ({ ...value, category: event.target.value }))}
          >
            <MenuItem value="">{tr('Barchasi')}</MenuItem>
            {categories.map((item) => (
              <MenuItem key={item.id} value={item.id}>
                {item.label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        <FormControl>
          <InputLabel id="studio-goal-label">{tr('Maqsad')}</InputLabel>
          <Select
            labelId="studio-goal-label"
            label={tr('Maqsad')}
            value={filter.goal}
            onChange={(event) => setFilter((value) => ({ ...value, goal: event.target.value }))}
          >
            <MenuItem value="">{tr('Barchasi')}</MenuItem>
            {goals.map((item) => (
              <MenuItem key={item.id} value={item.id}>
                {item.label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        {!theory && (
          <FormControl>
            <InputLabel id="studio-level-label">{tr('Daraja')}</InputLabel>
            <Select
              labelId="studio-level-label"
              label={tr('Daraja')}
              value={filter.level}
              onChange={(event) => setFilter((value) => ({ ...value, level: event.target.value }))}
            >
              <MenuItem value="">{tr('Barchasi')}</MenuItem>
              <MenuItem value="easy">{tr('Oson')}</MenuItem>
              <MenuItem value="intermediate">{tr('O‘rta')}</MenuItem>
              <MenuItem value="advanced">{tr('Murakkab')}</MenuItem>
            </Select>
          </FormControl>
        )}
      </div>
      <div className="studio-filter-meta">
        <span role="status">
          {shown.length} {tr(theory ? 'mavzu' : 'mashq')}
        </span>
        <Button
          size="small"
          startIcon={<FavoriteBorderRounded />}
          aria-pressed={filter.favoritesOnly}
          variant={filter.favoritesOnly ? 'contained' : 'text'}
          onClick={() => setFilter((value) => ({ ...value, favoritesOnly: !value.favoritesOnly }))}
        >
          {tr('Sevimlilar')}
        </Button>
      </div>
      {shown.length ? (
        <div className="studio-card-grid">
          {shown.map((item) => (
            <StudyCard key={item.id} item={item} />
          ))}
        </div>
      ) : (
        <EmptyState
          kind={
            filter.favoritesOnly &&
            !filter.query &&
            !filter.category &&
            !filter.goal &&
            !filter.level
              ? 'favorites'
              : 'search'
          }
          title={tr(filter.favoritesOnly ? 'Bu tanlovda sevimlilar yo‘q' : 'Mos dars topilmadi')}
          description={tr('Boshqa so‘z yoki filtr bilan qidirib ko‘ring.')}
          action={{ label: tr('Filtrlarni tozalash'), onClick: () => setFilter(emptyFilter) }}
        />
      )}
    </div>
  );
}
