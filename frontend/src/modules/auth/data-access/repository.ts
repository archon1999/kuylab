import { requestJson } from '@shared/api/transport';
import { accountStorage, setAccountScope } from '@shared/lib/accountScope';
import type { Account, AuthRepository } from '../domain';
export function createAuthRepository(): AuthRepository {
  const changed = () => {
    localStorage.setItem('kuylab-auth-change', crypto.randomUUID());
    location.reload();
  };
  return {
    async session() {
      const result = await requestJson<{ user: Account | null }>('auth/session/');
      setAccountScope(result.user?.id ?? null);
      if (
        result.user &&
        Object.keys(result.user.player_preferences).length &&
        !accountStorage.getItem('player-preferences-pending')
      )
        accountStorage.setItem(
          'kuylab-studio-player-preferences-v1',
          JSON.stringify(result.user.player_preferences),
        );
      return result.user;
    },
    async login(value) {
      await requestJson('auth/login/', 'POST', value);
      changed();
    },
    async register(value) {
      await requestJson('auth/register/', 'POST', value);
      changed();
    },
    async logout() {
      await requestJson('auth/logout/', 'POST', {});
      changed();
    },
    async password(current, next) {
      await requestJson('auth/password/', 'POST', {
        current_password: current,
        new_password: next,
      });
    },
  };
}
