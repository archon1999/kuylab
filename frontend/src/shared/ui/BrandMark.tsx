/** A grand piano silhouette, shared by navigation and loading states. */
export default function BrandMark({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 64 64" fill="none" aria-hidden="true">
      <path d="M9 29 45 7l4 2L18 29H9Z" fill="currentColor" />
      <path d="m44 11 9 24" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
      <path d="M10 33h43l6-3v10l-10 5H10V33Z" fill="currentColor" />
      <path d="M14 36h30v5H14z" fill="var(--logo-key, #faf8f5)" />
      <path d="M18 36v3m6-3v3m9-3v3m6-3v3" stroke="currentColor" strokeWidth="2.5" />
      <path d="m13 46 1 12h3l2-12m27 0 2 12h3l2-14M32 46v7h6v3H27v-3h2v-7" fill="currentColor" />
    </svg>
  );
}
