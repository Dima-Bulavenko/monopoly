---
description: "Use when writing, adding, or modifying backend tests. Covers pytest fixtures, conftest hierarchy, async tests, database isolation, HTTP client setup, mocking, and test module naming conventions."
applyTo: "backend/tests/**"
---

# Backend Testing Conventions

## Stack

- **pytest** with `asyncio_mode = "auto"` — all tests and fixtures are async by default, no `@pytest.mark.asyncio` needed.
- **httpx `AsyncClient` + `ASGITransport`** for HTTP endpoint tests — no real server.
- **pytest-mock (`MockerFixture`)** for mocking external dependencies (OAuth providers, etc.).
- **freezegun** for time-dependent logic.
- **SQLModel + asyncpg** against a real PostgreSQL test database (port 5434, `monopoly_test`).

## File Naming

- One test module per endpoint: `test_<endpoint_name>_endpoint.py`.
- Place all auth endpoint tests under `tests/auth/`.
- Example: `POST /auth/register` → `tests/auth/test_register_endpoint.py`.

## conftest Hierarchy

```
tests/
    conftest.py          ← global: DB engine/session, test_app autouse
    auth/
        conftest.py      ← domain: registered_user
        test_*.py
```

- Add a domain-level `conftest.py` (e.g. `tests/auth/conftest.py`) when two or more modules in that domain share fixtures.
- Never put domain-specific fixtures (e.g. `registered_user`) in the global `tests/conftest.py`.

## Global conftest.py (`tests/conftest.py`)

Must contain exactly these fixtures — do not add feature-specific logic here:

| Fixture | Scope | Purpose |
|---|---|---|
| `test_rsa_keys` | `session` | Generates RSA-2048 key pair once per run |
| `test_engine` | `session` | Creates tables on startup, drops on teardown |
| `db_session` | `function` | Per-test rolled-back transaction (savepoint isolation) |
| `test_app` | `function`, `autouse=True` | Overrides `get_session` with `db_session`; yields the FastAPI `app` |

### db_session isolation pattern

```python
async with test_engine.connect() as conn:
    await conn.begin()
    async with AsyncSession(
        bind=conn,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    ) as session:
        yield session
    await conn.rollback()
```

### test_app override pattern

Override the **session dependency** (`get_session`), not a higher-level service. This lets the real DI wiring run while only the DB connection is swapped:

```python
@pytest.fixture(autouse=True)
async def test_app(db_session):
    from app.main import app
    from app.auth.infrastructure.db.postgres import get_session

    async def _override():
        yield db_session

    app.dependency_overrides[get_session] = _override
    yield app
    app.dependency_overrides.clear()
```

## Per-Module Fixtures

Every endpoint test module defines its own `http_client` fixture. This lets each module apply its own transport settings, base URL, or default headers independently.

```python
@pytest.fixture
async def http_client(test_app) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://test",
    ) as client:
        yield client
```

## ENDPOINT Constant

Every test module must declare a module-level `ENDPOINT` constant instead of repeating the URL string:

```python
ENDPOINT = "/auth/register"
```

## Request Body Factories

Use a `make_<resource>_body` fixture that returns a factory function accepting `**overrides`. This avoids repetition and makes field-level variations explicit:

```python
@pytest.fixture
def make_register_body():
    def factory(**overrides):
        return {"email": "alice@example.com", "password": "Str0ng!Pass", "display_name": "Alice", **overrides}
    return factory
```

## Shared Response Fixtures

Extract the repeated "happy-path POST" into a fixture when multiple tests assert on the same response:

```python
@pytest.fixture
async def register_response(http_client, make_register_body):
    return await http_client.post(ENDPOINT, json=make_register_body())
```

## Cookie Handling

Pass cookies via the `Cookie` header, **not** the deprecated `cookies=` kwarg on `AsyncClient.post()`:

```python
# correct
await http_client.post(ENDPOINT, headers={"Cookie": f"refresh_token={token}"})

# wrong — triggers DeprecationWarning
await http_client.post(ENDPOINT, cookies={"refresh_token": token})
```

## Mocking External Providers (OAuth)

Patch the provider factory at the **router import path**, not the class itself. Use `mocker.patch` with an `AsyncMock`:

```python
_PROVIDER_PATH = "app.auth.api.router.get_google_provider"

@pytest.fixture
def mock_google_provider(mocker, google_identity):
    provider = AsyncMock()
    provider.verify_id_token.return_value = google_identity
    mocker.patch(_PROVIDER_PATH, return_value=provider)
    return provider
```

## Test Categories per Endpoint

Cover at minimum:

1. **Happy path** — correct status code, response body shape, cookie presence/attributes.
2. **Business errors** — domain exceptions mapped to correct HTTP status codes (401, 409, etc.) with `detail` in response.
3. **Validation** — missing/invalid required fields → 422.
4. **Side-effects** — e.g. token rotation revokes old token, logout makes refresh fail.
