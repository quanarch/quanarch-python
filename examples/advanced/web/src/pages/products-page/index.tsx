import { useState } from 'react';
import { CartPanel, ErrorBanner, ProductCard, ProductForm } from '../../components';
import { PERMISSIONS } from '../../constants';
import { useAuth, useCart, useOrders, useProducts } from '../../hooks';
import type { Order } from '../../types';

export function ProductsPage() {
  const { session, can } = useAuth();
  const { products, error, search, setSearch, create, restock, toggle, reload } = useProducts();
  const cart = useCart();
  const { place } = useOrders();
  const [placing, setPlacing] = useState(false);
  const [result, setResult] = useState<Order | null>(null);
  const [orderError, setOrderError] = useState<unknown>(null);
  const [actionError, setActionError] = useState<unknown>(null);

  const canManage = can(PERMISSIONS.MANAGE_PRODUCTS);
  const guard = (action: () => Promise<void>) => () => action().then(() => setActionError(null), setActionError);

  const placeOrder = async () => {
    setPlacing(true);
    setResult(null);
    try {
      const order = await place(cart.lines);
      setResult(order);
      setOrderError(null);
      if (order.status === 'confirmed') cart.clear();
      await reload();
    } catch (e) {
      setOrderError(e);
    } finally {
      setPlacing(false);
    }
  };

  return (
    <div className="shop">
      <section>
        <input className="search" placeholder="Search products" value={search} onChange={(e) => setSearch(e.target.value)} />
        <ErrorBanner error={error ?? actionError} />
        <div className="grid">
          {products.map((p) => (
            <ProductCard
              key={p.id}
              product={p}
              inCart={cart.lines.find((l) => l.product.id === p.id)?.quantity ?? 0}
              canBuy={!!session}
              canManage={canManage}
              onAdd={() => cart.add(p)}
              onRestock={guard(() => restock(p, 10))}
              onToggle={guard(() => toggle(p))}
            />
          ))}
          {products.length === 0 && <p className="muted">No products.</p>}
        </div>
      </section>
      <div className="side">
        {session && (
          <CartPanel
            lines={cart.lines}
            total={cart.total}
            placing={placing}
            result={result}
            error={orderError}
            onQuantity={cart.setQuantity}
            onPlace={placeOrder}
          />
        )}
        {canManage && <ProductForm onCreate={create} />}
      </div>
    </div>
  );
}
