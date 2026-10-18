import { createContext, useContext, useMemo, useState, type ReactNode } from 'react';
import { cartService } from '../../services';
import type { CartLine, Product } from '../../types';

interface CartValue {
  lines: CartLine[];
  total: number;
  add: (product: Product) => void;
  setQuantity: (productId: string, quantity: number) => void;
  clear: () => void;
}

const CartContext = createContext<CartValue | null>(null);

export function CartProvider({ children }: { children: ReactNode }) {
  const [lines, setLines] = useState<CartLine[]>([]);
  const value = useMemo<CartValue>(
    () => ({
      lines,
      total: cartService.total(lines),
      add: (product) => setLines((l) => cartService.add(l, product)),
      setQuantity: (productId, quantity) => setLines((l) => cartService.setQuantity(l, productId, quantity)),
      clear: () => setLines([]),
    }),
    [lines],
  );
  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

export function useCart(): CartValue {
  const value = useContext(CartContext);
  if (!value) throw new Error('useCart needs a CartProvider');
  return value;
}
