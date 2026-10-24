import { DarkModeOutlined, LightModeOutlined } from '@mui/icons-material';
import ErrorState from '@shared/ui/ErrorState';
import { parseRoute } from '@shared/routing/paths';
import {
  useEffect,
  useLayoutEffect,
  useRef,
  useState,
  type FormEvent,
  type ReactNode,
} from 'react';
import { transitionColorMode } from '@shared/ui/colorModeTransition';
import BrandMark from '@shared/ui/BrandMark';
import { AuthContext, useSession } from '../application';
import type { AuthRepository } from '../domain';
import './auth.css';
function guestPreference(key: string) {
  try {
    return localStorage.getItem(`guest:kuylab-${key}`);
  } catch {
    return null;
  }
}
const labels = {
  uz: [
    'Kirish',
    'Akkaunt yaratish',
    'Login',
    'Parol',
    'Ismingiz',
    'Shaxsiy studiyangiz',
    'Qayta urinish',
    'Kamida 8 belgi',
  ],
  ru: [
    'Войти',
    'Создать аккаунт',
    'Логин',
    'Пароль',
    'Ваше имя',
    'Ваша личная студия',
    'Повторить',
    'Не менее 8 символов',
  ],
  en: [
    'Sign in',
    'Create account',
    'Username',
    'Password',
    'Your name',
    'Your personal studio',
    'Retry',
    'At least 8 characters',
  ],
};
export default function AuthGate({
  repository,
  children,
}: {
  repository: AuthRepository;
  children: ReactNode;
}) {
  const session = useSession(repository);
  const [language, setLanguage] = useState<keyof typeof labels>(() => {
    const saved = guestPreference('language');
    return saved === 'ru' || saved === 'en' ? saved : 'uz';
  });
  const [mode, setMode] = useState<'light' | 'dark'>(() =>
    guestPreference('theme') === 'dark' ? 'dark' : 'light',
  );
  const modeRef = useRef(mode);
  const chooseMode = (next: 'light' | 'dark') => {
    if (modeRef.current === next) return;
    modeRef.current = next;
    transitionColorMode(() => setMode(next));
  };
  useLayoutEffect(() => {
    if (session.user) return;
    document.documentElement.dataset.theme = mode;
    document.documentElement.lang = language;
    try {
      localStorage.setItem('guest:kuylab-language', language);
      localStorage.setItem('guest:kuylab-theme', mode);
    } catch {
      /* The controls still work without browser storage. */
    }
  }, [language, mode, session.user]);
  const text = labels[language];
  const [register, setRegister] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  useEffect(() => {
    if (!session.user)
      document.title = `${parseRoute(location.pathname, location.search).page === 'notFound' ? '404' : session.error ? text[5] : text[register ? 1 : 0]} · KuyLab`;
  }, [text, register, session.user, session.error]);
  if (!session.user && parseRoute(location.pathname, location.search).page === 'notFound')
    return (
      <ErrorState
        full
        code="404"
        title={
          { uz: 'Sahifa topilmadi', ru: 'Страница не найдена', en: 'Page not found' }[language]
        }
        description={
          {
            uz: 'Bu manzil o‘zgargan yoki mavjud emas.',
            ru: 'Этот адрес изменился или не существует.',
            en: 'This address has changed or does not exist.',
          }[language]
        }
        action={{
          label: { uz: 'Bosh sahifa', ru: 'На главную', en: 'Go home' }[language],
          onClick: () => location.assign('/'),
        }}
      />
    );
  if (!session.user && session.error)
    return (
      <ErrorState
        full
        title={
          { uz: 'Ulanib bo‘lmadi', ru: 'Не удалось подключиться', en: 'Unable to connect' }[
            language
          ]
        }
        description={
          {
            uz: 'Studiyaga ulanish vaqtincha uzildi. Yana bir bor urinib ko‘ring.',
            ru: 'Связь со студией временно прервалась. Попробуйте ещё раз.',
            en: 'The connection to your studio was interrupted. Please try again.',
          }[language]
        }
        action={{ label: text[6], onClick: () => location.reload() }}
      />
    );
  if (session.user)
    return <AuthContext.Provider value={repository}>{children}</AuthContext.Provider>;
  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError('');
    setBusy(true);
    const form = new FormData(event.currentTarget);
    try {
      await repository[register ? 'register' : 'login']({
        username: String(form.get('username')),
        password: String(form.get('password')),
        display_name: String(form.get('display_name') || ''),
      });
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason));
      setBusy(false);
    }
  };
  return (
    <main className="auth-shell">
      <section className="auth-card">
        <div className="auth-brand">
          <BrandMark />
          <span>KuyLab</span>
        </div>
        {session.loading ? (
          <div
            role="status"
            className="auth-pulse"
            aria-label={{ uz: 'Yuklanmoqda…', ru: 'Загрузка…', en: 'Loading…' }[language]}
          />
        ) : session.error ? (
          <>
            <p role="alert">{session.error}</p>
            <button onClick={() => location.reload()}>{text[6]}</button>
          </>
        ) : (
          <>
            <div className="auth-preferences">
              <div
                className="auth-language"
                role="group"
                aria-label={{ uz: 'Til', ru: 'Язык', en: 'Language' }[language]}
              >
                {(['uz', 'ru', 'en'] as const).map((code) => (
                  <button
                    type="button"
                    key={code}
                    lang={code}
                    aria-pressed={code === language}
                    onClick={() => setLanguage(code)}
                  >
                    {code.toUpperCase()}
                  </button>
                ))}
              </div>
              <div
                className="auth-mode"
                role="group"
                aria-label={{ uz: 'Rang rejimi', ru: 'Тема', en: 'Theme' }[language]}
              >
                <button
                  type="button"
                  aria-pressed={mode === 'light'}
                  aria-label={
                    { uz: 'Yorug‘ rejim', ru: 'Светлая тема', en: 'Light mode' }[language]
                  }
                  onClick={() => chooseMode('light')}
                >
                  <LightModeOutlined />
                </button>
                <button
                  type="button"
                  aria-pressed={mode === 'dark'}
                  aria-label={
                    { uz: 'Qorong‘i rejim', ru: 'Тёмная тема', en: 'Dark mode' }[language]
                  }
                  onClick={() => chooseMode('dark')}
                >
                  <DarkModeOutlined />
                </button>
              </div>
            </div>
            <h1>{text[register ? 1 : 0]}</h1>
            <p>{text[5]}</p>

            <form onSubmit={submit}>
              {register && (
                <label>
                  {text[4]}
                  <input name="display_name" autoComplete="name" maxLength={80} required />
                </label>
              )}
              <label>
                {text[2]}
                <input
                  name="username"
                  autoComplete="username"
                  maxLength={150}
                  required
                  autoCapitalize="none"
                />
              </label>
              <label>
                {text[3]}
                <input
                  name="password"
                  type="password"
                  autoComplete={register ? 'new-password' : 'current-password'}
                  minLength={register ? 8 : undefined}
                  required
                />
                {register && <small>{text[7]}</small>}
              </label>
              {error && <p role="alert">{error}</p>}
              <button className="auth-submit" disabled={busy}>
                {busy ? '…' : text[register ? 1 : 0]}
              </button>
            </form>
            <button
              className="auth-alternative"
              onClick={() => {
                setRegister(!register);
                setError('');
              }}
            >
              {text[register ? 0 : 1]}
            </button>
          </>
        )}
      </section>
    </main>
  );
}
