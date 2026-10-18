import { Outlet } from 'react-router-dom';
import { Header } from '../../components';
import { useAuth, useCart } from '../../hooks';

export function MainLayout() {
  const { session, logout } = useAuth();
  const { lines, clear } = useCart();
  return (
    <div className="app">
      <Header
        session={session}
        cartCount={lines.reduce((n, l) => n + l.quantity, 0)}
        onLogout={() => {
          clear();
          logout();
        }}
      />
      <main className="main">
        <Outlet />
      </main>
    </div>
  );
}
