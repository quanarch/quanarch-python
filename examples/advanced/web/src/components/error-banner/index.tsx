import { ApiError } from '../../core';

/** Shows what went wrong, with every validation issue the quanar listed. */
export function ErrorBanner({ error }: { error: unknown }) {
  if (!error) return null;
  const message = error instanceof Error ? error.message : String(error);
  const issues = error instanceof ApiError ? error.issues : [];
  return (
    <div className="banner banner--error" role="alert">
      <strong>{message}</strong>
      {issues.length > 0 && (
        <ul>
          {issues.map((i) => (
            <li key={i.path}>
              <code>{i.path.replace(/^body\./, '')}</code> {i.message}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
