import type { PersonalState } from './entities/activity.types.ts';

export const challengeResultKey = (studyId: string, questionId: string) =>
  `${studyId}:challenge:${questionId}`;

export function challengeSummary(
  studyId: string,
  questionIds: string[],
  results: PersonalState['challengeResults'],
) {
  const ids = [...new Set(questionIds)];
  const states = ids.map((id) => results[challengeResultKey(studyId, id)]);
  const correct = states.filter((state) => state === 'correct').length;
  return {
    total: ids.length,
    correct,
    status: (states.includes('incorrect')
      ? 'struggling'
      : ids.length && correct === ids.length
        ? 'mastered'
        : 'learning') as PersonalState['progress'][string],
  };
}

export function recordChallengeAnswer(
  state: PersonalState,
  studyId: string,
  questionIds: string[],
  questionId: string,
  correct: boolean,
): PersonalState {
  if (!questionIds.includes(questionId)) return state;
  const result = correct ? 'correct' : 'incorrect';
  const key = challengeResultKey(studyId, questionId);
  const results: PersonalState['challengeResults'] = { ...state.challengeResults, [key]: result };
  const { status } = challengeSummary(studyId, questionIds, results);
  if (state.challengeResults[key] === result && state.progress[studyId] === status) return state;
  return {
    ...state,
    challengeResults: results,
    progress: { ...state.progress, [studyId]: status },
  };
}

export function markStudyStarted(state: PersonalState, studyId: string): PersonalState {
  if (!studyId || state.progress[studyId]) return state;
  return { ...state, progress: { ...state.progress, [studyId]: 'learning' } };
}
