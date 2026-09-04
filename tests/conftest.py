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
from main import Account, Portfolio, Project, app, get_session


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
