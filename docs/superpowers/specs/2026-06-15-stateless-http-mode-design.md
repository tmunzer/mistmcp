# Stateless HTTP transport mode — design

- **Date:** 2026-06-15
- **Status:** Approved (design)
- **Author:** Thomas Munzer (port assisted by Claude)
- **Repo:** `tmunzer/mistmcp` (public)

## 1. Summary

Add an **opt-in** "stateless HTTP" transport. When enabled (`MISTMCP_STATELESS=true`
or `--stateless`) together with `--transport http`, the server is served via
`mcp_server.http_app(stateless_http=True)` behind `uvicorn`, so the MCP SDK builds a
**fresh transport per request** with no server-side session to go stale. The practical
benefit: an already-connected MCP client **survives a server restart** without
reconnecting (no session id to invalidate).

This is a **port** of a feature already shipped on a private fork
(`tmunzer-AIDE/mistmcp-private` PR #15). The port keeps only the parts that fit this
repo; fork-only machinery (URL elicitation mode, web UI, MongoDB, retention sweeper,
push notifier) is dropped because none of it exists here.

### Design principles

1. **Opt-in and additive.** Default off ⇒ runtime behavior is unchanged.
2. **Behavior-neutral centralization.** Moving write-tool visibility to build time must
   not change what any *stateful* session ultimately sees.
3. **No in-band elicitation in stateless.** Stateless has no live session and no
   server→client channel, so the `ctx.elicit()` handshake cannot work. The design
   refuses exactly the one config that would require it, and otherwise fails closed.

## 2. Background / current behavior

- `ServerConfig` (`src/mistmcp/config.py`) holds `transport_mode` (`"stdio"`/`"http"`),
  `enable_write_tools`, `disable_elicitation`, `response_format`, `debug`, `log_file`.
  There is **no** `elicitation_mode`, no URL mode, no web UI, no MongoDB.
- `__main__.py` provides `start()`, `load_env_var()` (returns an 8-tuple), and `main()`
  (argparse). HTTP is served today via `mcp_server.run(transport="http", host, port)`.
- `server.py` builds a module-level singleton `mcp = FastMCP(...)` and, at module scope,
  runs `mcp.add_transform(Visibility(False, tags={"write"}, components={"tool"}))`.
  `create_mcp_server(config)` loads tools and returns that singleton.
- `ElicitationMiddleware` (`elicitation_middleware.py`) has **only** `on_initialize`. It
  resolves write-tool visibility **per session**: it always ends in an
  `if/elif/else` that explicitly enables/disables `write` and `write_delete`, and it
  records `disable_elicitation` session state via `ctx.set_state(...)`.
- `config_elicitation_handler` (`elicitation_processor.py`) reads
  `await ctx.get_state("disable_elicitation")`; if `True` it auto-accepts, otherwise it
  calls `ctx.elicit(...)` (requires a live session).

### Tool / tag inventory (verified)

Each of the four tools in the write/mutation surface carries exactly one tag:

| Tag | Tool | Build-time visibility today | How a mutation is gated today |
|---|---|---|---|
| `write` | `mist_update_configuration_objects` | **hidden** (server.py:200) | shown per session by middleware when write enabled |
| `write_delete` | `mist_change_configuration_objects` (incl. DELETE) | **hidden** | URL query parameters never expose it; mutation always elicits when otherwise enabled |
| `utilities_upgrade` | `mist_upgrades` | **visible, never touched** | mutating actions elicit only — **no `enable_write_tools` check** |
| `utilities` | `mist_utilities` | visible (`utilities` tag) | mutating utilities hard-gated by `enable_write_tools` (`utilities.py:838`) **and** then elicit |

The asymmetry between `mist_upgrades` (elicitation-only) and `mist_utilities`
(`enable_write_tools` + elicitation) is intentional existing behavior and is **preserved**.

### Why this is the crux of the port

In stateless mode each request is served by a **fresh transport that the SDK starts
already-initialized**, so `on_initialize` **cannot be relied on to set state for later tool
calls** — any state it records during one request does not carry to a subsequent
tool-call request, and the middleware's per-session visibility resolution does not run for
those calls. Therefore **build-time visibility is final** in stateless mode. Today only
`write` is hidden at build time, which means in naive stateless:

- `write_delete` (the DELETE tool) would be **visible** in a read-only session, and
- worse, in the DANGER-ZONE config (see §5.4) `on_call_tool` sets `disable_elicitation`,
  so a visible `write_delete` would **auto-accept** — escalating beyond stateful
  DANGER-ZONE behavior, where `write_delete` is explicitly hidden.

Hence folding `write_delete` into the build-time resolver is **required**, not optional.

## 3. Tech / version compatibility (verified in this repo)

- `fastmcp 3.4.2` — `FastMCP.http_app(..., stateless_http: bool | None = None, ...)` is
  supported; `http_app(stateless_http=True)` builds a `StarletteWithLifespan` app.
- `uvicorn 0.49.0` — `ws="websockets-sansio"` is a valid choice
  (`auto|none|websockets|websockets-sansio|wsproto`).
- `Context.set_state(key, value, *, serializable: bool = True)` — `serializable=False`
  (request-scoped state) is supported.
- `mcp 1.27.2`. No `pymongo`, no web UI, no URL mode.
- Tests: `pytest`, `asyncio_mode=auto`, coverage floor 30%. CI runs on Python
  3.10–3.13. No Mongo-absent CI gate is needed (there is no Mongo here).

## 4. Scope

### In scope

- `stateless` config field + `validate_stateless_config()` gate.
- `MISTMCP_STATELESS` env + `--stateless` CLI flag, threaded through
  `load_env_var()`/`main()`/`start()`.
- **New:** `MISTMCP_DISABLE_ELICITATION` env path (so env-only deployments can reach the
  DANGER-ZONE combo that stateless writes require — see §5.2).
- Stateless launch path (`_run_stateless_http`) using `http_app(stateless_http=True)` +
  `uvicorn.run(...)`. Non-stateless paths unchanged.
- Build-time write-tool visibility centralization for `write` + `write_delete` into
  `create_mcp_server()`.
- `ElicitationMiddleware.on_call_tool` to set request-scoped `disable_elicitation` in the
  stateless DANGER-ZONE path.
- A deterministic fail-closed guard in `config_elicitation_handler` so mutating actions
  that reach elicitation in stateless cannot hang or behave undefined (see §5.7).
- Observability log; README docs (this repo has no `.env.example`; the README env-var
  table is the canonical place — see §5.6).
- Tests.

### Out of scope (dropped fork-only machinery)

- URL elicitation mode, `_ensure_started_safe`, MongoDB, retention sweeper, push
  notifier and notifier-skip logic — none exist in this repo.
- Gating `mist_upgrades`/`mist_utilities` visibility (they are mixed read/write tools;
  hiding them would remove valid read/list behavior). Their mutation gating is unchanged.

## 5. Detailed design

### 5.1 Config + validation (`config.py`)

Add to `ServerConfig.__init__`:

```python
stateless: bool = False,
...
self.stateless = stateless
```

Add a dedicated exception and a pure validator:

```python
class ConfigurationError(Exception):
    """Raised when the server configuration is invalid and startup must be refused."""


def validate_stateless_config(config: ServerConfig) -> None:
    """Refuse stateless when it collides with in-band elicitation.

    Stateless HTTP has no live session and no server->client channel, so the
    ctx.elicit() handshake cannot work. The only config that *needs* that handshake
    is: write tools enabled over HTTP without disable_elicitation. Everything else
    (read-only HTTP, write + disable_elicitation, stdio) is stateless-safe.
    """
    if not config.stateless:
        return
    if (
        config.transport_mode == "http"
        and config.enable_write_tools
        and not config.disable_elicitation
    ):
        raise ConfigurationError(
            "Stateless HTTP mode is incompatible with in-band elicitation "
            "(write tools enabled without disable_elicitation), which needs a live "
            "session. Add --disable-elicitation / MISTMCP_DISABLE_ELICITATION=true, "
            "drop --enable-write-tools, or unset --stateless / MISTMCP_STATELESS."
        )
```

(No `elicitation_mode` term — simplified gate, as this repo has no URL mode.)

### 5.2 Env / CLI threading (`__main__.py`)

**`load_env_var`** — add a `stateless` parameter and a `MISTMCP_STATELESS` parse, and
add the new `MISTMCP_DISABLE_ELICITATION` parse (mirroring the existing
`MISTMCP_ENABLE_WRITE_TOOLS` idiom so the CLI flag is the default and the env can
override). Return becomes a **9-tuple** (adds `stateless`).

```python
env_stateless = os.getenv("MISTMCP_STATELESS", str(stateless))
stateless = env_stateless.lower() in ("true", "1", "yes")

env_disable_elicitation = os.getenv("MISTMCP_DISABLE_ELICITATION", str(disable_elicitation))
disable_elicitation = env_disable_elicitation.lower() in ("true", "1", "yes")
```

**`main()`** — add the CLI flag and thread `args.stateless` into `load_env_var`/`start`:

```python
parser.add_argument(
    "--stateless",
    action="store_true",
    help="Serve HTTP statelessly (fresh transport per request) so the MCP client "
         "survives a server restart. HTTP only; incompatible with in-band elicitation. "
         "Loses server->client push.",
)
```

`main()` converts a refused config into a **non-zero exit** (see §5.8 fatality):

```python
try:
    start(transport_mode, mcp_host, mcp_port, debug, enable_write_tools,
          disable_elicitation, response_format, log_file, stateless)
except ConfigurationError as exc:
    logger.error("Invalid configuration: %s", exc)
    raise SystemExit(2)
```

**`start()`** — add a `stateless: bool = False` parameter; set `config.stateless`; add the
transport guard; validate **before** the broad `try`; log the active mode:

```python
config.stateless = stateless

# stateless only applies to http
if config.stateless and transport_mode != "http":
    logger.warning(
        "MISTMCP_STATELESS / --stateless is set but transport is %s; stateless "
        "applies only to http — ignoring.", transport_mode)
    config.stateless = False

# Refuse incompatible config BEFORE the broad try below, so it cannot be swallowed.
validate_stateless_config(config)

if config.stateless:  # implies http
    logger.info(
        "Stateless HTTP mode active: fresh transport per request, so an "
        "already-connected MCP client survives a server restart. Server->client "
        "push (notifications/elicitation) is disabled; in-band elicitation is "
        "unavailable, so destructive utility/upgrade actions require "
        "disable_elicitation (DANGER ZONE) or are refused.")
```

### 5.3 Launch path (`__main__.py`)

Keep stdio and non-stateless HTTP **byte-for-byte**; add only the stateless branch:

```python
if transport_mode == "http":
    if config.stateless:
        _run_stateless_http(mcp_server, mcp_host, mcp_port)
    else:
        mcp_server.run(transport="http", host=mcp_host, port=mcp_port)  # unchanged
else:
    mcp_server.run()  # unchanged
```

```python
def _run_stateless_http(mcp_server, host: str, port: int) -> None:
    """Serve via http_app(stateless_http=True): the SDK builds a fresh transport per
    request, so there is no session id to go stale on a server restart. We pass no
    event_store; in stateless mode the SDK's per-request transport uses
    event_store=None regardless (the resumable GET stream is dropped)."""
    import uvicorn

    app = mcp_server.http_app(stateless_http=True)
    uvicorn.run(app, host=host, port=port, lifespan="on",
                timeout_graceful_shutdown=2, ws="websockets-sansio")
```

`http_app()` and `run(transport="http")` use the same default mount path, so the
client-facing URL path is unchanged between stateless and non-stateless.

### 5.4 Build-time write visibility (`server.py`)

Remove the module-scope transform (current line 200) and resolve visibility from config
inside `create_mcp_server()`:

```python
_PROTECTED_WRITE_TAGS = {"write", "write_delete"}


def _write_visible_tags(config: ServerConfig) -> set[str]:
    """Protected write tags that should be visible at build time for this config.
    Authoritative in stateless mode; a behavior-neutral floor in stateful mode, where
    ElicitationMiddleware.on_initialize re-resolves write/write_delete per session."""
    if config.enable_write_tools and config.disable_elicitation:
        return {"write"}        # DANGER ZONE: update only, never write_delete
    return set()                # read-only / elicitation-capable: hide both


def _configure_write_visibility(mcp_server: FastMCP, config: ServerConfig) -> None:
    """Install a deterministic hide-all-then-show-visible sequence for the protected
    write tags. FastMCP Visibility marks are later-wins, so the EFFECTIVE visibility
    equals this call's resolution even when called repeatedly on the reused module
    singleton. (The transform list itself grows by 1-2 entries per call; create_mcp_server
    runs once per process, so this is bounded. There is no per-transform removal API for
    Visibility, and effective-visibility idempotency is sufficient for correctness.)"""
    visible = _write_visible_tags(config)
    mcp_server.add_transform(
        Visibility(False, tags=_PROTECTED_WRITE_TAGS, components={"tool"}))
    if visible:
        mcp_server.add_transform(
            Visibility(True, tags=visible, components={"tool"}))
```

Call it at the end of `create_mcp_server`:

```python
def create_mcp_server(config: ServerConfig) -> FastMCP:
    enabled_tools = _load_tools(config)
    _configure_write_visibility(mcp, config)
    logger.debug("MCP Server ready with %d tools", len(enabled_tools))
    return mcp
```

**Why behavior-neutral in stateful mode:** `on_initialize` always re-resolves both
`write` and `write_delete` per session (every branch ends in the explicit
enable/disable), and per-session `enable_components`/`disable_components` override the
server-level transform (this is exactly how `write` already works today). `utilities` and
`utilities_upgrade` are never touched by the resolver, so they remain always-visible.

### 5.5 Request-scoped elicitation state (`elicitation_middleware.py`)

Add request hooks so stateless requests can establish their per-request policy before
FastMCP applies visibility transforms.

First, `on_call_tool` makes the DANGER-ZONE auto-accept work in stateless, where state
set in `on_initialize` does not carry to the tool-call request:

```python
async def on_call_tool(self, context, call_next):
    ctx = context.fastmcp_context
    if (
        config.stateless
        and config.transport_mode == "http"
        and config.enable_write_tools
        and config.disable_elicitation
        and ctx is not None
    ):
        # In stateless, on_initialize state does not carry to this call. Set the flag
        # request-scoped so config_elicitation_handler auto-accepts for this call only,
        # without leaking into the session store (per-request sessions are discarded).
        await ctx.set_state("disable_elicitation", True, serializable=False)
    return await call_next(context)
```

Gated on `config.stateless` so the stateful code path is literally unchanged (stateful
DANGER ZONE already sets the flag in `on_initialize`).

URL query parameters do not alter write-tool visibility or bypass elicitation. In
particular, `experimental=true` has no special meaning.

### 5.6 Observability and documentation

The INFO log in §5.2 is emitted once at startup when stateless+http is active. No
per-request logging is added.

This repo has **no `.env.example`**; the README environment-variable tables (currently
README.md lines ~84–106) are the canonical reference. The README change adds rows for
`MISTMCP_STATELESS` and `MISTMCP_DISABLE_ELICITATION` and a short "Stateless HTTP mode"
subsection covering the restart-survival benefit and the no-push / writes-require-DANGER-ZONE
trade-offs. No new `.env.example` artifact is introduced.

### 5.7 Deterministic fail-closed elicitation guard (`elicitation_processor.py`)

The handler must not depend on `ctx.elicit()`'s undefined behavior in stateless (it could
block awaiting a client response that can never be correlated). Add an explicit guard
**after** the state check so any mutating action that reaches elicitation in stateless
fails fast and deterministically:

```python
from mistmcp.config import config


class ElicitationUnavailableError(RuntimeError):
    """Raised when elicitation is required but cannot be performed (stateless HTTP has no
    server->client channel). The tool wrappers convert this into a clean ToolError."""


async def config_elicitation_handler(message, ctx: Context):
    if await ctx.get_state("disable_elicitation") is True:
        return ElicitResult(action="accept")

    if config.stateless and config.transport_mode == "http":
        # No live session / server->client channel in stateless: in-band elicitation
        # cannot complete. Fail closed deterministically instead of calling ctx.elicit().
        raise ElicitationUnavailableError(
            "In-band elicitation is unavailable in stateless HTTP mode; this action "
            "requires disable_elicitation (DANGER ZONE) or a stateful transport."
        )

    result = await ctx.elicit(message, response_type=None)
    ...  # unchanged
```

All three elicitation call sites already wrap `config_elicitation_handler` in
`try/except Exception` and re-raise as `ToolError` (`upgrades.py` `_confirm_upgrade_write_action`,
`utilities.py` `_confirm_disruptive_utility`, `change_configuration_objects.py`), so the raised
`ElicitationUnavailableError` surfaces to the client as a clean tool error. This guard is
behavior-neutral in stateful mode (`config.stateless` is `False`) and never reached in the
stateless DANGER-ZONE path (the state check returns "accept" first).

