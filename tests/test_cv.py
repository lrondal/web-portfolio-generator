"""Public portfolio render: GET /cv/{portfolio_id}."""

from conftest import SeedPortfolio
from fastapi.testclient import TestClient


def test_seeded_portfolio_shows_header_and_project_names(
    client: TestClient, seed_portfolio: SeedPortfolio
) -> None:
    portfolio = seed_portfolio(
        title="Data Work",
        display_name="Ada Lovelace",
        projects=[
            {"name": "Analytic Engine", "description": "A general-purpose computer."},
            {"name": "Note G", "description": "The first published algorithm."},
        ],
    )

    resp = client.get(f"/cv/{portfolio.portfolio_id}")

    assert resp.status_code == 200
    body = resp.text
    assert "Ada Lovelace" in body  # profile header
    assert "Data Work" in body  # portfolio title
    assert "Analytic Engine" in body
    assert "Note G" in body


def test_portfolio_with_no_projects_shows_empty_state(
    client: TestClient, seed_portfolio: SeedPortfolio
) -> None:
    portfolio = seed_portfolio(projects=[])

    resp = client.get(f"/cv/{portfolio.portfolio_id}")

    assert resp.status_code == 200
    assert "no projects yet" in resp.text.lower()


def test_unknown_portfolio_id_returns_404(client: TestClient) -> None:
    resp = client.get("/cv/999999")

    assert resp.status_code == 404
