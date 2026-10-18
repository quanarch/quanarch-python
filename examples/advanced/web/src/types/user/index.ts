export interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'customer';
  created_at: string;
}

export interface Session {
  token: string;
  expires_at: string;
  user: User;
  permissions: string[];
}
