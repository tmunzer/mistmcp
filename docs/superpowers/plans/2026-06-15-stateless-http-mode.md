# Stateless HTTP Transport Mode Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an opt-in stateless HTTP transport (`MISTMCP_STATELESS` / `--stateless`) so an already-connected MCP client survives a server restart, with default-off behavior byte-for-byte unchanged.

**Architecture:** When `stateless` + `transport=http`, serve via `mcp_server.http_app(stateless_http=True)` under `uvicorn` (fresh transport per request, no session). Because `on_initialize` state does not carry across stateless requests, write-tool visibility is resolved at build time in `create_mcp_server()`, the DANGER-ZONE elicitation bypass is set request-scoped in `on_call_tool`, and `config_elicitation_handler` fails closed in stateless. A startup gate refuses the one combo that needs in-band elicitation.

**Tech Stack:** Python 3.10–3.13, fastmcp 3.4.2, mcp 1.27.2, uvicorn 0.49.0, pytest (`asyncio_mode=auto`).

**Reference spec:** `docs/superpowers/specs/2026-06-15-stateless-http-mode-design.md`

---

## Conventions for every task

- **Run a single test** (avoids the repo-wide `--cov-fail-under=30` gate firing on a partial run):
  `uv run python -m pytest <path>::<TestClass>::<test> -v --no-cov`
- **Run a whole new/edited test file:** `uv run python -m pytest <path> -v --no-cov`
- **Final full suite** (Task 7 / end): `uv run python -m pytest` (coverage gate applies).
- **Lint after code changes:** `uv run ruff format <files>` then `uv run ruff check <files>`.
- Every commit message ends with the trailer:
  `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`
- The global `config` singleton (`mistmcp.config.config`) leaks across tests. New tests either
  use a **fresh `ServerConfig(...)`**, `monkeypatch.setattr(config, ...)` (auto-reverts), or
  explicitly reset the field they set. Follow the pattern shown in each task.
- **Task order matters.** `start()` gains its `stateless` param (Task 5) *before* the coupled
  `load_env_var`/`main()` rewrite (Task 6); each intermediate state keeps the full suite green.

## File map

| File | Change |
|---|---|
| `src/mistmcp/config.py` | Add `stateless` field; add `ConfigurationError`; add `validate_stateless_config()` |
| `src/mistmcp/elicitation_processor.py` | Add `ElicitationUnavailableError`; import `config`; add stateless fail-closed guard |
| `src/mistmcp/server.py` | Remove module-level write transform; add `_PROTECTED_WRITE_TAGS`, `_write_visible_tags()`, `_configure_write_visibility()`; call it in `create_mcp_server()` |
| `src/mistmcp/elicitation_middleware.py` | Add `on_call_tool` (request-scoped DANGER-ZONE bypass) |
| `src/mistmcp/__main__.py` | `start()` threading/guard/validate/log + launch branch + `_run_stateless_http()`; `load_env_var` env parse + 9-tuple; `main()` CLI flag + 9-tuple + `ConfigurationError`→exit(2) |
| `README.md` | `--stateless` option; `MISTMCP_STATELESS` / `MISTMCP_DISABLE_ELICITATION` rows; "Stateless HTTP mode" subsection |
| `tests/test_config.py` | New `TestStatelessConfig`, `TestValidateStatelessConfig` |
| `tests/test_elicitation_processor.py` | **New file** — guard tests |
| `tests/test_server.py` | New `TestWriteVisibleTags`, `TestConfigureWriteVisibility` |
| `tests/test_elicitation_middleware.py` | Extend `FakeFastMCPContext`; new `on_call_tool` tests |
| `tests/test_main.py` | New stateless start/launch tests (Task 5); main CLI/exit tests + fix 3 assertions (Task 6) |
| `tests/test_env_loading.py` | New stateless/disable-elicitation parse tests; fix 5 unpackings to 9-tuple (Task 6) |

---

## Task 1: Config field, `ConfigurationError`, and `validate_stateless_config`

**Files:**
- Modify: `src/mistmcp/config.py`
- Test: `tests/test_config.py`

- [ ] **Step 1: Write the failing tests**

Replace the import line at the top of `tests/test_config.py` with:

```python
import pytest

from mistmcp.config import (
    ConfigurationError,
    ServerConfig,
    validate_stateless_config,
)
```

Append (after the existing `TestServerConfig` class):

```python
class TestStatelessConfig:
    """Test the stateless config field"""

    def test_stateless_defaults_false(self) -> None:
        assert ServerConfig().stateless is False

    def test_stateless_can_be_set(self) -> None:
        assert ServerConfig(stateless=True).stateless is True


class TestValidateStatelessConfig:
    """Test validate_stateless_config refusal matrix"""

    def test_noop_when_not_stateless(self) -> None:
        # Otherwise-refused combo, but stateless=False -> never raises
        cfg = ServerConfig(
            transport_mode="http", enable_write_tools=True,
            disable_elicitation=False, stateless=False)
        validate_stateless_config(cfg)  # must not raise

    def test_refuses_http_write_without_disable(self) -> None:
        cfg = ServerConfig(
            transport_mode="http", enable_write_tools=True,
            disable_elicitation=False, stateless=True)
        with pytest.raises(ConfigurationError):
            validate_stateless_config(cfg)

    def test_allows_http_write_with_disable(self) -> None:
        cfg = ServerConfig(
            transport_mode="http", enable_write_tools=True,
            disable_elicitation=True, stateless=True)
        validate_stateless_config(cfg)  # must not raise

    def test_allows_http_readonly(self) -> None:
        cfg = ServerConfig(
            transport_mode="http", enable_write_tools=False,
            disable_elicitation=False, stateless=True)
        validate_stateless_config(cfg)  # must not raise

    def test_allows_stdio_even_with_write(self) -> None:
        cfg = ServerConfig(
            transport_mode="stdio", enable_write_tools=True,
            disable_elicitation=False, stateless=True)
        validate_stateless_config(cfg)  # must not raise (combo needs http)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run python -m pytest tests/test_config.py -v --no-cov`
