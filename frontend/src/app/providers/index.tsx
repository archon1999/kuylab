import { ActivityProvider } from '@modules/activity';
import { ProfileProvider, createProfileRepository } from '@modules/profile';
import { StudioProvider, createStudioRepository } from '@modules/studio';
import { NotificationProvider } from '@shared/ui/Notifications';
import { MidiProvider } from '@modules/practice';
const profile = createProfileRepository(),
  studio = createStudioRepository();
export default function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ProfileProvider repository={profile}>
      <NotificationProvider>
        <ActivityProvider>
          <StudioProvider repository={studio}>
            <MidiProvider>{children}</MidiProvider>
          </StudioProvider>
        </ActivityProvider>
      </NotificationProvider>
    </ProfileProvider>
  );
}
