import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { ROUTES } from '../constants';
import { AuthProvider, CartProvider, OrdersProvider, ProductsProvider, useAuth } from '../hooks';
import { MainLayout } from '../layouts';
import { LoginPage, NotFoundPage, OrdersPage, ProductsPage } from '../pages';

/** Orders exist only for a signed-in user; the provider follows the session. */
function SessionProviders({ children }: { children: React.ReactNode }) {
  const { session } = useAuth();
  return (
    <OrdersProvider key={session?.user.id ?? 'guest'} enabled={!!session}>
      {children}
    </OrdersProvider>
  );
}

export function App() {
  return (
    <AuthProvider>
      <SessionProviders>
        <CartProvider>
          <ProductsProvider>
            <BrowserRouter>
              <Routes>
                <Route element={<MainLayout />}>
                  <Route path={ROUTES.PRODUCTS} element={<ProductsPage />} />
                  <Route path={ROUTES.ORDERS} element={<OrdersPage />} />
                  <Route path={ROUTES.LOGIN} element={<LoginPage />} />
                  <Route path="*" element={<NotFoundPage />} />
                </Route>
              </Routes>
            </BrowserRouter>
          </ProductsProvider>
        </CartProvider>
      </SessionProviders>
    </AuthProvider>
  );
}
