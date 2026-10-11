import type { Session } from '../../domain/entities/session.types.ts';
import type { SessionDto } from '../dto/session.dto.ts';
export const mapSession = (raw: SessionDto): Session => ({
  id: Number(raw.id),
  composition: Number(raw.composition),
  duration_seconds: Number(raw.duration_seconds || Number(raw.minutes || 0) * 60),
  bpm: Number(raw.bpm || 60),
  hand: 'both',
  notes: String(raw.notes || ''),
  confidence: Number(raw.comfort || 3),
  created_at: String(raw.created_at || ''),
});
