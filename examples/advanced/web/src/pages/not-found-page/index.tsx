import { Link } from 'react-router-dom';
import { ROUTES } from '../../constants';

export function NotFoundPage() {
  return (
    <section className="panel">
      <h2>Not found</h2>
      <Link to={ROUTES.PRODUCTS}>Back to the products</Link>
    </section>
  );
}