Expected: FAIL — `ImportError: cannot import name 'ConfigurationError'`.

- [ ] **Step 3: Implement in `src/mistmcp/config.py`**

Add the `stateless` parameter/attribute to `ServerConfig.__init__` (insert `stateless` after `log_file`):

```python
    def __init__(
        self,
        transport_mode: str = "stdio",
        debug: bool = False,
        enable_write_tools: bool = False,
        disable_elicitation: bool = False,
        response_format: str = "json",
        log_file: str | None = None,
        stateless: bool = False,
    ) -> None:
        self.transport_mode: str = transport_mode
        self.mist_apitoken: str = ""
        self.mist_host: str = ""
        self.debug = debug
        self.enable_write_tools = enable_write_tools
        self.disable_elicitation = disable_elicitation
        self.response_format = response_format
        self.log_file: str | None = log_file
        self.stateless = stateless
```

Add, above the `config = ServerConfig()` singleton line:

```python
class ConfigurationError(Exception):
    """Raised when the server configuration is invalid and startup must be refused."""


def validate_stateless_config(config: "ServerConfig") -> None:
    """Refuse stateless when it collides with in-band elicitation.

    Stateless HTTP has no live session and no server->client channel, so the
    ctx.elicit() handshake cannot work. The only config that needs that handshake is
    write tools enabled over HTTP without disable_elicitation. Everything else
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

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run python -m pytest tests/test_config.py -v --no-cov`
Expected: PASS.

- [ ] **Step 5: Lint and commit**

```bash
uv run ruff format src/mistmcp/config.py tests/test_config.py
uv run ruff check src/mistmcp/config.py tests/test_config.py
git add src/mistmcp/config.py tests/test_config.py
git commit -m "$(printf 'feat: add stateless config field and validate_stateless_config\n\nCo-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>')"
```

---

## Task 2: Fail-closed elicitation guard

**Files:**
- Modify: `src/mistmcp/elicitation_processor.py`
- Test: `tests/test_elicitation_processor.py` (new)

- [ ] **Step 1: Write the failing tests**

Create `tests/test_elicitation_processor.py`:

```python
"""Tests for the elicitation handler's stateless fail-closed guard"""

import pytest

from mistmcp.config import config
from mistmcp.elicitation_processor import (
    ElicitationUnavailableError,
    config_elicitation_handler,
)


class FakeCtx:
    def __init__(self, state=None, elicit_exc=None) -> None:
        self._state = state or {}
        self._elicit_exc = elicit_exc
        self.elicit_calls: list = []

    async def get_state(self, key):
        return self._state.get(key)

    async def elicit(self, message, response_type=None):
        self.elicit_calls.append((message, response_type))
        if self._elicit_exc is not None:
            raise self._elicit_exc
        return None


async def test_auto_accepts_when_state_true(monkeypatch) -> None:
    monkeypatch.setattr(config, "stateless", True)
    monkeypatch.setattr(config, "transport_mode", "http")
    ctx = FakeCtx(state={"disable_elicitation": True})

    result = await config_elicitation_handler("msg", ctx)

    assert result.action == "accept"
    assert ctx.elicit_calls == []  # state check returns before the guard


async def test_raises_unavailable_in_stateless_http(monkeypatch) -> None:
    monkeypatch.setattr(config, "stateless", True)
    monkeypatch.setattr(config, "transport_mode", "http")
    ctx = FakeCtx(state={})  # disable_elicitation not set

    with pytest.raises(ElicitationUnavailableError):
        await config_elicitation_handler("msg", ctx)

    assert ctx.elicit_calls == []  # guard fired BEFORE ctx.elicit


async def test_calls_elicit_in_stateful(monkeypatch) -> None:
    monkeypatch.setattr(config, "stateless", False)
    monkeypatch.setattr(config, "transport_mode", "http")
    sentinel = RuntimeError("elicit-reached")
    ctx = FakeCtx(state={}, elicit_exc=sentinel)

    # In stateful mode the guard must NOT fire; ctx.elicit is reached (and here
    # raises our sentinel, proving the handler proceeded past the guard).
    with pytest.raises(RuntimeError, match="elicit-reached"):
        await config_elicitation_handler("msg", ctx)

    assert len(ctx.elicit_calls) == 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run python -m pytest tests/test_elicitation_processor.py -v --no-cov`
Expected: FAIL — `ImportError: cannot import name 'ElicitationUnavailableError'`.

- [ ] **Step 3: Implement in `src/mistmcp/elicitation_processor.py`**

Add the config import alongside the existing logger import near the top:

```python
from mistmcp.config import config
from mistmcp.logger import logger
```

Add the exception class above `config_elicitation_handler`:

