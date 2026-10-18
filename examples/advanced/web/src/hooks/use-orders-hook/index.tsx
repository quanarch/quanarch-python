import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';
import { orderService } from '../../services';
import type { CartLine, Order } from '../../types';

interface OrdersValue {
  orders: Order[];
  loading: boolean;
  error: unknown;
  reload: () => Promise<void>;
  place: (lines: CartLine[]) => Promise<Order>;
  cancel: (order: Order) => Promise<void>;
}

const OrdersContext = createContext<OrdersValue | null>(null);

export function OrdersProvider({ children, enabled }: { children: ReactNode; enabled: boolean }) {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<unknown>(null);

  const reload = useCallback(async () => {
    if (!enabled) return setOrders([]);
    setLoading(true);
    try {
      setOrders(await orderService.list());
      setError(null);
    } catch (e) {
      setError(e);
    } finally {
      setLoading(false);
    }
  }, [enabled]);

  useEffect(() => void reload(), [reload]);

  const value = useMemo<OrdersValue>(
    () => ({
      orders,
      loading,
      error,
      reload,
      place: async (lines) => {
        const order = await orderService.place(lines);
        await reload();
        return order;
      },
      cancel: async (order) => {
        await orderService.cancel(order);
        await reload();
      },
    }),
    [orders, loading, error, reload],
  );
  return <OrdersContext.Provider value={value}>{children}</OrdersContext.Provider>;
}

export function useOrders(): OrdersValue {
  const value = useContext(OrdersContext);
  if (!value) throw new Error('useOrders needs an OrdersProvider');
  return value;
}
