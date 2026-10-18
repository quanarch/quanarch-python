import { ordersApi } from '../../api';
import { appConfig } from '../../config';
import type { CartLine, Order } from '../../types';
import { cartService } from '../cart-service';

const wait = (ms: number) => new Promise((r) => setTimeout(r, ms));

export const orderService = {
  list: () => ordersApi.list(),
  cancel: (order: Order) => ordersApi.cancel(order.id),

  /**
   * The quanar takes the order at once (202) and the stock is decided by events between
   * the quans; this waits for that answer so the user sees confirmed or rejected.
   */
  async place(lines: CartLine[]): Promise<Order> {
    let order = await ordersApi.place(cartService.toItems(lines));
    const until = Date.now() + appConfig.orderSettleMs;
    let delay = 50;
    while (order.status === 'pending' && Date.now() < until) {
      await wait(delay);
      delay = Math.min(delay * 2, 800);
      order = await ordersApi.get(order.id);
    }
    return order;
  },
};