```python
class ElicitationUnavailableError(RuntimeError):
    """Raised when elicitation is required but cannot be performed (stateless HTTP has
    no server->client channel). The tool wrappers convert this into a clean ToolError."""
```

Insert the guard in `config_elicitation_handler`, immediately AFTER the `get_state` auto-accept block and BEFORE the `ctx.elicit` call:

```python
async def config_elicitation_handler(message, ctx: Context):

    if await ctx.get_state("disable_elicitation") is True:
        logger.debug(
            "Elicitation middleware: elicitation is disabled for this client, automatically accepting without prompting"
        )
        return ElicitResult(action="accept")

    if config.stateless and config.transport_mode == "http":
        # No live session / server->client channel in stateless: in-band elicitation
        # cannot complete. Fail closed deterministically instead of calling ctx.elicit().
        raise ElicitationUnavailableError(
            "In-band elicitation is unavailable in stateless HTTP mode; this action "
            "requires disable_elicitation (DANGER ZONE) or a stateful transport."
        )

    logger.debug(
        "Elicitation middleware: prompting user with message: %s",
        message,
    )
    result = await ctx.elicit(message, response_type=None)
    ...  # rest of the function unchanged
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run python -m pytest tests/test_elicitation_processor.py tests/test_elicitation_middleware.py -v --no-cov`
Expected: PASS (new guard tests AND the existing `test_stdio_disable_elicitation_sets_state_and_skips_prompt`, which reaches the auto-accept return before the guard).

- [ ] **Step 5: Lint and commit**

```bash
uv run ruff format src/mistmcp/elicitation_processor.py tests/test_elicitation_processor.py
uv run ruff check src/mistmcp/elicitation_processor.py tests/test_elicitation_processor.py
git add src/mistmcp/elicitation_processor.py tests/test_elicitation_processor.py
git commit -m "$(printf 'feat: fail closed in config_elicitation_handler under stateless http\n\nCo-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>')"
```

---

## Task 3: Build-time write-tool visibility centralization

**Files:**
- Modify: `src/mistmcp/server.py`
- Test: `tests/test_server.py`

- [ ] **Step 1: Write the failing tests**

Replace the imports at the top of `tests/test_server.py` with:

```python
from unittest.mock import patch

from fastmcp import FastMCP

from mistmcp.config import ServerConfig
from mistmcp.server import (
    _PROTECTED_WRITE_TAGS,
    _configure_write_visibility,
    _write_visible_tags,
    create_mcp_server,
    mcp,
)
```

Append these classes to `tests/test_server.py`:

```python
def _build_fresh_mcp() -> FastMCP:
    m = FastMCP(name="test_visibility")

    @m.tool(name="w_tool", tags={"write"})
    def w_tool() -> str:
        return "w"

    @m.tool(name="wd_tool", tags={"write_delete"})
    def wd_tool() -> str:
        return "wd"

    @m.tool(name="up_tool", tags={"utilities_upgrade"})
    def up_tool() -> str:
        return "up"

    @m.tool(name="read_tool", tags={"info"})
    def read_tool() -> str:
        return "r"

    return m


async def _visible_names(m: FastMCP) -> set[str]:
    tools = await m.list_tools()  # public path applies Visibility transforms
    return {t.name for t in tools}


class TestWriteVisibleTags:
    def test_protected_tags_are_write_and_write_delete(self) -> None:
        assert _PROTECTED_WRITE_TAGS == {"write", "write_delete"}

    def test_readonly_hides_all(self) -> None:
        cfg = ServerConfig(enable_write_tools=False, disable_elicitation=False)
        assert _write_visible_tags(cfg) == set()

    def test_danger_zone_shows_write_only(self) -> None:
        cfg = ServerConfig(enable_write_tools=True, disable_elicitation=True)
        assert _write_visible_tags(cfg) == {"write"}

    def test_write_without_disable_shows_nothing_at_build(self) -> None:
        cfg = ServerConfig(enable_write_tools=True, disable_elicitation=False)
        assert _write_visible_tags(cfg) == set()


class TestConfigureWriteVisibility:
    async def test_readonly_hides_write_and_write_delete(self) -> None:
        m = _build_fresh_mcp()
        _configure_write_visibility(m, ServerConfig(enable_write_tools=False))
        visible = await _visible_names(m)
        assert "w_tool" not in visible
        assert "wd_tool" not in visible
        assert "up_tool" in visible  # utilities_upgrade untouched
        assert "read_tool" in visible

    async def test_danger_zone_shows_write_hides_write_delete(self) -> None:
        m = _build_fresh_mcp()
        _configure_write_visibility(
            m, ServerConfig(enable_write_tools=True, disable_elicitation=True))
        visible = await _visible_names(m)
        assert "w_tool" in visible
        assert "wd_tool" not in visible
        assert "up_tool" in visible

    async def test_idempotent_last_config_wins(self) -> None:
        m = _build_fresh_mcp()
        _configure_write_visibility(
            m, ServerConfig(enable_write_tools=True, disable_elicitation=True))
        _configure_write_visibility(m, ServerConfig(enable_write_tools=False))
        visible = await _visible_names(m)
        assert "w_tool" not in visible
        assert "wd_tool" not in visible

    async def test_idempotent_last_config_wins_reverse(self) -> None:
        m = _build_fresh_mcp()
        _configure_write_visibility(m, ServerConfig(enable_write_tools=False))
        _configure_write_visibility(
            m, ServerConfig(enable_write_tools=True, disable_elicitation=True))
        visible = await _visible_names(m)
        assert "w_tool" in visible
        assert "wd_tool" not in visible
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run python -m pytest tests/test_server.py -v --no-cov`
Expected: FAIL — `ImportError: cannot import name '_PROTECTED_WRITE_TAGS'`.