### 5.8 Fatality of config errors

`validate_stateless_config()` is called in `start()` **before** the broad
`try/except Exception` that wraps `create_mcp_server`/`run`, so a `ConfigurationError`
propagates out of `start()` rather than being logged-and-swallowed. `main()` catches
`ConfigurationError`, logs a clear message, and exits with status `2`. An invalid server
config therefore **never** results in a silent successful return.

## 6. Visibility & behavior matrix

Tools: **W** = `mist_update_configuration_objects` (`write`),
**WD** = `mist_change_configuration_objects` (`write_delete`),
**UP** = `mist_upgrades` (`utilities_upgrade`),
**UT** = `mist_utilities` (`utilities`). "elicit" = prompts the client; "auto" =
auto-accept; "fail-closed" = mutation refused with a clean `ToolError`.

| Scenario | W | WD | UP | UT | Mutation behavior |
|---|---|---|---|---|---|
| **Stateful normal** (read-only) | hidden | hidden | visible | visible | UT mutating hard-blocked (`enable_write_tools=False`); UP mutating elicits (fails if client lacks elicitation) |
| **Stateful elicitation-capable** (write, client supports elicit) | visible | hidden | visible | visible | W/UP/UT mutating **elicit** (user prompted) |
| **Stateful DANGER** (write + disable_elicitation) | visible | hidden | visible | visible | W/UP/UT mutating **auto** (session state set in on_initialize) |
| **Stateless read-only** (no write; gate passes) | hidden | hidden | visible | visible | UT mutating hard-blocked (`enable_write_tools=False`); UP mutating **fail-closed** via the §5.7 guard (ElicitationUnavailableError ⇒ ToolError, deterministic — never calls `ctx.elicit()`); WD not listed |
| **Stateless DANGER** (write + disable_elicitation; gate passes) | visible | hidden | visible | visible | W/UP/UT mutating **auto** (request-scoped state set in on_call_tool); WD hidden ⇒ no delete |

