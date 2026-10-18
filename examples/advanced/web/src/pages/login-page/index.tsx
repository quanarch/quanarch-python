import { useState, type FormEvent } from 'react';
import { Navigate } from 'react-router-dom';
import { ErrorBanner } from '../../components';
import { ROUTES } from '../../constants';
import { useAuth } from '../../hooks';

export function LoginPage() {
  const { session, login, register } = useAuth();
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [form, setForm] = useState({ email: '', name: '', password: '' });
  const [error, setError] = useState<unknown>(null);
  const [busy, setBusy] = useState(false);

  if (session) return <Navigate to={ROUTES.PRODUCTS} replace />;

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setBusy(true);
    try {
      if (mode === 'login') await login(form.email, form.password);
      else await register(form);
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  };
  const set = (key: keyof typeof form) => (e: { target: { value: string } }) => setForm({ ...form, [key]: e.target.value });

  return (
    <form className="panel form login" onSubmit={submit}>
      <div className="tabs">
        <button type="button" className={mode === 'login' ? 'is-on' : ''} onClick={() => setMode('login')}>
          Sign in
        </button>
        <button type="button" className={mode === 'register' ? 'is-on' : ''} onClick={() => setMode('register')}>
          Create account
        </button>
      </div>
      <input placeholder="Email" autoComplete="email" value={form.email} onChange={set('email')} />
      {mode === 'register' && <input placeholder="Name" value={form.name} onChange={set('name')} />}
      <input placeholder="Password" type="password" autoComplete={mode === 'login' ? 'current-password' : 'new-password'} value={form.password} onChange={set('password')} />
      <button className="btn btn--wide" disabled={busy}>
        {mode === 'login' ? 'Sign in' : 'Create account'}
      </button>
      <ErrorBanner error={error} />
      <p className="muted hint">The first start creates admin@shop.test / admin1234.</p>
    </form>
  );
}
