import type { Product } from '../../types';
import { formatMoney } from '../../utils';

interface Props {
  product: Product;
  inCart: number;
  canBuy: boolean;
  canManage: boolean;
  onAdd: () => void;
  onRestock: () => void;
  onToggle: () => void;
}

export function ProductCard({ product, inCart, canBuy, canManage, onAdd, onRestock, onToggle }: Props) {
  const left = product.stock - inCart;
  return (
    <article className={`card${product.active ? '' : ' card--inactive'}`}>
      <div className="card__head">
        <h3>{product.name}</h3>
        <span className="price">{formatMoney(product.price)}</span>
      </div>
      {product.description && <p className="muted">{product.description}</p>}
      <p className={product.stock < 5 ? 'stock stock--low' : 'stock'}>{product.stock} in stock</p>
      <div className="card__actions">
        {canBuy && (
          <button className="btn" onClick={onAdd} disabled={!product.active || left <= 0}>
            Add to cart
          </button>
        )}
        {canManage && (
          <>
            <button className="btn btn--ghost" onClick={onRestock}>
              +10 stock
            </button>
            <button className="btn btn--ghost" onClick={onToggle}>
              {product.active ? 'Hide' : 'Show'}
            </button>
          </>
        )}
      </div>
    </article>
  );
}
