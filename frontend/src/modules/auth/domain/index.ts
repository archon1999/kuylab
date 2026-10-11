export type Account = {
  id: number;
  username: string;
  display_name: string;
  player_preferences: Record<string, unknown>;
};
export type Credentials = { username: string; password: string; display_name?: string };
export type AuthRepository = {
  session(): Promise<Account | null>;
  login(value: Credentials): Promise<void>;
  register(value: Credentials): Promise<void>;
  logout(): Promise<void>;
  password(current: string, next: string): Promise<void>;
};
