export type Arrangement = {
  id: number;
  title: string;
  source_url: string;
  reference_video_url?: string;
  full_score_url?: string;
  full_score_file_url?: string;
  full_score_verified_at?: string;
  full_score_format?: string;
  full_score_pages?: { number: number; url: string }[];
  arranger?: string;
  exact_version_confirmed?: boolean;
  workflow_status?: string;
  key_signature?: string;
  time_signature?: string;
  active_score_id?: number;
  active_score_format?: 'midi' | 'musicxml' | null;
  active_score_completeness_verified_at?: string | null;
  tempo_bpm?: number;
  tempo_beat_unit?: string;
  page_count?: number;
};

export type Composition = {
  id: number;
  title: string;
  composer: string;
  source_url: string;
  source_type: string;
  arrangement_label: string;
  source_status: string;
  status?: string;
  notes?: string;
  target_bpm?: number;
  arrangement?: Arrangement;
  category?: string;
};

export type CompositionInput = {
  title: string;
  composer: string;
  source_url: string;
  arrangement_title: string;
};
