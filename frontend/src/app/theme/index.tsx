import { CssBaseline, ThemeProvider, createTheme } from '@mui/material';
import { usePreferences } from '@shared/i18n';
import { useMemo } from 'react';
import { motionDurations, motionEasing } from '@shared/ui/motion';
import AppLayout from '../layouts/studio/AppLayout';
import { MidiConnectionDialog } from '@modules/practice';

export default function ThemedApp() {
  const { mode } = usePreferences();
  const theme = useMemo(() => {
    const dark = mode === 'dark';
    return createTheme({
      palette: {
        mode,
        primary: { main: dark ? '#eba165' : '#a47148', contrastText: dark ? '#18122b' : '#ffffff' },
        background: { default: dark ? '#18122b' : '#faf8f5', paper: dark ? '#292043' : '#fffdfa' },
        text: { primary: dark ? '#f5edc9' : '#4b5563', secondary: dark ? '#bcb3ce' : '#737c8b' },
        divider: dark ? '#3a3053' : '#eae5df',
        error: { main: dark ? '#f2a197' : '#b65345' },
      },
      typography: {
        fontFamily: '"Alan Sans Variable", "Inter Variable", sans-serif',
        fontSize: 14,
        button: { textTransform: 'none', fontWeight: 600, letterSpacing: 0 },
        h1: { fontFamily: '"Lora Variable", Georgia, serif', fontWeight: 600 },
        h2: { fontFamily: '"Lora Variable", Georgia, serif', fontWeight: 600 },
      },
      shape: { borderRadius: 12 },
      transitions: {
        duration: motionDurations,
        easing: {
          easeInOut: motionEasing,
          easeOut: motionEasing,
          easeIn: motionEasing,
          sharp: motionEasing,
        },
      },
      components: {
        MuiButton: {
          defaultProps: { disableElevation: true },
          styleOverrides: {
            root: { minHeight: 42, paddingInline: 20, borderRadius: 10 },
            outlined: { borderColor: dark ? '#514264' : '#ded3c6' },
          },
        },
        MuiPaper: { styleOverrides: { root: { backgroundImage: 'none' } } },
        MuiDialog: { styleOverrides: { paper: { border: 'none', padding: 8, borderRadius: 16 } } },
        MuiMenu: {
          styleOverrides: {
            paper: {
              border: `1px solid ${dark ? '#3a3053' : '#eae5df'}`,
              boxShadow: '0 12px 36px #18122b14',
            },
          },
        },
        MuiTextField: { defaultProps: { fullWidth: true, variant: 'outlined' } },
        MuiChip: {
          styleOverrides: {
            root: {
              fontSize: 12,
              backgroundColor: dark ? '#32284e' : '#f3eee7',
              color: dark ? '#eba165' : '#8e633f',
            },
          },
        },
        MuiTab: { styleOverrides: { root: { textTransform: 'none' } } },
        MuiSkeleton: {
          defaultProps: { animation: 'wave' },
          styleOverrides: { root: { backgroundColor: dark ? '#3a3053' : '#ece7e0' } },
        },
      },
    });
  }, [mode]);
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AppLayout />
      <MidiConnectionDialog />
    </ThemeProvider>
  );
}