- [ ] **Step 3: Implement in `src/mistmcp/server.py`**

Delete the module-level transform and its comment (currently lines 197–200):

```python
# Write tools are disabled by default and enabled per-session by
# ElicitationMiddleware during initialization when the client declares
# elicitation support or explicitly sends X-Disable-Elicitation: true.
mcp.add_transform(Visibility(False, tags={"write"}, components={"tool"}))
```

Add the resolver functions above `def create_mcp_server`:

```python
_PROTECTED_WRITE_TAGS = {"write", "write_delete"}


def _write_visible_tags(config: ServerConfig) -> set[str]:
    """Protected write tags that should be visible at build time for this config.

    Authoritative in stateless mode; a behavior-neutral floor in stateful mode, where
    ElicitationMiddleware.on_initialize re-resolves write/write_delete per session.
    """
    if config.enable_write_tools and config.disable_elicitation:
        return {"write"}  # DANGER ZONE: update only, never write_delete
    return set()  # read-only / elicitation-capable: hide both at build time


def _configure_write_visibility(mcp_server: FastMCP, config: ServerConfig) -> None:
    """Install a deterministic hide-all-then-show-visible transform sequence for the
    protected write tags. FastMCP Visibility marks are later-wins, so the EFFECTIVE
    visibility equals this call's resolution even when called repeatedly on the reused
    module singleton (the transform list grows by 1-2 entries per call; create_mcp_server
    runs once per process)."""
    visible = _write_visible_tags(config)
    mcp_server.add_transform(
        Visibility(False, tags=_PROTECTED_WRITE_TAGS, components={"tool"}))
    if visible:
        mcp_server.add_transform(
            Visibility(True, tags=visible, components={"tool"}))
```

Call it inside `create_mcp_server` (after `_load_tools`, before the debug log):

```python
def create_mcp_server(config: ServerConfig) -> FastMCP:
    """Configure and return the MCP server with all tools loaded."""
    enabled_tools = _load_tools(config)

    _configure_write_visibility(mcp, config)

    logger.debug("MCP Server ready with %d tools", len(enabled_tools))

    return mcp
```

(`Visibility` is already imported at `server.py:16`; `ServerConfig` at `server.py:18`.)

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run python -m pytest tests/test_server.py -v --no-cov`
Expected: PASS (new visibility tests AND the existing `TestMcpInstance`/`TestCreateMcpServer` tests).

- [ ] **Step 5: Lint and commit**

```bash
uv run ruff format src/mistmcp/server.py tests/test_server.py
uv run ruff check src/mistmcp/server.py tests/test_server.py
git add src/mistmcp/server.py tests/test_server.py
git commit -m "$(printf 'feat: resolve write-tool visibility at build time in create_mcp_server\n\nCo-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>')"
```

---

## Task 4: `on_call_tool` request-scoped DANGER-ZONE bypass

**Files:**
- Modify: `src/mistmcp/elicitation_middleware.py`
- Test: `tests/test_elicitation_middleware.py`

- [ ] **Step 1: Extend the fake and write the failing tests**

In `tests/test_elicitation_middleware.py`, replace the `FakeFastMCPContext.__init__` and `set_state` so the fake accepts the `serializable` keyword and records calls (the rest of the class is unchanged):

```python
class FakeFastMCPContext:
    def __init__(self) -> None:
        self.state: dict[str, bool] = {}
        self.enabled_calls: list[dict[str, set[str]]] = []
        self.disabled_calls: list[dict[str, set[str]]] = []
        self.elicit_calls: list[tuple[str, None]] = []
        self.set_state_calls: list[tuple[str, bool, bool]] = []

    async def set_state(self, key: str, value: bool, *, serializable: bool = True) -> None:
        self.state[key] = value
        self.set_state_calls.append((key, value, serializable))
```

Append these tests to the same file:

```python
async def test_on_call_tool_sets_request_scoped_state_in_stateless_danger(
    monkeypatch,
) -> None:
    monkeypatch.setattr(config, "stateless", True)
    monkeypatch.setattr(config, "transport_mode", "http")
    monkeypatch.setattr(config, "enable_write_tools", True)
    monkeypatch.setattr(config, "disable_elicitation", True)

    fastmcp_context = FakeFastMCPContext()
    context = FakeMiddlewareContext(fastmcp_context)
    middleware = ElicitationMiddleware()

    async def call_next(_context):
        return "tool-result"

    result = await middleware.on_call_tool(context, call_next)

    assert result == "tool-result"
    assert fastmcp_context.state.get("disable_elicitation") is True
    # request-scoped: serializable must be False
    assert fastmcp_context.set_state_calls == [("disable_elicitation", True, False)]


