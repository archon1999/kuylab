let account: number | null = null;
export function setAccountScope(id: number | null) {
  account = id;
}
export function accountId() {
  return account;
}
export function scopedKey(key: string) {
  return account === null ? `guest:${key}` : `user:${account}:${key}`;
}
export const accountStorage = {
  getItem: (key: string) => localStorage.getItem(scopedKey(key)),
  setItem: (key: string, value: string) => localStorage.setItem(scopedKey(key), value),
};
