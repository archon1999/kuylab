import { ActivityProvider } from '@modules/activity';
import { ProfileProvider, createProfileRepository } from '@modules/profile';
import { StudioProvider, createStudioRepository } from '@modules/studio';
import { NotificationProvider } from '@shared/ui/Notifications';
const profile = createProfileRepository(),
  studio = createStudioRepository();
export default function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ProfileProvider repository={profile}>
      <NotificationProvider>
        <ActivityProvider>
          <StudioProvider repository={studio}>{children}</StudioProvider>
        </ActivityProvider>
      </NotificationProvider>
    </ProfileProvider>
  );
}
