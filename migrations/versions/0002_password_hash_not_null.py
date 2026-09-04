"""account.password_hash becomes NOT NULL

Ticket 1's baseline left ``password_hash`` nullable (#3 was written to expect
either that or an absent column). Every Account is now created through signup,
which always stores a bcrypt hash, so the column is tightened to NOT NULL.

Revision ID: 0002_password_hash_not_null
Revises: 0001_baseline
Create Date: 2026-09-04 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = '0002_password_hash_not_null'
down_revision: Union[str, None] = '0001_baseline'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('account', schema=None) as batch_op:
        batch_op.alter_column(
            'password_hash',
            existing_type=sqlmodel.sql.sqltypes.AutoString(),
            nullable=False,
        )


def downgrade() -> None:
    with op.batch_alter_table('account', schema=None) as batch_op:
        batch_op.alter_column(
            'password_hash',
            existing_type=sqlmodel.sql.sqltypes.AutoString(),
            nullable=True,
        )
