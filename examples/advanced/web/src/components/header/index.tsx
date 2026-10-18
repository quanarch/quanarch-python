import { NavLink } from 'react-router-dom';
import { ROUTES } from '../../constants';
import type { Session } from '../../types';

interface Props {
  session: Session | null;
  cartCount: number;
  onLogout: () => void;
}

export function Header({ session, cartCount, onLogout }: Props) {
  return (
    <header className="header">
      <NavLink to={ROUTES.PRODUCTS} className="header__brand">
        Shop
      </NavLink>
      <nav className="header__nav">
        <NavLink to={ROUTES.PRODUCTS} end>
          Products{cartCount > 0 && <span className="pill">{cartCount}</span>}
        </NavLink>
        {session && <NavLink to={ROUTES.ORDERS}>Orders</NavLink>}
      </nav>
      <div className="header__user">
        {session ? (
          <>
            <span>
              {session.user.name} <small className="muted">{session.user.role}</small>
            </span>
            <button className="btn btn--ghost" onClick={onLogout}>
              Sign out
            </button>
          </>
        ) : (
          <NavLink to={ROUTES.LOGIN} className="btn">
            Sign in
          </NavLink>
        )}
      </div>
    </header>
  );
}
