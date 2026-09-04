# https://github.com/EPF-MDE/fastapi-coffee-experiment/blob/master/main.py
import os
from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select
from starlette.middleware.sessions import SessionMiddleware

from auth import hash_password, verify_password


class Account(SQLModel, table=True):
    """The identity a person signs in with, plus their single inline Profile.

    One Profile per Account (ADR-0001): the profile fields live here as columns
    rather than in their own table. Every Account is born through signup, so
    ``password_hash`` is NOT NULL (migration ``0002``).
    """

    account_id: int | None = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)  # sign-in email
    password_hash: str  # bcrypt hash; set at signup, never stored in plaintext

    # Profile fields, shown at the top of every one of this account's portfolios.
    display_name: str
    age: int
    contact_email: str | None = None  # public, distinct from the sign-in email
    github: str | None = None
    phone: str | None = None

    portfolios: list["Portfolio"] = Relationship(
        back_populates="account",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class Portfolio(SQLModel, table=True):
    """A public page owned by exactly one Account, addressed by its own id."""

    portfolio_id: int | None = Field(default=None, primary_key=True)
    account_id: int = Field(
        foreign_key="account.account_id", ondelete="CASCADE", index=True
    )
    title: str
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    account: Account | None = Relationship(back_populates="portfolios")
    projects: list["Project"] = Relationship(
        back_populates="portfolio",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class Project(SQLModel, table=True):
    """One item within a Portfolio."""

    project_id: int | None = Field(default=None, primary_key=True)
    portfolio_id: int = Field(
        foreign_key="portfolio.portfolio_id", ondelete="CASCADE", index=True
    )
    name: str
    description: str
    image_url: str | None = None
    link: str | None = None
    skill_list: str | None = None  # comma-separated, split into tags in the template

    portfolio: Portfolio | None = Relationship(back_populates="projects")


DEFAULT_DATABASE_URL = "sqlite:///database.db"


def resolve_database_url() -> str:
    """Engine URL from the environment (``postgresql://...`` in every non-test
    env, per ADR-0003). The SQLite fallback keeps a bare local checkout
    runnable; the schema itself is owned by the Alembic migrations, not by
    ``create_all``.
    """
    return os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)


DATABASE_URL = resolve_database_url()

DEFAULT_SESSION_SECRET = "dev-only-insecure-session-secret"


def resolve_session_secret() -> str:
    """Secret that signs the session cookie, from ``SESSION_SECRET``.

    A separate deployment secret from the database URL. The dev fallback keeps a
    bare local checkout runnable; every real environment must set it so cookies
    signed by one deploy stay valid on the next.
    """
    return os.environ.get("SESSION_SECRET", DEFAULT_SESSION_SECRET)


# Signup takes only an email + password (ADR-0002); the other Profile columns
# are NOT NULL, so a fresh Account gets placeholders until profile editing lands.
# The only password rule is a minimum length (bcrypt's 72-byte input cap is
# handled by the pre-hash in ``auth``, so there is no maximum to police here).
MIN_PASSWORD_LENGTH = 8

connect_args = (
    {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)
engine = create_engine(DATABASE_URL, connect_args=connect_args)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "template"))


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=resolve_session_secret())
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "static")),
    name="static",
)


def get_current_account(request: Request, session: Session) -> Account | None:
    """The signed-in Account, or ``None`` — read straight from the signed,
    HTTP-only session cookie (``account_id`` claim); there is no server-side
    session store.
    """
    account_id = request.session.get("account_id")
    if account_id is None:
        return None
    return session.get(Account, account_id)


def password_rejection_reason(password: str) -> str | None:
    """A user-facing message when ``password`` is unacceptable, else ``None``."""
    if len(password) < MIN_PASSWORD_LENGTH:
        return f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
    return None


# A valid hash to verify against when the email is unknown, so a bad email and a
# bad password both pay one bcrypt check and cannot be told apart by timing.
_ABSENT_ACCOUNT_HASH = hash_password("no-account-with-this-email")


def start_session(request: Request, account: Account) -> RedirectResponse:
    """Put ``account`` in the session cookie and send them to their portfolios."""
    request.session["account_id"] = account.account_id
    return RedirectResponse("/portfolios", status_code=303)


def render_auth_form(
    request: Request,
    template_name: str,
    *,
    current_account: Account | None = None,
    error: str | None = None,
    email: str = "",
    status_code: int = 200,
):
    """Render ``signup.html`` / ``login.html`` — one place builds their context."""
    return templates.TemplateResponse(
        request,
        template_name,
        {
            "current_account": current_account,
            "error": error,
            "email": email,
            "min_password_length": MIN_PASSWORD_LENGTH,
        },
        status_code=status_code,
    )


@app.get("/")
def home_page(request: Request, session: SessionDep):
    return templates.TemplateResponse(
        request,
        "index.html",
        {"current_account": get_current_account(request, session)},
    )


@app.get("/signup", response_class=HTMLResponse)
def signup_form(request: Request, session: SessionDep):
    return render_auth_form(
        request,
        "signup.html",
        current_account=get_current_account(request, session),
    )


@app.post("/signup")
def signup(
    request: Request,
    session: SessionDep,
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
):
    email = email.strip().lower()
    error = password_rejection_reason(password)
    if error is None and session.exec(
        select(Account).where(Account.email == email)
    ).first():
        error = "An account with that email already exists."
    if error is not None:
        return render_auth_form(
            request, "signup.html", error=error, email=email, status_code=400
        )

    account = Account(
        email=email,
        password_hash=hash_password(password),
        display_name=email.split("@")[0],  # placeholder Profile, editable later
        age=0,
    )
    session.add(account)
    session.commit()
    session.refresh(account)

    return start_session(request, account)


@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request, session: SessionDep):
    return render_auth_form(
        request,
        "login.html",
        current_account=get_current_account(request, session),
    )


@app.post("/login")
def login(
    request: Request,
    session: SessionDep,
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
):
    email = email.strip().lower()
    account = session.exec(
        select(Account).where(Account.email == email)
    ).first()
    known_hash = account.password_hash if account else _ABSENT_ACCOUNT_HASH
    if not verify_password(password, known_hash) or account is None:
        return render_auth_form(
            request,
            "login.html",
            error="Incorrect email or password.",
            email=email,
            status_code=400,
        )

    return start_session(request, account)


@app.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)


@app.get("/portfolios", response_class=HTMLResponse)
def portfolio_list(request: Request, session: SessionDep):
    account = get_current_account(request, session)
    if account is None:
        return RedirectResponse("/login", status_code=303)

    portfolios = session.exec(
        select(Portfolio).where(Portfolio.account_id == account.account_id)
    ).all()
    return templates.TemplateResponse(
        request,
        "portfolios.html",
        {"current_account": account, "portfolios": portfolios},
    )


@app.get("/cv/{portfolio_id}", response_class=HTMLResponse)
def portfolio_page(request: Request, portfolio_id: int, session: SessionDep):
    portfolio = session.get(Portfolio, portfolio_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    account = session.get(Account, portfolio.account_id)
    projects = session.exec(
        select(Project).where(Project.portfolio_id == portfolio_id)
    ).all()

    return templates.TemplateResponse(
        request=request,
        name="cv.html",
        context={
            "account": account,
            "portfolio": portfolio,
            "projects": projects,
            "current_account": get_current_account(request, session),
        },
    )
