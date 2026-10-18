import { ENDPOINTS } from '../../constants';
import { httpClient } from '../../core';
import type { Session, User } from '../../types';

export const usersApi = {
  login: (email: string, password: string) => httpClient.post<Session>(ENDPOINTS.LOGIN, { email, password }),
  register: (input: { email: string; name: string; password: string }) => httpClient.post<User>(ENDPOINTS.REGISTER, input),
};
