import '@app/styles/fonts.css';
import Providers from '@app/providers';
import '@app/styles/styles.css';
import '@app/styles/learning.css';
// Keep the shell overrides last; stylesheet import order affects the sidebar layout.
import '@app/styles/appChrome.css';
import '@app/styles/motion.css';
import { initializeMotion } from '@shared/ui/motion';
import ThemedApp from '@app/theme';
import React from 'react';
import { AuthProvider } from '@modules/auth';
import ReactDOM from 'react-dom/client';
import { registerOffline } from '@shared/offline';
registerOffline();
initializeMotion();
ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <AuthProvider>
      <Providers>
        <ThemedApp />
      </Providers>
    </AuthProvider>
  </React.StrictMode>,
);
