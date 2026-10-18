import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';
import { productService } from '../../services';
import type { NewProduct, Product } from '../../types';

interface ProductsValue {
  products: Product[];
  loading: boolean;
  error: unknown;
  search: string;
  setSearch: (search: string) => void;
  reload: () => Promise<void>;
  create: (product: NewProduct) => Promise<void>;
  restock: (product: Product, quantity: number) => Promise<void>;
  toggle: (product: Product) => Promise<void>;
}

const ProductsContext = createContext<ProductsValue | null>(null);

export function ProductsProvider({ children }: { children: ReactNode }) {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<unknown>(null);
  const [search, setSearch] = useState('');

  const reload = useCallback(async () => {
    setLoading(true);
    try {
      setProducts(await productService.list(search));
      setError(null);
    } catch (e) {
      setError(e);
    } finally {
      setLoading(false);
    }
  }, [search]);

  useEffect(() => {
    const timer = setTimeout(() => void reload(), 200);
    return () => clearTimeout(timer);
  }, [reload]);

  const act = useCallback(
    async (action: () => Promise<unknown>) => {
      await action();
      await reload();
    },
    [reload],
  );

  const value = useMemo<ProductsValue>(
    () => ({
      products,
      loading,
      error,
      search,
      setSearch,
      reload,
      create: (p) => act(() => productService.create(p)),
      restock: (p, q) => act(() => productService.restock(p, q)),
      toggle: (p) => act(() => productService.toggle(p)),
    }),
    [products, loading, error, search, reload, act],
  );
  return <ProductsContext.Provider value={value}>{children}</ProductsContext.Provider>;
}

export function useProducts(): ProductsValue {
  const value = useContext(ProductsContext);
  if (!value) throw new Error('useProducts needs a ProductsProvider');
  return value;
}
