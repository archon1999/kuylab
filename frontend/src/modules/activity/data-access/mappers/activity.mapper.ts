import type { ActivitySession, PersonalState } from '../../domain/entities/activity.types.ts';
const validId = (id: unknown): id is string =>
  typeof id === 'string' && /^[a-zA-Z0-9:_-]{1,100}$/.test(id);
export function mapPersonal(value: PersonalState): PersonalState {
  return {
    comfortableSpeeds: Object.fromEntries(
      Object.entries(value?.comfortableSpeeds || {})
        .filter(
          ([id, speed]) => validId(id) && Number.isInteger(speed) && speed >= 20 && speed <= 200,
        )
        .slice(0, 500),
    ),
    progress: Object.fromEntries(
      Object.entries(value?.progress || {})
        .filter(
          ([id, state]) => validId(id) && ['learning', 'struggling', 'mastered'].includes(state),
        )
        .slice(0, 500),
    ),
    lastStages: Object.fromEntries(
      Object.entries(value?.lastStages || {})
        .filter(([id, stage]) => validId(id) && validId(stage))
        .slice(0, 500),
    ),
    favorites: Array.isArray(value?.favorites) ? value.favorites.filter(validId).slice(0, 500) : [],
    recents: Array.isArray(value?.recents)
      ? value.recents
          .filter((item) => validId(item.id) && Number.isFinite(Date.parse(item.openedAt)))
          .slice(0, 40)
      : [],
    positions: Object.fromEntries(
      Object.entries(value?.positions || {}).filter(
        ([key, val]) => validId(key) && Number.isFinite(val) && val >= 0 && val <= 7200,
      ),
    ),
  };
}
export function validVisit(value: ActivitySession) {
  return (
    value &&
    typeof value.id === 'string' &&
    Number.isFinite(Date.parse(value.startedAt)) &&
    Number.isInteger(value.seconds) &&
    value.seconds >= 0 &&
    value.seconds <= 86400 &&
    value.contentSeconds &&
    value.daySeconds
  );
}
