# shop · Python advanced example

A full-stack Quanarch application: a quanar server, a qua, three quans and a React client.

```
shop/
├── packages/shop-qua/   the qua: definitions, types and thin calls; no logic
├── quanar/              the server: managers in app/core, each quan in its own process
├── quans/
│   ├── users/           accounts, roles, sign-in; asks the quanar for tokens
│   ├── products/        catalogue and stock; reserves stock for orders
│   └── orders/          orders; follows products by events
├── artifacts/           built quans, served and announced on /events/<quan>
├── web/                 the React client; it only knows the quanar, under /api
└── scripts/             build (and seal), register, start, check
```

Every Python part is its own project in one [uv](https://docs.astral.sh/uv/) workspace: one
environment holds them all while you develop.

## Run

Requires Python 3.12 or later, uv and Node.js 24 or later (for the web client).

```sh
uv sync --all-packages      # once: every Python part
npm install --prefix web    # once: the web client
uv run scripts/start.py     # builds and seals the quans, starts everything
```

| Part | Address |
| --- | --- |
| web | http://localhost:5180 |
| quanar | http://localhost:3000 (`/health`, `/quans`) |
| artifacts | http://localhost:4100 |

The first start creates `admin@shop.test` / `admin1234`. Ctrl+C stops all three.

If a port is taken, move the quanar and tell the web where it went:

```sh
PORT=3200 QUANAR_URL=http://localhost:3200 uv run scripts/start.py    # ARTIFACTS_PORT moves the artifacts
```

Each part on its own, in three terminals (after `uv run scripts/build.py`):

```sh
uv run artifacts/server.py               # 1 · artifacts
cd quanar && uv run python -m app        # 2 · quanar
cd web && npm run dev                    # 3 · web
```

Working on a quan: `uv run scripts/register.py --open` lists the quans without hashes, then
`cd quans/orders && uv run python build.py --watch` rebuilds on every change; the quanar takes
the new build in at once. `scripts/start.py` seals them again.

| Command | |
| --- | --- |
| `uv run scripts/build.py` | build every quan into the artifacts and seal them |
| `uv run scripts/start.py` | `build`, then start artifacts, quanar and web |
| `uv run scripts/register.py` | seal the built quans into `quanar/data/quans.json`; `--open` without hashes |
| `uv run scripts/check.py` | type-check every part: mypy for Python, tsc for the web |

The database is `quanar/data/shop.db`; delete it to start over.

## A quan declares, the quanar does

A quan writes no route, no table and no check by hand. Its package says what it is in one
`manifest = QuanManifest(...)`, and the quanar's managers make it real when it loads the quan:

| The quan declares | in | The quanar's manager |
| --- | --- | --- |
| models: fields, types, unique, index, enum | `models.py` | `schema_manager` creates and migrates the tables |
| permissions | `permissions.py` | `permission_manager` knows them; tokens say who holds them |
| apis: endpoint, method, middlewares, permissions, validation, handler | `apis.py` | `api_manager` opens them, per quan |
| validation rules | `validations.py` | `validation_manager` answers 422 before the quan is reached |
| events it listens to | `events.py` | `event_manager` carries them between quans |

`quan_registry` runs them in that order, then lets the quan start. A request passes the
quanar's middlewares (`authenticate`, `rate-limit`), its permission check and validation,
then the quan's own middlewares (`middlewares.py`), then the handler. Database calls,
password hashing, tokens and events go back to the quanar through the qua.

## An order, by events

`orders` never reads the products' tables. `POST /orders` stores a pending order and emits
`orders.placed`. `products` takes the stock in one transaction and answers
`products.reserved` or `products.rejected`; `orders` follows. Cancelling emits
`orders.cancelled` and `products` gives the stock back.

## Try

- Sign in as a customer and add a product: 403, the quanar checked `products:manage`.
- Send a product with a negative price: 422 with every issue, before the quan runs.
- Order more than the stock: the order is rejected, nothing is taken.
- Change a file in `artifacts/quans` by hand: its hash no longer matches and the quan is unmounted.
- `curl localhost:3000/quans` lists every quan's apis, models, permissions and events.

## The walls, honestly

Each quan runs in its own Python process with an empty environment and a memory ceiling.
Its imports are limited by name, and an audit hook refuses files, sockets and new processes.
Both live inside the interpreter, which offers no real security boundary: code that sets out
to break the rule can reach further through the objects it is given. For quans you do not
trust, isolate their processes at the operating system level too.
