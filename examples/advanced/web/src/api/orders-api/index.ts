import { ENDPOINTS } from '../../constants';
import { httpClient } from '../../core';
import type { Order } from '../../types';

export const ordersApi = {
  list: () => httpClient.get<Order[]>(ENDPOINTS.ORDERS),
  get: (id: string) => httpClient.get<Order>(ENDPOINTS.ORDER(id)),
  place: (items: { product_id: string; quantity: number }[]) => httpClient.post<Order>(ENDPOINTS.ORDERS, { items }),
  cancel: (id: string) => httpClient.post<Order>(ENDPOINTS.CANCEL(id)),
};
