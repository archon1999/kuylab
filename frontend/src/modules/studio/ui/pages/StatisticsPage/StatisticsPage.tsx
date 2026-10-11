import EmptyState from '@shared/ui/EmptyState';
import { useActivity } from '@modules/activity';
import { usePreferences, useTranslation } from '@shared/i18n';
import { useStudio } from '../../../application';
import { allStudyItems } from '../../../domain';
import { formatStudioDate } from '../../../domain/dateLabels';
import { Heading, SectionTitle } from '../../shared/StudioParts';
import '../../studio.css';
export default function StatisticsPage() {
  const { stats, sessions } = useActivity();
  const { catalog } = useStudio();
  const { language } = usePreferences();
  const tr = useTranslation();
  const max = Math.max(1, ...stats.days.map((day) => day.seconds));
  const label = (id: string) =>
    catalog?.compositions.find((item) => `composition:${item.id}` === id)?.title ||
    (catalog && allStudyItems(catalog).find((item) => item.id === id)?.title);
  const formatDate = (value: string, short = false) => formatStudioDate(value, language, short);
  return (
    <div className="studio-page">
      <Heading title={tr('Statistika')} />
      <div className="studio-stat-cards">
        <div>
          <span>{tr('Shu hafta')}</span>
          <strong>
            {Math.floor(stats.weekSeconds / 60)} <small>{tr('daq.')}</small>
          </strong>
        </div>
        <div>
          <span>{tr('Jami vaqt')}</span>
          <strong>
            {Math.floor(stats.totalSeconds / 60)} <small>{tr('daq.')}</small>
          </strong>
        </div>
        <div>
          <span>{tr('Faol kunlar')}</span>
          <strong>{stats.activeDays}</strong>
        </div>
      </div>
      <section className="studio-chart-section">
        <SectionTitle title={tr('Kunlar bo‘yicha faollik')} />
        {!stats.days.some((day) => day.seconds > 0) ? (
          <EmptyState
            compact
            kind="activity"
            title={tr('Bu hafta hali faollik yo‘q')}
            description={tr('Mashg‘ulotlaringiz shu yerda jamlanadi.')}
          />
        ) : (
          <div
            className="studio-bar-chart"
            role="img"
            aria-label={`${tr('Kunlar bo‘yicha saytda o‘tkazilgan vaqt')}: ${stats.days.map((day) => `${formatDate(`${day.date}T12:00:00`)} — ${Math.floor(day.seconds / 60)} ${tr('daq.')}`).join('; ')}`}
          >
            {stats.days.map((day) => (
              <div key={day.date}>
                <span className="studio-bar-value">{Math.floor(day.seconds / 60)}</span>
                <div className="studio-bar-track">
                  <i
                    style={{
                      height: `${day.seconds ? Math.max(3, (day.seconds / max) * 100) : 0}%`,
                    }}
                  />
                </div>
                <span>{formatDate(`${day.date}T12:00:00`, true)}</span>
              </div>
            ))}
          </div>
        )}
      </section>
      <div className="studio-dashboard-columns">
        <section>
          <SectionTitle title={tr('Kontent bilan o‘tkazilgan vaqt')} />
          <div className="studio-stat-list">
            {stats.content
              .filter((item) => !!label(item.id))
              .map((item) => (
                <div key={item.id}>
                  <span>{label(item.id)}</span>
                  <strong>
                    {Math.floor(item.seconds / 60)} {tr('daq.')}
                  </strong>
                </div>
              ))}
            {!stats.content.some((item) => !!label(item.id)) && (
              <EmptyState
                compact
                kind="activity"
                title={tr('Hali faollik yo‘q')}
                description={tr('Mashg‘ulotlaringiz shu yerda jamlanadi.')}
              />
            )}
          </div>
        </section>
        <section>
          <SectionTitle title={tr('Oxirgi tashriflar')} />
          <div className="studio-stat-list">
            {sessions
              .slice()
              .sort((a, b) => b.startedAt.localeCompare(a.startedAt))
              .slice(0, 10)
              .map((session) => (
                <div key={session.id}>
                  <span>{formatDate(session.startedAt)}</span>
                  <strong>
                    {Math.floor(session.seconds / 60)} {tr('daq.')}
                  </strong>
                </div>
              ))}
            {!sessions.length && (
              <EmptyState
                compact
                kind="activity"
                title={tr('Hali faollik yo‘q')}
                description={tr('Mashg‘ulotlaringiz shu yerda jamlanadi.')}
              />
            )}
          </div>
        </section>
      </div>
    </div>
  );
}
