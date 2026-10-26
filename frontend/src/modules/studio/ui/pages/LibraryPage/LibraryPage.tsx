import { useDeferredValue, useRef, useState } from 'react';
import EmptyState from '@shared/ui/EmptyState';
import { useActivity } from '@modules/activity';
import { useTranslation } from '@shared/i18n';
import { ClearRounded, FavoriteBorderRounded, SearchRounded } from '@mui/icons-material';
import {
  Button,
  FormControl,
  IconButton,
  InputAdornment,
  InputLabel,
  MenuItem,
  Pagination,
  Select,
  TextField,
  useMediaQuery,
} from '@mui/material';
import { useStudio } from '../../../application';
import {
  compositionPage,
  emptyCompositionFilter,
  filterCompositions,
  type CompositionFilter,
} from '../../../domain';
import { CompositionCard, Heading } from '../../shared/StudioParts';
import '../../studio.css';

export default function LibraryPage() {
  const { catalog } = useStudio();
  const { favorites } = useActivity();
  const tr = useTranslation();
  const [filter, setFilter] = useState<CompositionFilter>(emptyCompositionFilter);
  const query = useDeferredValue(filter.query);
  const [page, setPage] = useState(1);
  const [size, setSize] = useState(6);
  const list = useRef<HTMLDivElement>(null);
  const reduced = useMediaQuery('(prefers-reduced-motion: reduce)');
  const items = catalog?.compositions || [];
  const collections = [...new Set(items.map((item) => item.collection || '__other__'))];
  const shown = filterCompositions(items, { ...filter, query }, favorites);
  const result = compositionPage(shown, page, size);
  const change = (value: Partial<CompositionFilter>) => {
    setFilter((current) => ({ ...current, ...value }));
    setPage(1);
  };
  const reset = () => {
    setFilter(emptyCompositionFilter);
    setPage(1);
  };
  const filtered = Object.keys(emptyCompositionFilter).some(
    (key) =>
      filter[key as keyof CompositionFilter] !==
      emptyCompositionFilter[key as keyof CompositionFilter],
  );
  return (
    <div className="studio-page studio-library-page">
      <Heading title={tr('Kompozitsiyalar')} />
      {!!items.length && (
        <>
          <div className="composition-library-filters">
            <TextField
              label={tr('Qidirish')}
              placeholder={tr('Asar, bastakor yoki to‘plam')}
              value={filter.query}
              onChange={(event) => change({ query: event.target.value })}
              slotProps={{
                input: {
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchRounded />
                    </InputAdornment>
                  ),
                  endAdornment: filter.query ? (
                    <InputAdornment position="end">
                      <IconButton
                        size="small"
                        aria-label={tr('Qidiruvni tozalash')}
                        onClick={() => change({ query: '' })}
                      >
                        <ClearRounded fontSize="small" />
                      </IconButton>
                    </InputAdornment>
                  ) : undefined,
                },
              }}
            />
            <FormControl>
              <InputLabel id="composition-difficulty-label">{tr('Qiyinchilik')}</InputLabel>
              <Select
                labelId="composition-difficulty-label"
                label={tr('Qiyinchilik')}
                value={filter.difficulty}
                onChange={(event) => change({ difficulty: Number(event.target.value) })}
              >
                <MenuItem value={0}>{tr('Barchasi')}</MenuItem>
                {[1, 2, 3, 4, 5].map((value) => (
                  <MenuItem key={value} value={value}>
                    {'★'.repeat(value)}
                    {'☆'.repeat(5 - value)} · {value}/5
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <FormControl>
              <InputLabel id="composition-collection-label">{tr('To‘plam')}</InputLabel>
              <Select
                labelId="composition-collection-label"
                label={tr('To‘plam')}
                value={filter.collection}
                onChange={(event) => change({ collection: event.target.value })}
              >
                <MenuItem value="">{tr('Barchasi')}</MenuItem>
                {collections.map((value) => (
                  <MenuItem key={value} value={value}>
                    {value === '__other__' ? tr('Alohida asarlar') : value}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <FormControl>
              <InputLabel id="composition-sort-label">{tr('Saralash')}</InputLabel>
              <Select
                labelId="composition-sort-label"
                label={tr('Saralash')}
                value={filter.sort}
                onChange={(event) =>
                  change({ sort: event.target.value as CompositionFilter['sort'] })
                }
              >
                <MenuItem value="curated">{tr('To‘plam tartibida')}</MenuItem>
                <MenuItem value="title">{tr('Nomi bo‘yicha')}</MenuItem>
                <MenuItem value="difficulty">{tr('Osondan murakkabga')}</MenuItem>
                <MenuItem value="duration">{tr('Qisqadan uzunga')}</MenuItem>
              </Select>
            </FormControl>
          </div>
          <div className="studio-filter-meta composition-library-meta">
            <span role="status">{tr('Kompozitsiyalar: {0}', [result.total])}</span>
            <div className="studio-filter-actions">
              {filtered && (
                <Button size="small" onClick={reset}>
                  {tr('Filtrlarni tozalash')}
                </Button>
              )}
              <Button
                size="small"
                startIcon={<FavoriteBorderRounded />}
                aria-pressed={filter.favoritesOnly}
                variant={filter.favoritesOnly ? 'contained' : 'text'}
                onClick={() => change({ favoritesOnly: !filter.favoritesOnly })}
              >
                {tr('Sevimlilar')}
              </Button>
            </div>
          </div>
        </>
      )}
      {!items.length ? (
        <EmptyState
          kind="library"
          title={tr('Hozircha kompozitsiyalar yo‘q')}
          description={tr('Tayyor kompozitsiyalar shu yerda ko‘rinadi.')}
        />
      ) : !shown.length ? (
        <EmptyState
          kind={filter.favoritesOnly ? 'favorites' : 'search'}
          title={tr('Mos kompozitsiya topilmadi')}
          description={tr('Boshqa so‘z yoki filtr bilan qidirib ko‘ring.')}
          action={{ label: tr('Filtrlarni tozalash'), onClick: reset }}
        />
      ) : (
        <>
          <div ref={list} className="studio-compositions">
            {result.items.map((composition) => (
              <CompositionCard
                key={composition.id}
                composition={composition}
                difficulty={filter.difficulty}
              />
            ))}
          </div>
          <div className="composition-pagination">
            <span>
              {result.from}–{result.to} / {result.total}
            </span>
            <Pagination
              count={result.pages}
              page={result.page}
              shape="rounded"
              color="primary"
              aria-label={tr('Kompozitsiyalar sahifalari')}
              getItemAriaLabel={(type, number) =>
                type === 'page'
                  ? tr('{0}-sahifa', [number || 1])
                  : tr(
                      type === 'next'
                        ? 'Keyingi sahifa'
                        : type === 'previous'
                          ? 'Oldingi sahifa'
                          : type === 'first'
                            ? 'Birinchi sahifa'
                            : 'Oxirgi sahifa',
                    )
              }
              onChange={(_, next) => {
                setPage(next);
                requestAnimationFrame(() =>
                  list.current?.scrollIntoView({
                    block: 'start',
                    behavior: reduced ? 'instant' : 'smooth',
                  }),
                );
              }}
            />
            <FormControl size="small" className="composition-page-size">
              <InputLabel id="composition-page-size">{tr('Sahifada')}</InputLabel>
              <Select
                labelId="composition-page-size"
                label={tr('Sahifada')}
                value={size}
                onChange={(event) => {
                  setSize(Number(event.target.value));
                  setPage(1);
                }}
              >
                {[6, 12, 24].map((count) => (
                  <MenuItem key={count} value={count}>
                    {count}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </div>
          <p className="composition-difficulty-note">
            {tr(
              'Yulduzlar shu MIDI variantining qiyinligini bildiradi. Boshqa aranjirovkada daraja farq qilishi mumkin.',
            )}
          </p>
        </>
      )}
    </div>
  );
}
