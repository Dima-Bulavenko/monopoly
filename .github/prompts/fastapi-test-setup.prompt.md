---
description: "Set up the full async test infrastructure for a FastAPI + SQLModel project. Creates conftest.py fixtures, configures pytest-asyncio, adds a test PostgreSQL service to docker-compose, and scaffolds the first test module."
agent: "agent"
argument-hint: "Describe the project layout or any deviations from defaults"
---

Set up a complete async test environment for this FastAPI + SQLModel project following the established conventions in this repository.

## Steps

### 1. Dev dependencies

Ensure these are present in `pyproject.toml` `[dependency-groups] dev`:

- `httpx` — async HTTP client for ASGI tests
- `pytest-asyncio` — async test support
- `pytest-mock` — `MockerFixture` for patching
- `freezegun` — time travel for time-dependent tests

Add any that are missing via `uv add --dev <package>`.

### 2. pytest configuration

Add to `[tool.pytest.ini_options]` in `pyproject.toml`:

```toml
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "session"
asyncio_default_test_loop_scope = "session"
```

### 3. Test PostgreSQL service in docker-compose.yml

Add a `postgres-test` service. Choose a host port not already bound (check with `ss -tlnp`). Use a separate database name (e.g. `monopoly_test`) so it never touches production data:

```yaml
postgres-test:
  image: postgres:17-alpine
  container_name: <project>-postgres-test
  ports:
    - "<free_port>:5432"
  environment:
    POSTGRES_USER: <user>
    POSTGRES_PASSWORD: <password>
    POSTGRES_DB: <project>_test
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U <user>"]
    interval: 5s
    timeout: 3s
    retries: 5
```

### 4. tests/conftest.py — global fixtures

Create `tests/conftest.py` with these four fixtures and nothing else:

**`test_rsa_keys` (session-scoped)** — generates an RSA-2048 key pair once per run using `cryptography`:

```python
@pytest.fixture(scope="session")
def test_rsa_keys() -> tuple[str, str]:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()
    return private_pem, public_pem
```

**`test_engine` (session-scoped)** — connects to the test DB, runs `create_all` before first test, `drop_all` + `dispose` after last:

```python
TEST_DATABASE_URL = "postgresql+asyncpg://<user>:<password>@localhost:<port>/<db>_test"

@pytest.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    await engine.dispose()
```

Import all SQLModel table models at module level so `SQLModel.metadata` sees them before `create_all`.

**`db_session` (function-scoped)** — wraps each test in a transaction + savepoint that is rolled back unconditionally:

```python
@pytest.fixture
async def db_session(test_engine):
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

**`test_app` (function-scoped, `autouse=True`)** — overrides `get_session` with `db_session` and yields the FastAPI app:

```python
@pytest.fixture(autouse=True)
async def test_app(db_session):
    from app.main import app
    from <path>.postgres import get_session

    async def _override():
        yield db_session

    app.dependency_overrides[get_session] = _override
    yield app
    app.dependency_overrides.clear()
```

### 5. Domain conftest.py — when needed

Create `tests/<domain>/conftest.py` when two or more test modules in that domain share fixtures. Typical contents:

- **`make_<domain>_service` factory** — wires real infrastructure against `db_session` and `test_rsa_keys`, returns a callable accepting optional override kwargs.
- **`registered_<entity>` fixture** — registers/creates a canonical entity via the HTTP API and returns its credentials/tokens as a dict.

### 6. First test module

For the first endpoint to test, create `tests/<domain>/test_<endpoint_name>_endpoint.py` containing:

- `ENDPOINT = "/path/to/endpoint"` module constant
- `http_client` fixture using `ASGITransport(app=test_app)` — defined in the module, not in conftest
- `make_<resource>_body` fixture returning a factory with `**overrides`
- A shared response fixture for the main happy-path call if multiple tests assert on it
- Test groups: happy path, business errors, validation (422)

### 7. Verify

```sh
docker compose up -d postgres-test
uv run pytest tests/ --collect-only   # confirm collection, no import errors
uv run pytest tests/ -v               # confirm all pass
```
