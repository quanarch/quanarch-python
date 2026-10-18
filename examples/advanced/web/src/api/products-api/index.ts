import { ENDPOINTS } from '../../constants';
import { httpClient } from '../../core';
import type { NewProduct, Product } from '../../types';

export const productsApi = {
  list: (search = '') => httpClient.get<Product[]>(`${ENDPOINTS.PRODUCTS}${search ? `?search=${encodeURIComponent(search)}` : ''}`),
  create: (product: NewProduct) => httpClient.post<Product>(ENDPOINTS.PRODUCTS, product),
  update: (id: string, changes: Partial<Pick<Product, 'name' | 'price' | 'active'>>) => httpClient.patch<Product>(ENDPOINTS.PRODUCT(id), changes),
  restock: (id: string, quantity: number) => httpClient.post<Product>(ENDPOINTS.RESTOCK(id), { quantity }),
};
