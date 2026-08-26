"""initial migration

Revision ID: 7b382568f1c0
Revises:
Create Date: 2026-08-26 00:34:58.978685

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "7b382568f1c0"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