async def test_on_call_tool_noop_when_not_stateless(monkeypatch) -> None:
    monkeypatch.setattr(config, "stateless", False)
    monkeypatch.setattr(config, "transport_mode", "http")
    monkeypatch.setattr(config, "enable_write_tools", True)
    monkeypatch.setattr(config, "disable_elicitation", True)

    fastmcp_context = FakeFastMCPContext()
    context = FakeMiddlewareContext(fastmcp_context)
    middleware = ElicitationMiddleware()

    async def call_next(_context):
        return "tool-result"

    result = await middleware.on_call_tool(context, call_next)

    assert result == "tool-result"
    assert fastmcp_context.set_state_calls == []
    assert "disable_elicitation" not in fastmcp_context.state
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run python -m pytest tests/test_elicitation_middleware.py -v --no-cov`
Expected: FAIL — `AttributeError: 'ElicitationMiddleware' object has no attribute 'on_call_tool'`.

- [ ] **Step 3: Implement in `src/mistmcp/elicitation_middleware.py`**

Add a new method to the `ElicitationMiddleware` class (after `on_initialize`):

```python
    async def on_call_tool(self, context, call_next):
        """In stateless HTTP, on_initialize state does not carry to this tool call.
        Set the DANGER-ZONE auto-accept flag request-scoped so config_elicitation_handler
        accepts for this call only (no leak into the session store). Gated on
        config.stateless so the stateful path is literally unchanged."""
        ctx = context.fastmcp_context
        if (
            config.stateless
            and config.transport_mode == "http"
            and config.enable_write_tools
            and config.disable_elicitation
            and ctx is not None
        ):
            await ctx.set_state("disable_elicitation", True, serializable=False)
        return await call_next(context)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run python -m pytest tests/test_elicitation_middleware.py -v --no-cov`
Expected: PASS (new `on_call_tool` tests AND the existing `on_initialize` test, unaffected by the backward-compatible `set_state` signature).

- [ ] **Step 5: Lint and commit**

```bash
uv run ruff format src/mistmcp/elicitation_middleware.py tests/test_elicitation_middleware.py
uv run ruff check src/mistmcp/elicitation_middleware.py tests/test_elicitation_middleware.py
git add src/mistmcp/elicitation_middleware.py tests/test_elicitation_middleware.py
git commit -m "$(printf 'feat: add on_call_tool request-scoped elicitation bypass for stateless danger zone\n\nCo-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>')"
```

---

## Task 5: `start()` threading + stateless launch path

**Files:**
- Modify: `src/mistmcp/__main__.py`
- Test: `tests/test_main.py`

> Why before Task 6: `start()` must accept `stateless` before `main()` can pass it. `main()` and `load_env_var` are left unchanged here, so the full suite stays green (`main()` still calls `start()` with 8 positional args ⇒ `stateless` defaults to `False`).

- [ ] **Step 1: Write the failing tests**

Replace the imports at the top of `tests/test_main.py` with:

```python
from unittest.mock import Mock, patch

import pytest

