export const appConfig = {
  /** Where the quanar is reached. The dev server, or a reverse proxy, strips /api and sends the rest on. */
  apiUrl: import.meta.env.VITE_API_URL ?? '/api',
  /** How long to wait for an order to be confirmed or rejected. */
  orderSettleMs: 5000,
};
