import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from 'react';
import { authService } from '../../services';
import type { Session } from '../../types';

interface AuthValue {
  session: Session | null;
  login: (email: string, password: string) => Promise<void>;
  register: (input: { email: string; name: string; password: string }) => Promise<void>;
  logout: () => void;
  can: (permission: string) => boolean;
}

const AuthContext = createContext<AuthValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState(authService.current);

  const login = useCallback(async (email: string, password: string) => setSession(await authService.login(email, password)), []);
  const register = useCallback(async (input: { email: string; name: string; password: string }) => setSession(await authService.register(input)), []);
  const logout = useCallback(() => {
    authService.logout();
    setSession(null);
  }, []);
  const can = useCallback((permission: string) => authService.can(session, permission), [session]);

  const value = useMemo(() => ({ session, login, register, logout, can }), [session, login, register, logout, can]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthValue {
  const value = useContext(AuthContext);
  if (!value) throw new Error('useAuth needs an AuthProvider');
  return value;
}
