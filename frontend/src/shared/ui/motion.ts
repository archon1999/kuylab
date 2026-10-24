export const motionDuration = 200;
export const motionEasing = 'cubic-bezier(0.4, 0, 0.2, 1)';
export const motionDurations = {
  shortest: motionDuration,
  shorter: motionDuration,
  short: motionDuration,
  standard: motionDuration,
  complex: motionDuration,
  enteringScreen: motionDuration,
  leavingScreen: motionDuration,
};

export function initializeMotion() {
  document.documentElement.style.setProperty('--motion-duration', `${motionDuration}ms`);
  document.documentElement.style.setProperty('--motion-easing', motionEasing);
}
