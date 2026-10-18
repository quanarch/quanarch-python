import type { CartLine, Order } from '../../types';
import { formatMoney } from '../../utils';
import { ErrorBanner } from '../error-banner';

interface Props {
  lines: CartLine[];
  total: number;
  placing: boolean;
  result: Order | null;
  error: unknown;
  onQuantity: (productId: string, quantity: number) => void;
  onPlace: () => void;
}

export function CartPanel({ lines, total, placing, result, error, onQuantity, onPlace }: Props) {
  return (
    <aside className="panel cart">
      <h3>Cart</h3>
      {lines.length === 0 && <p className="muted">Empty.</p>}
      {lines.map((l) => (
        <div className="cart__line" key={l.product.id}>
          <span>{l.product.name}</span>
          <input type="number" min={0} max={100} value={l.quantity} onChange={(e) => onQuantity(l.product.id, Number(e.target.value))} />
          <span>{formatMoney(l.product.price * l.quantity)}</span>
        </div>
      ))}
      {lines.length > 0 && (
        <>
          <div className="cart__total">
            <span>Total</span>
            <strong>{formatMoney(total)}</strong>
          </div>
          <button className="btn btn--wide" onClick={onPlace} disabled={placing}>
            {placing ? 'Waiting for stock…' : 'Place order'}
          </button>
        </>
      )}
      {result && (
        <div className={`banner banner--${result.status === 'confirmed' ? 'ok' : 'error'}`}>
          Order {result.status}
          {result.total !== null && result.status === 'confirmed' && <> · {formatMoney(result.total)}</>}
          {result.reason && <> · {result.reason}</>}
        </div>
      )}
      <ErrorBanner error={error} />
    </aside>
  );
}
