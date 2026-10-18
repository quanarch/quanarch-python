import { usersApi } from '../../api';
import { STORAGE_KEYS } from '../../constants';
import type { Session } from '../../types';

function read(): Session | null {
  try {
    const session = JSON.parse(localStorage.getItem(STORAGE_KEYS.SESSION) ?? 'null') as Session | null;
    return session && new Date(session.expires_at).getTime() > Date.now() ? session : null;
  } catch {
    return null;
  }
}

export const authService = {
  current: read,

  async login(email: string, password: string): Promise<Session> {
    const session = await usersApi.login(email, password);
    localStorage.setItem(STORAGE_KEYS.SESSION, JSON.stringify(session));
    return session;
  },

  async register(input: { email: string; name: string; password: string }): Promise<Session> {
    await usersApi.register(input);
    return authService.login(input.email, input.password);
  },

  logout() {
    localStorage.removeItem(STORAGE_KEYS.SESSION);
  },

  /** For showing or hiding things only; the quanar checks every permission again. */
  can(session: Session | null, permission: string) {
    return !!session?.permissions.includes(permission);
  },
};
