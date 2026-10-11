export type ArrangementDto = {
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

export type CompositionDto = Record<string, unknown> & { arrangement?: ArrangementDto };
export type CompositionListDto = CompositionDto[] | { results: CompositionDto[] };
