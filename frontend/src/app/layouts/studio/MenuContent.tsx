/* Adapted from Material UI's MIT-licensed Dashboard template MenuContent.
 * https://github.com/mui/material-ui/blob/master/docs/data/material/getting-started/templates/dashboard/components/MenuContent.tsx
 * Copyright (c) 2014 Call-Em-All. See ../MUI-LICENSE.txt.
 */
import {
  AutoStoriesRounded,
  GridViewRounded,
  MusicNoteRounded,
  PianoRounded,
  SettingsRounded,
  BarChartRounded,
} from '@mui/icons-material';
import { List, ListItem, ListItemButton, ListItemIcon, ListItemText, Stack } from '@mui/material';
import { useTranslation } from '@shared/i18n';

import { isPlainLinkClick, routePath, type Page } from '@shared/routing';
const mainListItems = [
  { id: 'dashboard' as Page, text: 'Bosh sahifa', icon: <GridViewRounded /> },
  { id: 'library' as Page, text: 'Kompozitsiyalar', icon: <MusicNoteRounded /> },
  { id: 'exercises' as Page, text: 'Mashqlar', icon: <PianoRounded /> },
  { id: 'theory' as Page, text: 'Nazariya', icon: <AutoStoriesRounded /> },
];
const secondaryListItems = [
  { id: 'statistics' as Page, text: 'Statistika', icon: <BarChartRounded /> },
  { id: 'settings' as Page, text: 'Sozlamalar', icon: <SettingsRounded /> },
];

export default function MenuContent({
  page,
  onNavigate,
}: {
  page: Page;
  onNavigate: (page: Page) => void;
}) {
  const tr = useTranslation();
  const renderItem = (item: (typeof mainListItems)[number]) => (
    <ListItem key={item.id} disablePadding>
      <ListItemButton
        component="a"
        href={routePath(item.id)}
        aria-label={tr(item.text)}
        aria-current={
          page === item.id || (['detail', 'lesson'].includes(page) && item.id === 'library')
            ? 'page'
            : undefined
        }
        selected={
          page === item.id || (['detail', 'lesson'].includes(page) && item.id === 'library')
        }
        onClick={(event) => {
          if (!isPlainLinkClick(event)) return;
          event.preventDefault();
          onNavigate(item.id);
        }}
      >
        <ListItemIcon>{item.icon}</ListItemIcon>
        <ListItemText primary={tr(item.text)} />
      </ListItemButton>
    </ListItem>
  );
  return (
    <Stack
      component="nav"
      id="app-navigation"
      aria-label={tr('Asosiy menyu')}
      className="sidebar-navigation"
      sx={{ flexGrow: 1 }}
    >
      <div className="sidebar-section-label">{tr('Asosiy')}</div>
      <List>{mainListItems.slice(0, 2).map(renderItem)}</List>
      <div className="sidebar-section-label">{tr('Mashg‘ulotlar')}</div>
      <List>{mainListItems.slice(2).map(renderItem)}</List>
      <div className="sidebar-section-label">{tr('Akkaunt')}</div>
      <List>{secondaryListItems.map(renderItem)}</List>
    </Stack>
  );
}
