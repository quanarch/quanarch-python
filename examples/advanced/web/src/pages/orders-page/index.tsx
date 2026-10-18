import { Navigate } from 'react-router-dom';
import { ErrorBanner, OrderRow } from '../../components';
import { PERMISSIONS, ROUTES } from '../../constants';
import { useAuth, useOrders, useProducts } from '../../hooks';

export function OrdersPage() {
  const { session, can } = useAuth();
  const { orders, error, cancel } = useOrders();
  const { products } = useProducts();
  if (!session) return <Navigate to={ROUTES.LOGIN} replace />;

  const everyone = can(PERMISSIONS.READ_ALL_ORDERS);
  const names = Object.fromEntries(products.map((p) => [p.id, p.name]));
  return (
    <section className="orders">
      <h2>{everyone ? 'All orders' : 'Your orders'}</h2>
      <ErrorBanner error={error} />
      {orders.length === 0 && <p className="muted">No orders yet.</p>}
      {orders.map((o) => (
        <OrderRow key={o.id} order={o} names={names} showOwner={everyone} onCancel={() => void cancel(o)} />
      ))}
    </section>
  );
}