from mistmcp.__main__ import _run_stateless_http, main, start
from mistmcp.config import ConfigurationError, config
```

Append this class to `tests/test_main.py`:

```python
class TestStatelessStart:
    """Test stateless threading and launch path in start()"""

    @patch("mistmcp.__main__._run_stateless_http")
    @patch("mistmcp.__main__.create_mcp_server")
    def test_http_stateless_uses_stateless_launch(
        self, mock_create, mock_run_stateless
    ) -> None:
        mock_server = Mock()
        mock_create.return_value = mock_server

        start("http", "127.0.0.1", 8000, enable_write_tools=False,
              disable_elicitation=False, stateless=True)

        mock_run_stateless.assert_called_once_with(mock_server, "127.0.0.1", 8000)
        mock_server.run.assert_not_called()
        config.stateless = False  # reset global

    @patch("mistmcp.__main__._run_stateless_http")
    @patch("mistmcp.__main__.create_mcp_server")
    def test_http_non_stateless_uses_run(
        self, mock_create, mock_run_stateless
    ) -> None:
        mock_server = Mock()
        mock_create.return_value = mock_server

        start("http", "127.0.0.1", 8000, stateless=False)

        mock_run_stateless.assert_not_called()
        mock_server.run.assert_called_once_with(
            transport="http", host="127.0.0.1", port=8000)

    @patch("mistmcp.__main__.create_mcp_server")
    def test_stateless_stdio_downgrades_with_warning(
        self, mock_create, capsys
    ) -> None:
        mock_server = Mock()
        mock_create.return_value = mock_server

        start("stdio", "127.0.0.1", 8000, stateless=True)

        captured = capsys.readouterr()
        assert "stateless applies only to http" in captured.err
        mock_server.run.assert_called_once_with()
        config.stateless = False  # reset global

    def test_start_does_not_swallow_config_error(self) -> None:
        with pytest.raises(ConfigurationError):
            start("http", "127.0.0.1", 8000, enable_write_tools=True,
                  disable_elicitation=False, stateless=True)
        config.stateless = False  # reset global

    @patch("uvicorn.run")
    def test_run_stateless_http_builds_stateless_app(self, mock_uvicorn_run) -> None:
        mock_server = Mock()
        app = mock_server.http_app.return_value

        _run_stateless_http(mock_server, "0.0.0.0", 9000)

        # no event_store kwarg — only stateless_http=True
        mock_server.http_app.assert_called_once_with(stateless_http=True)
        mock_uvicorn_run.assert_called_once_with(
            app, host="0.0.0.0", port=9000, lifespan="on",
            timeout_graceful_shutdown=2, ws="websockets-sansio")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run python -m pytest tests/test_main.py::TestStatelessStart -v --no-cov`
Expected: FAIL — `ImportError: cannot import name '_run_stateless_http'`.

- [ ] **Step 3: Implement in `src/mistmcp/__main__.py`**

Update the config import at the top of the file (do NOT add `ConfigurationError` yet — it is unused until Task 6 and ruff will flag it):

```python
from mistmcp.config import config, validate_stateless_config
```

Add the launch helper directly above `def start(`:

```python
def _run_stateless_http(mcp_server, host: str, port: int) -> None:
    """Serve via http_app(stateless_http=True): the SDK builds a fresh transport per
    request, so there is no session id to go stale on a server restart. We pass no
    event_store; in stateless mode the SDK's per-request transport uses event_store=None
    regardless (the resumable GET stream is dropped)."""
    import uvicorn

    app = mcp_server.http_app(stateless_http=True)
    uvicorn.run(
        app,
        host=host,
        port=port,
        lifespan="on",
        timeout_graceful_shutdown=2,
        ws="websockets-sansio",
    )
```

Replace `start()` with this full version (adds the `stateless` param, downgrade guard, validation, INFO log, and launch branch):

```python
def start(
    transport_mode: str,
    mcp_host: str,
    mcp_port: int,
    debug: bool = False,
    enable_write_tools: bool = False,
    disable_elicitation: bool = False,
    response_format: str = "json",
    log_file: str | None = None,
    stateless: bool = False,
) -> None:
    # Update global config
    config.transport_mode = transport_mode
    config.debug = debug
    config.enable_write_tools = enable_write_tools
    config.disable_elicitation = disable_elicitation
    config.response_format = response_format
    config.log_file = log_file
    config.stateless = stateless

    setup_logging(debug=debug, log_file=log_file)

    # stateless only applies to http
    if config.stateless and transport_mode != "http":
        logger.warning(
            "MISTMCP_STATELESS / --stateless is set but transport is %s; stateless "
            "applies only to http — ignoring.",
            transport_mode,
        )
        config.stateless = False

    # Refuse incompatible config BEFORE the broad try below, so it cannot be swallowed.
    validate_stateless_config(config)

    logger.info("Starting Mist MCP Server — transport: %s", transport_mode)
    logger.debug("  MIST_HOST: %s", config.mist_host)
    logger.debug("  RESPONSE_FORMAT: %s", config.response_format)
    logger.debug("  ENABLE_WRITE_TOOLS: %s", config.enable_write_tools)
    logger.debug("  DISABLE_ELICITATION: %s", config.disable_elicitation)
    if transport_mode == "http":
        logger.debug("  MCP_HOST: %s", mcp_host)
        logger.debug("  MCP_PORT: %s", mcp_port)
    if config.stateless:
        logger.info(
            "Stateless HTTP mode active: fresh transport per request, so an "
            "already-connected MCP client survives a server restart. Server->client "
            "push (notifications/elicitation) is disabled; in-band elicitation is "
            "unavailable, so destructive utility/upgrade actions require "
            "disable_elicitation (DANGER ZONE) or are refused."
        )

    try:
        mcp_server = create_mcp_server(config)

        if transport_mode == "http":
            if config.stateless:
                _run_stateless_http(mcp_server, mcp_host, mcp_port)
            else:
                mcp_server.run(transport="http", host=mcp_host, port=mcp_port)
        else:
            mcp_server.run()

    except KeyboardInterrupt:
        logger.info("Mist MCP Server stopped by user")

    except Exception as e:
        logger.error("Mist MCP Error: %s", e)
        if debug:
            import traceback

            traceback.print_exc()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run python -m pytest tests/test_main.py -v --no-cov`
Expected: PASS — `TestStatelessStart` passes; existing `TestStart` and `TestMain` tests still pass (`main()` unchanged ⇒ still calls `start()` with 8 positional args; `stateless` defaults `False`; validate is a no-op).

- [ ] **Step 5: Lint and commit**

```bash
uv run ruff format src/mistmcp/__main__.py tests/test_main.py
uv run ruff check src/mistmcp/__main__.py tests/test_main.py
git add src/mistmcp/__main__.py tests/test_main.py
git commit -m "$(printf 'feat: thread stateless into start() and add stateless http launch path\n\nCo-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>')"
```

---

## Task 6: `load_env_var` env parsing + `main()` CLI flag and fatal exit

These changes are coupled (the 9-tuple, the `--stateless` flag, and `main()`'s 9-unpack/pass-through must land together) and are done as one task.

**Files:**
- Modify: `src/mistmcp/__main__.py`
- Test: `tests/test_env_loading.py`, `tests/test_main.py`

- [ ] **Step 1: Write the failing tests AND fix existing assertions/unpackings**

**In `tests/test_env_loading.py`** — fix the 5 existing `load_env_var` unpackings to a 9-tuple (each gains one trailing `_`):

- `test_load_env_var_stdio_mode` (~line 91): `..., response_format, _ = load_env_var(` → `..., response_format, _, _ = load_env_var(`
- `test_load_env_var_http_mode` (~line 114): `..., response_format, _ = load_env_var(` → `..., response_format, _, _ = load_env_var(`
- `test_load_env_var_debug_variations` (~line 145): `_, _, _, debug, _, _, _, _ = load_env_var(` → `_, _, _, debug, _, _, _, _, _ = load_env_var(`
- `test_load_env_var_port_parsing` (~line 167): `_, _, mcp_port, _, _, _, _, _ = load_env_var(` → `_, _, mcp_port, _, _, _, _, _, _ = load_env_var(`
- `test_load_env_var_host_and_port_from_env` (~line 181): `_, mcp_host, mcp_port, _, _, _, _, _ = load_env_var(` → `_, mcp_host, mcp_port, _, _, _, _, _, _ = load_env_var(`

Then append to the `TestLoadEnvVar` class:

```python
    def test_load_env_var_returns_9_tuple(self) -> None:
        base_env = {"MIST_APITOKEN": "t", "MIST_HOST": "h"}
        with patch.dict(os.environ, base_env, clear=False):
            result = load_env_var(
                "stdio", None, None, False, False, False, None, None, False)
            assert len(result) == 9

    def test_load_env_var_stateless_parsing(self) -> None:
        test_cases = [
            ("true", True), ("TRUE", True), ("1", True), ("yes", True),
            ("false", False), ("0", False), ("", False),
        ]
        base_env = {"MIST_APITOKEN": "t", "MIST_HOST": "h"}
        for value, expected in test_cases:
            env = {**base_env, "MISTMCP_STATELESS": value}
            with patch.dict(os.environ, env, clear=False):
                result = load_env_var(
                    "http", None, None, False, False, False, None, None, False)
                assert result[8] == expected, f"Failed for MISTMCP_STATELESS='{value}'"

    def test_load_env_var_disable_elicitation_parsing(self) -> None:
        base_env = {"MIST_APITOKEN": "t", "MIST_HOST": "h"}
        env = {**base_env, "MISTMCP_DISABLE_ELICITATION": "true"}
        with patch.dict(os.environ, env, clear=False):
            result = load_env_var(
                "stdio", None, None, False, False, False, None, None, False)
            assert result[5] is True  # disable_elicitation
```

**In `tests/test_main.py`** — update the 3 existing `TestMain` assertions to include the trailing `stateless` argument (`False`):

- `test_main_default_args`: `...("stdio", "127.0.0.1", 8000, False, False, False, "json", None)` → `...("stdio", "127.0.0.1", 8000, False, False, False, "json", None, False)`
- `test_main_with_debug`: `...("stdio", "127.0.0.1", 8000, True, False, False, "json", None)` → `...("stdio", "127.0.0.1", 8000, True, False, False, "json", None, False)`
- `test_main_custom_host_and_port`: `...("http", "0.0.0.0", 9000, False, False, False, "json", None)` → `...("http", "0.0.0.0", 9000, False, False, False, "json", None, False)`

Then append to the `TestMain` class:

```python
    @patch("mistmcp.__main__.start")
    def test_main_stateless_flag(self, mock_start) -> None:
        with patch("sys.argv", ["mistmcp", "--transport", "http", "--stateless"]):
            main()
        mock_start.assert_called_once_with(
            "http", "127.0.0.1", 8000, False, False, False, "json", None, True)

    @patch("mistmcp.__main__.start", side_effect=ConfigurationError("bad combo"))
    def test_main_exits_2_on_config_error(self, mock_start) -> None:
        with patch(
            "sys.argv",
            ["mistmcp", "--transport", "http", "--stateless", "--enable-write-tools"],
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
        assert exc_info.value.code == 2
```

(`ConfigurationError` and `pytest` are already imported in `tests/test_main.py` from Task 5.)

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run python -m pytest tests/test_env_loading.py tests/test_main.py -v --no-cov`
Expected: FAIL — env tests pass 9 args / read `result[8]` (`TypeError`/`IndexError`); `test_main_stateless_flag` hits argparse `SystemExit(2)` on the unknown `--stateless`; updated assertions fail (`main()` still calls `start()` with 8 args).

- [ ] **Step 3: Implement in `src/mistmcp/__main__.py`**

Update the config import to add `ConfigurationError`:

```python
from mistmcp.config import ConfigurationError, config, validate_stateless_config
```

Change the `load_env_var` signature (add `stateless` last, update return annotation):

```python
def load_env_var(
    transport_mode: str | None,
    mcp_host: str | None,
    mcp_port: int | None,
    debug: bool,
    enable_write_tools: bool,
    disable_elicitation: bool,
    response_format: str | None,
    log_file: str | None,
    stateless: bool = False,
) -> tuple[str, str, int, bool, bool, bool, str, str | None, bool]:
```

In the `load_env_var` body, immediately after the existing `enable_write_tools` parse block, add the two new parses:

```python
    env_enable_write_tools = os.getenv(
        "MISTMCP_ENABLE_WRITE_TOOLS", str(enable_write_tools)
    )
    enable_write_tools = env_enable_write_tools.lower() in ("true", "1", "yes")

    env_disable_elicitation = os.getenv(
        "MISTMCP_DISABLE_ELICITATION", str(disable_elicitation)
    )
    disable_elicitation = env_disable_elicitation.lower() in ("true", "1", "yes")

    env_stateless = os.getenv("MISTMCP_STATELESS", str(stateless))
    stateless = env_stateless.lower() in ("true", "1", "yes")
```

Change the `load_env_var` return to include `stateless`:

```python
    return (
        transport_mode,
        mcp_host,
        mcp_port,
        debug,
        enable_write_tools,
        disable_elicitation,
        response_format,
        log_file,
        stateless,
    )
```

In `main()`, add the CLI argument (after the `--disable-elicitation` argument):

```python
    parser.add_argument(
        "--stateless",
        action="store_true",
        help="Serve HTTP statelessly (fresh transport per request) so the MCP client "
        "survives a server restart. HTTP only; incompatible with in-band elicitation. "
        "Loses server->client push (notifications/elicitation).",
    )
```

In `main()`, update the `load_env_var` unpacking + call to 9 elements and pass `args.stateless`:

```python
    (
        transport_mode,
        mcp_host,
        mcp_port,
        debug,
        enable_write_tools,
        disable_elicitation,
        response_format,
        log_file,
        stateless,
    ) = load_env_var(
        args.transport,
        args.host,
        args.port,
        args.debug,
        args.enable_write_tools,
        args.disable_elicitation,
        args.response_format,
        args.log_file,
        args.stateless,
    )
```

In `main()`, replace the `start(...)` call with a guarded version that exits non-zero on a refused config:

```python
    try:
        start(
            transport_mode,
            mcp_host,
            mcp_port,
            debug,
            enable_write_tools,
            disable_elicitation,
            response_format,
            log_file,
            stateless,
        )
    except ConfigurationError as exc:
        logger.error("Invalid configuration: %s", exc)
        raise SystemExit(2)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run python -m pytest tests/test_env_loading.py tests/test_main.py -v --no-cov`
Expected: PASS (all env-loading + all `TestStart`/`TestStatelessStart`/`TestMain` tests).

- [ ] **Step 5: Lint and commit**

```bash
uv run ruff format src/mistmcp/__main__.py tests/test_env_loading.py tests/test_main.py
uv run ruff check src/mistmcp/__main__.py tests/test_env_loading.py tests/test_main.py
git add src/mistmcp/__main__.py tests/test_env_loading.py tests/test_main.py
git commit -m "$(printf 'feat: add --stateless flag, env parsing, and fatal exit on invalid config\n\nCo-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>')"
```

---

## Task 7: README documentation + full-suite verification

**Files:**
- Modify: `README.md`
- Verify: whole test suite

- [ ] **Step 1: Add the `--stateless` CLI option**

In `README.md`, in the `OPTIONS:` block (after the `--disable-elicitation` line, ~line 65), add:

```
    --stateless             Only when transport==http, serve statelessly so clients survive a server restart (no server->client push)
```

- [ ] **Step 2: Add env-var rows**

In the **HTTP Mode** table (after the `MISTMCP_ENABLE_WRITE_TOOLS` row, ~line 104), add:

```
| MISTMCP_DISABLE_ELICITATION | No | DANGER ZONE! true/false (default: false) |
| MISTMCP_STATELESS | No | true/false (default: false) — survive server restart, no server->client push |
```

In the **STDIO Mode** table (after its `MISTMCP_ENABLE_WRITE_TOOLS` row, ~line 94), add:

```
| MISTMCP_DISABLE_ELICITATION | No | DANGER ZONE! true/false (default: false) |
```

- [ ] **Step 3: Add a "Stateless HTTP mode" subsection**

After the HTTP Mode `> **Note:**` line (~line 106), add (the `===STATELESS-FENCE===` markers below stand in for triple backticks — replace each with ``` when inserting):

```
### Stateless HTTP mode

Set `MISTMCP_STATELESS=true` (or `--stateless`) with `--transport http` to serve each
request on a fresh transport. There is no server session id to go stale, so an
already-connected MCP client survives a server restart without reconnecting.

Trade-offs:

- **No server→client push.** Notifications and in-band elicitation are disabled.
- **Writes require the DANGER ZONE.** Because elicitation can't prompt, write tools are
  only available with `--enable-write-tools` **and** `--disable-elicitation` (or
  `MISTMCP_DISABLE_ELICITATION=true`), which auto-accepts. Starting stateless + http +
  `--enable-write-tools` without `--disable-elicitation` is refused at startup.
- **Read-only stays safe.** Without write tools, destructive upgrade/utility actions
  fail closed with a clear error.

Example:

===STATELESS-FENCE===bash
uv run mistmcp --transport http --stateless                       # read-only, restart-safe
uv run mistmcp --transport http --stateless \
    --enable-write-tools --disable-elicitation                    # writes (DANGER ZONE)
===STATELESS-FENCE===
```

- [ ] **Step 4: Verify the full suite passes with coverage**

Run: `uv run python -m pytest`
Expected: PASS — all tests green, coverage ≥ 30% (the repo gate). If coverage dips below 30%, a test was likely skipped; re-check Tasks 1–6.

- [ ] **Step 5: Lint everything touched and commit**

```bash
uv run ruff format src/mistmcp tests
uv run ruff check src/mistmcp tests
git add README.md
git commit -m "$(printf 'docs: document stateless HTTP mode and new env vars\n\nCo-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>')"
```

---

## Final verification checklist

- [ ] `uv run python -m pytest` — full suite green, coverage ≥ 30%.
- [ ] `uv run ruff check src tests` — clean.
- [ ] `uv run ruff format --check src tests` — clean.
- [ ] Default-off behavior unchanged: `git diff main -- src/mistmcp` shows the only runtime change for `stateless=False` is the (behavior-neutral) build-time visibility move and the new, gated `on_call_tool`/guard branches.
- [ ] Manual smoke (optional): `uv run mistmcp --transport http --stateless` starts and logs the stateless INFO line; `uv run mistmcp --transport http --stateless --enable-write-tools` exits non-zero with the refusal message.
```
