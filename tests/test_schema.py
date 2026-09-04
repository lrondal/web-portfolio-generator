"""Schema-level guarantees the later tickets inherit."""

import pytest
from conftest import SeedPortfolio
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, SQLModel, select

from main import Account, Portfolio, Project


def test_user_table_gone_new_tables_present() -> None:
    tables = set(SQLModel.metadata.tables)
    assert "user" not in tables
    assert {"account", "portfolio", "project"} <= tables


def test_duplicate_sign_in_email_is_rejected(session: Session) -> None:
    session.add(Account(email="dup@example.com", display_name="A", age=20))
    session.commit()

    session.add(Account(email="dup@example.com", display_name="B", age=21))
    with pytest.raises(IntegrityError):
        session.commit()


def test_deleting_account_cascades_to_portfolios_and_projects(
    session: Session, seed_portfolio: SeedPortfolio
) -> None:
    portfolio = seed_portfolio(
        projects=[
            {"name": "P1", "description": "d"},
            {"name": "P2", "description": "d"},
        ]
    )
    account_id = portfolio.account_id

    session.delete(session.get(Account, account_id))
    session.commit()

    remaining_portfolios = session.exec(
        select(Portfolio).where(Portfolio.account_id == account_id)
    ).all()
    assert remaining_portfolios == []
    assert session.exec(select(Project)).all() == []


def test_deleting_portfolio_cascades_to_its_projects(
    session: Session, seed_portfolio: SeedPortfolio
) -> None:
    portfolio = seed_portfolio(projects=[{"name": "P1", "description": "d"}])
    portfolio_id = portfolio.portfolio_id

    session.delete(session.get(Portfolio, portfolio_id))
    session.commit()

    remaining_projects = session.exec(
        select(Project).where(Project.portfolio_id == portfolio_id)
    ).all()
    assert remaining_projects == []
