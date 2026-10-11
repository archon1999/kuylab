import { useLayoutEffect } from 'react';
import { mountErrorScreen } from './errorScreen';
import BrandMark from './BrandMark';
import './errorState.css';

export default function ErrorState({
  code,
  title,
  description,
  action,
  secondary,
  full = false,
}: {
  code?: string;
  title: string;
  description?: string;
  action?: { label: string; onClick: () => void };
  secondary?: { label: string; onClick: () => void };
  full?: boolean;
}) {
  useLayoutEffect(mountErrorScreen, []);
  return (
    <section className={`error-state ${full ? 'error-state-full' : ''}`} role="alert">
      <div className="error-state-inner">
        <div className="error-state-brand" aria-label="KuyLab">
          <BrandMark />
          <span>KuyLab</span>
        </div>
        {code && <span className="error-state-code">{code}</span>}
        <h1>{title}</h1>
        {description && <p>{description}</p>}
        <div className="error-state-actions">
          {action && (
            <button className="error-state-primary" onClick={action.onClick}>
              {action.label}
              <span aria-hidden="true">→</span>
            </button>
          )}
          {secondary && <button onClick={secondary.onClick}>{secondary.label}</button>}
        </div>
      </div>
    </section>
  );
}
