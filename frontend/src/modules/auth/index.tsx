import type { ReactNode } from 'react';
import { createAuthRepository } from './data-access/repository';
import AuthGate from './ui/AuthGate';
const repository = createAuthRepository();
export function AuthProvider({ children }: { children: ReactNode }) {
  return <AuthGate repository={repository}>{children}</AuthGate>;
}
export { useAuth } from './application';

export { default as PasswordForm } from './ui/PasswordForm';
