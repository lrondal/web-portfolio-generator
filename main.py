# https://github.com/EPF-MDE/fastapi-coffee-experiment/blob/master/main.py
import os
from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select


class Account(SQLModel, table=True):
    """The identity a person signs in with, plus their single inline Profile.

    One Profile per Account (ADR-0001): the profile fields live here as columns
    rather than in their own table. ``password_hash`` is nullable for now and is
    populated once signup/login lands (Ticket 2).
    """

    account_id: int | None = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)  # sign-in email
    password_hash: str | None = None

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


# Engine URL comes from the environment (postgresql://... in every non-test env,
# per ADR-0003). The SQLite fallback keeps a bare local checkout runnable; the
# schema itself is owned by the Alembic migrations, not by create_all.
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///database.db")

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
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "static")),
    name="static",
)


@app.get("/")
def home_page(request: Request):
    return templates.TemplateResponse(request, "index.html")


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
        },
    )
