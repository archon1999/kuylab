export type Recent = { id: string; openedAt: string };

export type PersonalState = {
  progress: Record<string, 'learning' | 'struggling' | 'mastered'>;
  lastStages: Record<string, string>;
  favorites: string[];
  recents: Recent[];
  positions: Record<string, number>;
};

export type ActivitySession = {
  id: string;
  startedAt: string;
  seconds: number;
  contentSeconds: Record<string, number>;
  daySeconds: Record<string, number>;
};

export type ActivityStats = {
  totalSeconds: number;
  weekSeconds: number;
  activeDays: number;
  days: { date: string; seconds: number }[];
  content: { id: string; seconds: number }[];
};
