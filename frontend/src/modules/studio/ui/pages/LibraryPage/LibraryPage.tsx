import { useDeferredValue, useEffect, useRef } from 'react';
import EmptyState from '@shared/ui/EmptyState';
import { useActivity } from '@modules/activity';
import { useTranslation } from '@shared/i18n';
import {
  ClearRounded,
  FavoriteBorderRounded,
  GridViewRounded,
  SearchRounded,
  ViewAgendaOutlined,
} from '@mui/icons-material';
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
  ToggleButton,
  ToggleButtonGroup,
  Tooltip,
  useMediaQuery,
} from '@mui/material';
import { useStudio } from '../../../application';
import { useCompositionLibraryState } from '../../../application/useCompositionLibraryState';
import {
  compositionPage,
  compositionGroups,
  compositionCollections,
  inferCompositionGroup,
  collectionForGroup,
  compositionCollectionLabel,
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
  const { filter, page, size, view, change, reset, setPage, setSize, setView } =
    useCompositionLibraryState();
  const query = useDeferredValue(filter.query);
  const list = useRef<HTMLDivElement>(null);
  const reduced = useMediaQuery('(prefers-reduced-motion: reduce)');
  const scrollToList = () =>
    requestAnimationFrame(() =>
      list.current?.scrollIntoView({
        block: 'start',
        behavior: reduced ? 'instant' : 'smooth',
      }),
    );
  const items = catalog?.compositions || [];
  const groups = compositionGroups(items);
  const activeGroup = filter.group || inferCompositionGroup(items, filter.collection);
  const collections = compositionCollections(items, activeGroup);
  const shown = filterCompositions(items, { ...filter, query }, favorites);
  const result = compositionPage(shown, page, size);
  useEffect(() => {
    if (catalog && query === filter.query && page !== result.page) setPage(result.page, true);
  }, [catalog, query, filter.query, page, result.page]);
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
              <InputLabel id="composition-group-label">{tr('Yo‘nalish')}</InputLabel>
              <Select
                labelId="composition-group-label"
                label={tr('Yo‘nalish')}
                value={activeGroup}
                onChange={(event) =>
                  change({
                    group: event.target.value,
                    collection: collectionForGroup(items, event.target.value, filter.collection),
                  })
                }
              >
                <MenuItem value="">{tr('Barchasi')}</MenuItem>
                {activeGroup && !groups.some((group) => group.id === activeGroup) && (
                  <MenuItem value={activeGroup}>{activeGroup}</MenuItem>
                )}
                {groups.map((group) => (
                  <MenuItem key={group.id} value={group.id}>
                    {group.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <FormControl disabled={!activeGroup && !filter.collection}>
              <InputLabel id="composition-collection-label" shrink>
                {tr('To‘plam')}
              </InputLabel>
              <Select
                labelId="composition-collection-label"
                label={tr('To‘plam')}
                value={filter.collection}
                onChange={(event) => change({ group: activeGroup, collection: event.target.value })}
                displayEmpty
                notched
                renderValue={(value) =>
                  value
                    ? compositionCollectionLabel(items, value)
                    : tr(activeGroup ? 'Barchasi' : 'Avval yo‘nalishni tanlang')
                }
              >
                <MenuItem value="">{tr('Barchasi')}</MenuItem>
                {filter.collection &&
                  !collections.some((item) => item.id === filter.collection) && (
                    <MenuItem value={filter.collection}>
                      {compositionCollectionLabel(items, filter.collection)}
                    </MenuItem>
                  )}
                {collections.map((value) => (
                  <MenuItem key={value.id} value={value.id}>
                    {value.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
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
              <ToggleButtonGroup
                className="composition-view-switch"
                value={view}
                exclusive
                size="small"
                aria-label={tr('Kompozitsiyalar ko‘rinishi')}
                onChange={(_, next: 'list' | 'grid' | null) => next && setView(next)}
              >
                <Tooltip title={tr('Ro‘yxat ko‘rinishi')}>
                  <ToggleButton value="list" aria-label={tr('Ro‘yxat ko‘rinishi')}>
                    <ViewAgendaOutlined fontSize="small" />
                  </ToggleButton>
                </Tooltip>
                <Tooltip title={tr('Katakli ko‘rinish')}>
                  <ToggleButton value="grid" aria-label={tr('Katakli ko‘rinish')}>
                    <GridViewRounded fontSize="small" />
                  </ToggleButton>
                </Tooltip>
              </ToggleButtonGroup>
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
          <div
            ref={list}
            className={`studio-compositions${view === 'grid' ? ' studio-compositions-grid' : ''}`}
          >
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
                scrollToList();
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
                  scrollToList();
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
        </>
      )}
    </div>
  );
}
