import { productsApi } from '../../api';
import type { NewProduct, Product } from '../../types';

export const productService = {
  list: (search: string) => productsApi.list(search.trim()),
  create: (product: NewProduct) => productsApi.create(product),
  restock: (product: Product, quantity: number) => productsApi.restock(product.id, quantity),
  toggle: (product: Product) => productsApi.update(product.id, { active: !product.active }),
};