Note: **stateless + http + write + NOT disable_elicitation** is **refused at startup**
(§5.1) and so has no row.

Each stateless row's W/WD column matches its stateful counterpart's *final* (post-
initialize) state — that is the behavior-neutrality the centralization preserves.

## 7. Accepted trade-offs

- **No server→client push in stateless.** `stateless_http=True` drops the GET route, so
  notifications and in-band elicitation are unavailable. Accepted.
- **Destructive actions in stateless read-only fail closed.** `mist_upgrades` mutating
  actions hit the §5.7 guard and return a clean `ToolError` (elicitation unavailable)
  deterministically, rather than relying on `ctx.elicit()` behavior; `mist_utilities`
  mutating actions are hard-blocked earlier by `enable_write_tools`. This is the safe
  default.
- **Write in stateless requires explicit configuration.** Standard update writes
  require `enable_write_tools=True` + `disable_elicitation=True` (auto-accept).

## 8. Testing strategy

`pytest`, `asyncio_mode=auto`. New/extended tests (all pure — no network, no Mongo):

- **Config / validation** (`test_config*.py`): `validate_stateless_config` refusal matrix —
  refuse only `stateless+http+enable_write_tools+not disable_elicitation`; pass for stdio,
  read-only, and write+disable_elicitation. `stateless` defaults to `False`.
