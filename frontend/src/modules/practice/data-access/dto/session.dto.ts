export type SessionDto = Record<string, unknown>;
export type SessionOverviewDto = { recent_sessions?: SessionDto[]; sessions?: SessionDto[] };
