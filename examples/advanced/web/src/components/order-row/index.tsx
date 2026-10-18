import { ORDER_STATUS_LABEL } from '../../constants';
import type { Order } from '../../types';
import { formatDate, formatMoney } from '../../utils';

interface Props {
  order: Order;
  /** Product names by id, for orders that were never priced. */
  names: Record<string, string>;
  showOwner: boolean;
  onCancel: () => void;
}

export function OrderRow({ order, names, showOwner, onCancel }: Props) {
  const cancellable = order.status === 'pending' || order.status === 'confirmed';
  return (
    <article className="panel order">
      <div className="order__head">
        <span className={`status status--${order.status}`}>{ORDER_STATUS_LABEL[order.status]}</span>
        <span className="muted">{formatDate(order.created_at)}</span>
        {showOwner && <code className="muted">{order.user_id.slice(0, 8)}</code>}
        <strong>{order.total !== null ? formatMoney(order.total) : '—'}</strong>
      </div>
      <ul className="order__lines">
        {(order.lines ?? order.items.map((i) => ({ ...i, name: names[i.product_id] ?? 'a removed product', price: 0 }))).map((l) => (
          <li key={l.product_id}>
            {l.quantity} × {l.name}
          </li>
        ))}
      </ul>
      {order.reason && <p className="muted">{order.reason}</p>}
      {cancellable && (
        <button className="btn btn--ghost" onClick={onCancel}>
          Cancel
        </button>
      )}
    </article>
  );
}
