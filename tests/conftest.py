"""Shared test fixtures.

Every test drives the app through one seam: HTTP requests via Starlette's
``TestClient`` against the real ASGI app, with the ``get_session`` dependency
overridden to a throwaway in-memory SQLite database created per test. Nothing
below reaches past that seam.
"""

from collections.abc import Callable, Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

import main
from auth import hash_password
from main import Account, Portfolio, Project, app, get_session

# One bcrypt hash, computed once, for accounts seeded straight into the DB for
# read-path tests (they never sign in, so the plaintext behind it is irrelevant).
SEED_PASSWORD_HASH = hash_password("seed-account-password")


@pytest.fixture(name="session")
def session_fixture() -> Iterator[Session]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Iterator[TestClient]:
    def get_session_override() -> Session:
        return session

    app.dependency_overrides[get_session] = get_session_override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


LogInClient = Callable[..., TestClient]


@pytest.fixture(name="logged_in_client")
def logged_in_client_fixture(client: TestClient) -> LogInClient:
    """Run an Account through the real signup then login routes and hand back the
    same client, now carrying the session cookie the app set. No auth stubbing:
    both routes are exercised and the returned cookie is what the tests use.
    """

    def _log_in(
        email: str = "owner@example.com",
        password: str = "password123",
    ) -> TestClient:
        signup = client.post(
            "/signup",
            data={"email": email, "password": password},
            follow_redirects=False,
        )
        assert signup.status_code == 303, signup.text
        client.post("/logout")
        login = client.post(
            "/login",
            data={"email": email, "password": password},
            follow_redirects=False,
        )
        assert login.status_code == 303, login.text
        return client

    return _log_in


SeedPortfolio = Callable[..., Portfolio]


@pytest.fixture(name="seed_portfolio")
def seed_portfolio_fixture(session: Session) -> SeedPortfolio:
    """Insert an Account + Portfolio (+ Projects) directly, for read-path setup.

    Write-path state (accounts, portfolios, projects that a later ticket exposes
    a route for) will be built through those routes; this helper exists only so
    the read path has something to render before those routes exist.
    """

    def _seed(
        *,
        title: str = "My Portfolio",
        display_name: str = "Ada Lovelace",
        email: str = "ada@example.com",
        contact_email: str | None = "contact@example.com",
        github: str | None = "https://github.com/ada",
        phone: str | None = "+33123456789",
        age: int = 36,
        projects: list[dict] | None = None,
    ) -> Portfolio:
        account = Account(
            email=email,
            password_hash=SEED_PASSWORD_HASH,
            display_name=display_name,
            age=age,
            contact_email=contact_email,
            github=github,
            phone=phone,
        )
        session.add(account)
        session.commit()
        session.refresh(account)

        portfolio = Portfolio(account_id=account.account_id, title=title)
        session.add(portfolio)
        session.commit()
        session.refresh(portfolio)

        for fields in projects or []:
            session.add(Project(portfolio_id=portfolio.portfolio_id, **fields))
        session.commit()
        session.refresh(portfolio)
        return portfolio

    return _seed
