export type Session = {
  id?: number;
  composition: number;
  duration_seconds: number;
  bpm: number;
  hand: string;
  notes: string;
  confidence: number;
  created_at?: string;
};
