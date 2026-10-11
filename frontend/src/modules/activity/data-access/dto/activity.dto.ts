export type RecentDto = { id: string; openedAt: string };
export type PersonalStateDto = {
  progress: Record<string, 'learning' | 'struggling' | 'mastered'>;
  lastStages: Record<string, string>;
  favorites: string[];
  recents: RecentDto[];
  positions: Record<string, number>;
};
export type ActivitySessionDto = {
  id: string;
  startedAt: string;
  seconds: number;
  contentSeconds: Record<string, number>;
  daySeconds: Record<string, number>;
};
