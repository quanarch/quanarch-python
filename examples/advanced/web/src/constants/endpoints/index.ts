/** The paths the quans listen to, through the quanar. */
export const ENDPOINTS = {
  LOGIN: '/users/login',
  REGISTER: '/users/register',
  ME: '/users/me',
  PRODUCTS: '/products',
  PRODUCT: (id: string) => `/products/${id}`,
  RESTOCK: (id: string) => `/products/${id}/restock`,
  ORDERS: '/orders',
  ORDER: (id: string) => `/orders/${id}`,
  CANCEL: (id: string) => `/orders/${id}/cancel`,
} as const;
