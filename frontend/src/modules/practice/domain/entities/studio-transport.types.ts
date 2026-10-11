export type StudioNote = {
  id: string;
  pitch: number;
  hand: 'left' | 'right';
  onset: number;
  duration: number;
  soundDuration: number;
  velocity: number;
};

export type StudioTimeline = { notes: StudioNote[]; duration: number };

export type PlaybackWindow = {
  sourceFrom: number;
  sourceTo: number;
  wallFrom: number;
  speed: number;
  resume: boolean;
  sourceEnd: number;
};
