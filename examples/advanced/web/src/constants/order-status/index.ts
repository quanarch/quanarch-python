import type { OrderStatus } from '../../types';

export const ORDER_STATUS_LABEL: Record<OrderStatus, string> = {
  pending: 'Waiting for stock',
  confirmed: 'Confirmed',
  rejected: 'Rejected',
  cancelled: 'Cancelled',
};

export const PERMISSIONS = {
  MANAGE_PRODUCTS: 'products:manage',
  READ_ALL_ORDERS: 'orders:read-all',
} as const;
