import { createContext, useContext, useEffect, useState } from 'react';
import type { Account, AuthRepository } from '../domain';
export const AuthContext = createContext<AuthRepository | null>(null);
export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) throw new Error('AuthProvider required');
  return value;
}
export function useSession(repository: AuthRepository) {
  const [user, setUser] = useState<Account | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  useEffect(() => {
    let active = true;
    repository
      .session()
      .then((value) => {
        if (active) setUser(value);
      })
      .catch((reason) => {
        if (active) setError(String(reason.message));
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    const changed = (event: StorageEvent) => {
      if (event.key === 'kuylab-auth-change') location.reload();
    };
    const expired = () => location.reload();
    window.addEventListener('storage', changed);
    window.addEventListener('kuylab-session-expired', expired);
    return () => {
      active = false;
      window.removeEventListener('storage', changed);
      window.removeEventListener('kuylab-session-expired', expired);
    };
  }, [repository]);
  return { user, loading, error };
}
