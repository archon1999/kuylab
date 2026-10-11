import { request } from '@shared/api/http';
import type { ScoreRepository, ScoreSummary } from '../../domain/contracts/score.repository';
import type { Score } from '../../domain/score';

export const createScoreRepository = (): ScoreRepository => ({
  async list(id) {
    const result = await request<ScoreSummary[] | { results: ScoreSummary[] }>(
      'scores/?arrangement_id=' + id,
    );
    return Array.isArray(result) ? result : result.results;
  },
  get: (id) => request<Score>('scores/' + id + '/'),
  lesson: (id) => request<Score>('lessons/' + id + '/exercise/'),
  patch: (id, value) => request<Score>('scores/' + id + '/', 'PATCH', value),
  import(input) {
    const form = new FormData();
    form.append('file', new Blob([input.bytes], { type: 'audio/midi' }), input.filename);
    if (input.arrangementId !== undefined)
      form.append('arrangement_id', String(input.arrangementId));
    else form.append('composition_id', String(input.compositionId));
    form.append('title', input.title);
    form.append('rights_confirmed', String(input.rightsConfirmed));
    form.append('exact_version_confirmed', String(input.exactVersionConfirmed));
    return request<Score>('scores/', 'POST', form);
  },
});