- **Env / CLI / start** (`test_main.py`): `MISTMCP_STATELESS` and
  `MISTMCP_DISABLE_ELICITATION` truthy/falsy parsing; `--stateless` flag; `load_env_var`
  9-tuple; `start()` sets `config.stateless`; stdio downgrade warning; `start()` raises
  `ConfigurationError` (not swallowed) on the refused combo; `main()` exits non-zero.
- **Visibility** (`test_server.py`): `_write_visible_tags` matrix (read-only ⇒ `∅`;
  DANGER ⇒ `{write}`); `_configure_write_visibility` hides `{write, write_delete}` and
  shows the resolved set; **effective-visibility idempotency** — call twice with different
  configs on the singleton and assert the last config wins; confirm `utilities`/
  `utilities_upgrade` are untouched.
- **Launch** (`test_main.py` or new): mock `http_app` + `uvicorn.run`; assert `start()`
  selects `_run_stateless_http` for http+stateless and `mcp_server.run(...)` for
  http+non-stateless; assert `http_app(stateless_http=True)` is called with **no**
  `event_store` kwarg; assert uvicorn args `(host, port, lifespan="on",
  timeout_graceful_shutdown=2, ws="websockets-sansio")`.
- **Middleware** (`test_elicitation_middleware.py`): `on_call_tool` sets request-scoped
  (`serializable=False`) `disable_elicitation` only in stateless DANGER ZONE; URL query
  parameters cannot enable write tools; existing `on_initialize` tests stay green under
  the new build-time floor.
- **Elicitation guard** (`test_elicitation_processor.py` or similar): `config_elicitation_handler`
  returns `accept` when `disable_elicitation` state is `True`; raises
  `ElicitationUnavailableError` when `config.stateless and config.transport_mode == "http"`
  and state is not set (asserting `ctx.elicit` is **not** called); calls `ctx.elicit` normally
  in stateful mode. Optionally assert a wrapper (e.g. `_confirm_upgrade_write_action`) converts
  the raised error into a `ToolError`.

## 9. Process

Spec → implementation plan (`writing-plans`) → subagent-driven TDD with two-stage review →
PR to `tmunzer/mistmcp` `main`. Default-off behavior must remain unchanged; verify with the
existing suite plus the new tests.
