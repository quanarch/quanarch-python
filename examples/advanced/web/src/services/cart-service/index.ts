import type { CartLine, Product } from '../../types';

/** The cart is the client's own: plain functions over a list of lines. */
export const cartService = {
  add(lines: CartLine[], product: Product): CartLine[] {
    const found = lines.find((l) => l.product.id === product.id);
    if (!found) return [...lines, { product, quantity: 1 }];
    return lines.map((l) => (l === found ? { ...l, quantity: Math.min(l.quantity + 1, 100) } : l));
  },

  setQuantity(lines: CartLine[], productId: string, quantity: number): CartLine[] {
    if (quantity <= 0) return lines.filter((l) => l.product.id !== productId);
    return lines.map((l) => (l.product.id === productId ? { ...l, quantity: Math.min(quantity, 100) } : l));
  },

  total: (lines: CartLine[]) => lines.reduce((sum, l) => sum + l.product.price * l.quantity, 0),

  toItems: (lines: CartLine[]) => lines.map((l) => ({ product_id: l.product.id, quantity: l.quantity })),
};
