export type StudioPreferences = {
  noteNames: boolean;
  keyNames: boolean;
  shadows: boolean;
  particles: boolean;
  velocityGradients: boolean;
  left: boolean;
  right: boolean;
  leftColor: string;
  rightColor: string;
  lookahead: number;
  volume: number;
  reverb: number;
  speed: number;
  leftVolume: number;
  rightVolume: number;
  countIn: number;
  focusKeys: boolean;
  compactNoteLengths: boolean;
};

export type RollSettings = Pick<
  StudioPreferences,
  | 'noteNames'
  | 'keyNames'
  | 'shadows'
  | 'particles'
  | 'velocityGradients'
  | 'left'
  | 'right'
  | 'leftColor'
  | 'rightColor'
  | 'lookahead'
  | 'focusKeys'
>;
