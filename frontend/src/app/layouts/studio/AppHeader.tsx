import { useAuth } from '@modules/auth';
import { MidiButton } from '@modules/practice';
import type { Profile } from '@modules/profile';
import {
  DarkModeOutlined,
  KeyboardArrowDownRounded,
  LanguageRounded,
  LightModeOutlined,
  MenuRounded,
  PersonOutlineRounded,
  SettingsOutlined,
} from '@mui/icons-material';
import { Avatar, Button, IconButton, Menu, MenuItem, Tooltip } from '@mui/material';
import { usePreferences, useTranslation } from '@shared/i18n';
import { isPlainLinkClick, routePath } from '@shared/routing';
import { useState } from 'react';
import PianoLogo from './PianoLogo';

export default function AppHeader({
  profile,
  menuOpen,
  onMenu,
  onHome,
  onSettings,
}: {
  profile: Profile;
  menuOpen: boolean;
  onMenu: () => void;
  onHome: () => void;
  onSettings: () => void;
}) {
  const tr = useTranslation();
  const auth = useAuth();
  const [authError, setAuthError] = useState('');
  const { language, setLanguage, mode, toggleMode } = usePreferences();
  const [languageAnchor, setLanguageAnchor] = useState<HTMLElement | null>(null);
  const [profileAnchor, setProfileAnchor] = useState<HTMLElement | null>(null);
  const languageNames = { uz: 'O‘zbekcha', ru: 'Русский', en: 'English' };
  return (
    <header className="app-header">
      <div className="app-header-brand">
        <IconButton
          className="sidebar-toggle"
          aria-label={tr(menuOpen ? 'Menyuni yopish' : 'Menyuni ochish')}
          aria-expanded={menuOpen}
          aria-controls="app-navigation"
          onClick={onMenu}
        >
          <MenuRounded />
        </IconButton>
        <a
          href={routePath('dashboard')}
          className="brand"
          onClick={(event) => {
            if (!isPlainLinkClick(event)) return;
            event.preventDefault();
            onHome();
          }}
        >
          <PianoLogo className="piano-logo" />
          <span>
            Kuy<span className="brand-light">Lab</span>
          </span>
        </a>
      </div>
      <div className="header-actions">
        <MidiButton />
        <Button
          className="language-control"
          startIcon={<LanguageRounded />}
          endIcon={<KeyboardArrowDownRounded />}
          onClick={(event) => setLanguageAnchor(event.currentTarget)}
          aria-haspopup="menu"
          aria-expanded={!!languageAnchor}
          aria-label={tr('Til')}
        >
          <span className="language-full">{languageNames[language]}</span>
          <span className="language-short" aria-hidden="true">
            {language.toUpperCase()}
          </span>
        </Button>
        <Menu
          anchorEl={languageAnchor}
          open={!!languageAnchor}
          onClose={() => setLanguageAnchor(null)}
        >
          {(['uz', 'ru', 'en'] as const).map((code) => (
            <MenuItem
              key={code}
              selected={language === code}
              onClick={() => {
                setLanguage(code);
                setLanguageAnchor(null);
              }}
            >
              {languageNames[code]} <small className="language-code">{code.toUpperCase()}</small>
            </MenuItem>
          ))}
        </Menu>
        <Tooltip title={tr(mode === 'light' ? 'Qorong‘i rejim' : 'Yorug‘ rejim')}>
          <IconButton
            className="theme-control"
            onClick={toggleMode}
            aria-label={tr(mode === 'light' ? 'Qorong‘i rejim' : 'Yorug‘ rejim')}
          >
            {mode === 'light' ? <DarkModeOutlined /> : <LightModeOutlined />}
          </IconButton>
        </Tooltip>
        <Button
          className="profile-control"
          onClick={(event) => setProfileAnchor(event.currentTarget)}
          aria-label={tr('Profil menyusi')}
          aria-haspopup="menu"
          aria-expanded={!!profileAnchor}
          startIcon={
            <Avatar
              sx={{ width: 30, height: 30, bgcolor: 'var(--orange)', color: '#fff', fontSize: 13 }}
            >
              {profile.display_name?.charAt(0) || 'P'}
            </Avatar>
          }
          endIcon={<KeyboardArrowDownRounded />}
        >
          <span>{profile.display_name}</span>
        </Button>
        <Menu
          anchorEl={profileAnchor}
          open={!!profileAnchor}
          onClose={() => setProfileAnchor(null)}
        >
          <div className="profile-menu-heading">
            <strong>{profile.display_name}</strong>
            <small>{profile.instrument_model}</small>
          </div>
          <MenuItem
            onClick={() => {
              setProfileAnchor(null);
              onSettings();
            }}
          >
            <PersonOutlineRounded sx={{ mr: 1.5, fontSize: 19 }} />
            {tr('Profil')}
          </MenuItem>
          <MenuItem
            onClick={() => {
              setProfileAnchor(null);
              onSettings();
            }}
          >
            <SettingsOutlined sx={{ mr: 1.5, fontSize: 19 }} />
            {tr('Sozlamalar')}
          </MenuItem>
          <MenuItem
            onClick={() => void auth.logout().catch((error) => setAuthError(error.message))}
          >
            {tr('Chiqish')}
          </MenuItem>
          {authError && <p role="alert">{authError}</p>}
        </Menu>
      </div>
    </header>
  );
}
