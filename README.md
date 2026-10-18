# quanarch-python

The Python stack of [Quanarch](https://quanarch.org): the templates `qu` uses for
`--lang python`.

```sh
qu new project shop --lang python --dir . --qua shop-qua --quanar shop-quanar --quan notes
qu new examples shop --lang python --example advanced --dir .
```

Needs qu 0.3.6 or later, Python 3.12 or later and [uv](https://docs.astral.sh/uv/); the
advanced example's web client also needs Node.js 24 or later.

## How Quanarch works in Python

- The **quanar** is one ASGI server, on Starlette. It holds no business logic: an
  `api_manager` listens for the quans, a `db_manager` stores for them, and a loader
  brings them in.
- A **quan** is a package built into one `.pyz` file. It serves nothing itself:
  `api.get("/notes", handler)` asks the quanar to listen to `GET /notes`, and
  `await db.create("notes", row)` asks it to store a row. It cannot run on its own.
- The **qua** is the contract: `api` and `db` as `typing.Protocol`s, with general
  methods only, and `init()` where the quanar plugs its core in. It knows no tables,
  no users, no stock.

Each quan runs in its own Python process, started with `python -I`, an empty
environment and a memory ceiling. It may import only its own package, the quas
plugged into it and a short list of standard modules, and an audit hook refuses
files, sockets and new processes. These walls live inside the interpreter and are
not a security boundary on their own; quans you do not trust need operating
system isolation too.

A quan's `build.py --watch` serves its file and announces every new build on
`/events`; the quanar follows that stream, loads the quan into memory when it
opens, reloads it on a new build and unmounts it the moment it closes.

## Templates

| Template | What it holds |
| --- | --- |
| `templates/project` | The project root: `conf.qu`, a README and `packages/README.md`. |
| `templates/qua` | The contract, a publishable package: `QuanarCore` with `api` and `db`, `init()` and the thin calls quans make. |
| `templates/quanar` | The server, package `app`: `api_manager`, `db_manager` (in memory), the HTTP app, loader, quan host and event stream. Also renders a **qmock**, on port 3001. |
| `templates/quan` | A quan that listens to `GET` and `POST /<name>` and stores rows in the `<name>` table, with handlers, services, constants and `build.py`. |

Every part is a uv project; a quanar and its quans use the project's quas from
`packages/` through `[tool.uv.sources]`. How a quan or a qua added later is taken
in by the quanar is declared in `stack.qu`, under `on quan` and `on qua`.

## Examples

`examples/advanced` is a full-stack shop: a Starlette quanar, a qua, three quans and a React
client, in one uv workspace. Its quans declare models, permissions, apis with middlewares and
validation, and the events they listen to, as dataclasses; the quanar's managers turn them into
tables, routes and checks. Orders and stock talk only by events. See its README.

## License

Quanarch was created by [Can Berk Coşar](https://berkcosar.com) and is developed at
[Relteco](https://relteco.com).

Licensed under the [Apache License, Version 2.0](LICENSE). See [NOTICE](NOTICE).
