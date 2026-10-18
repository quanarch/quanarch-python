import type { Product } from '../product';

export type OrderStatus = 'pending' | 'confirmed' | 'rejected' | 'cancelled';

export interface OrderLine {
  product_id: string;
  name: string;
  price: number;
  quantity: number;
}

export interface Order {
  id: string;
  user_id: string;
  status: OrderStatus;
  items: { product_id: string; quantity: number }[];
  lines: OrderLine[] | null;
  total: number | null;
  reason: string | null;
  created_at: string;
}

export interface CartLine {
  product: Product;
  quantity: number;
}
