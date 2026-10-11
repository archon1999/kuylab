import { CloseRounded } from '@mui/icons-material';
import { IconButton, Snackbar } from '@mui/material';
import { useTranslation } from '@shared/i18n';
import { createContext, useContext, useState } from 'react';
const Context = createContext<(message: string) => void>(() => {});
export function NotificationProvider({ children }: { children: React.ReactNode }) {
  const [message, setMessage] = useState('');
  const tr = useTranslation();
  return (
    <Context.Provider value={setMessage}>
      {children}
      <Snackbar
        open={!!message}
        autoHideDuration={5000}
        onClose={() => setMessage('')}
        message={tr(message)}
        action={
          <IconButton
            size="small"
            aria-label={tr('Xabarni yopish')}
            color="inherit"
            onClick={() => setMessage('')}
          >
            <CloseRounded />
          </IconButton>
        }
      />
    </Context.Provider>
  );
}
export const useNotify = () => useContext(Context);
