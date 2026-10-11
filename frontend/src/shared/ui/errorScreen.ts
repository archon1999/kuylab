import { useSyncExternalStore } from 'react';
const screens = new Set<symbol>();
const listeners = new Set<() => void>();
const notify = () => listeners.forEach((listener) => listener());
export function mountErrorScreen() {
  const id = Symbol();
  screens.add(id);
  notify();
  return () => {
    screens.delete(id);
    notify();
  };
}
export function useErrorScreen() {
  return useSyncExternalStore(
    (listener) => {
      listeners.add(listener);
      return () => {
        listeners.delete(listener);
      };
    },
    () => screens.size > 0,
  );
}
