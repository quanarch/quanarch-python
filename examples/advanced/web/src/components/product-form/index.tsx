import { useState, type FormEvent } from 'react';
import type { NewProduct } from '../../types';
import { ErrorBanner } from '../error-banner';

const EMPTY = { name: '', description: '', price: '', stock: '' };

/** Sends what is typed; the rules are checked by the quanar, and its answer is shown. */
export function ProductForm({ onCreate }: { onCreate: (product: NewProduct) => Promise<void> }) {
  const [form, setForm] = useState(EMPTY);
  const [error, setError] = useState<unknown>(null);
  const set = (key: keyof typeof EMPTY) => (e: { target: { value: string } }) => setForm({ ...form, [key]: e.target.value });

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    try {
      await onCreate({ name: form.name, description: form.description || undefined, price: Number(form.price), stock: Number(form.stock || 0) });
      setForm(EMPTY);
      setError(null);
    } catch (err) {
      setError(err);
    }
  };

  return (
    <form className="panel form" onSubmit={submit}>
      <h3>New product</h3>
      <input placeholder="Name" value={form.name} onChange={set('name')} />
      <input placeholder="Description" value={form.description} onChange={set('description')} />
      <div className="form__row">
        <input placeholder="Price" inputMode="decimal" value={form.price} onChange={set('price')} />
        <input placeholder="Stock" inputMode="numeric" value={form.stock} onChange={set('stock')} />
      </div>
      <button className="btn">Add</button>
      <ErrorBanner error={error} />
    </form>
  );
}
