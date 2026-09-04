"""Signup / login / logout through the HTTP seam (ADR-0002: email + password).

Every test drives the real routes; the session cookie the app sets is the only
thing carried between requests (TestClient keeps its own cookie jar per test).
"""

from conftest import LogInClient
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from main import Account

GOOD_PASSWORD = "password123"


def test_signup_creates_hashed_account_and_logs_in(
    client: TestClient, session: Session
) -> None:
    resp = client.post(
        "/signup", data={"email": "Ada@example.com", "password": GOOD_PASSWORD}
    )

    assert resp.status_code == 200
    assert resp.url.path == "/portfolios"
    assert "no portfolios yet" in resp.text.lower()

    account = session.exec(
        select(Account).where(Account.email == "ada@example.com")
    ).one()
    assert account.password_hash
    assert account.password_hash != GOOD_PASSWORD
    assert GOOD_PASSWORD not in account.password_hash


def test_signup_rejects_duplicate_email(client: TestClient) -> None:
    client.post(
        "/signup", data={"email": "dup@example.com", "password": GOOD_PASSWORD}
    )

    resp = client.post(
        "/signup",
        data={"email": "dup@example.com", "password": GOOD_PASSWORD},
        follow_redirects=False,
    )

    assert resp.status_code == 400
    assert "exist" in resp.text.lower()


def test_signup_rejects_short_password(
    client: TestClient, session: Session
) -> None:
    resp = client.post(
        "/signup",
        data={"email": "shorty@example.com", "password": "7chars!"},
        follow_redirects=False,
    )

    assert resp.status_code == 400
    assert "at least 8" in resp.text.lower()
    assert session.exec(select(Account)).all() == []


def test_signup_accepts_password_longer_than_72_bytes(client: TestClient) -> None:
    # bcrypt caps its input at 72 bytes; the pre-hash in auth.py removes that
    # ceiling, so a very long password must still sign up cleanly (not 500).
    resp = client.post(
        "/signup",
        data={"email": "long@example.com", "password": "p" * 200},
        follow_redirects=False,
    )

    assert resp.status_code == 303
    assert resp.headers["location"] == "/portfolios"


def test_login_rejects_wrong_password(client: TestClient) -> None:
    client.post(
        "/signup", data={"email": "ada@example.com", "password": GOOD_PASSWORD}
    )
    client.post("/logout")

    resp = client.post(
        "/login",
        data={"email": "ada@example.com", "password": "wrongpassword"},
        follow_redirects=False,
    )

    assert resp.status_code == 400
    assert "incorrect" in resp.text.lower()


def test_login_rejects_unknown_email(client: TestClient) -> None:
    resp = client.post(
        "/login",
        data={"email": "nobody@example.com", "password": GOOD_PASSWORD},
        follow_redirects=False,
    )

    assert resp.status_code == 400


def test_login_succeeds_after_signup_and_logout(client: TestClient) -> None:
    client.post(
        "/signup", data={"email": "ada@example.com", "password": GOOD_PASSWORD}
    )
    client.post("/logout")

    resp = client.post(
        "/login", data={"email": "ada@example.com", "password": GOOD_PASSWORD}
    )

    assert resp.status_code == 200
    assert resp.url.path == "/portfolios"


def test_portfolio_list_shows_empty_state_for_fresh_account(
    logged_in_client: LogInClient,
) -> None:
    client = logged_in_client()

    resp = client.get("/portfolios")

    assert resp.status_code == 200
    assert "no portfolios yet" in resp.text.lower()


def test_anonymous_visitor_to_portfolio_list_is_redirected_to_login(
    client: TestClient,
) -> None:
    resp = client.get("/portfolios", follow_redirects=False)

    assert resp.status_code == 303
    assert resp.headers["location"] == "/login"


def test_protected_page_redirects_to_login_after_logout(
    logged_in_client: LogInClient,
) -> None:
    client = logged_in_client()
    assert client.get("/portfolios", follow_redirects=False).status_code == 200

    client.post("/logout")

    resp = client.get("/portfolios", follow_redirects=False)
    assert resp.status_code == 303
    assert resp.headers["location"] == "/login"


def test_session_cookie_is_http_only(client: TestClient) -> None:
    resp = client.post(
        "/signup",
        data={"email": "ada@example.com", "password": GOOD_PASSWORD},
        follow_redirects=False,
    )

    set_cookie = resp.headers["set-cookie"]
    assert "session=" in set_cookie
    assert "httponly" in set_cookie.lower()


def test_tampered_session_cookie_is_rejected(client: TestClient) -> None:
    client.post(
        "/signup",
        data={"email": "ada@example.com", "password": GOOD_PASSWORD},
        follow_redirects=False,
    )
    assert client.get("/portfolios", follow_redirects=False).status_code == 200

    client.cookies.set("session", "tampered-value")
    resp = client.get("/portfolios", follow_redirects=False)

    assert resp.status_code == 303
    assert resp.headers["location"] == "/login"
