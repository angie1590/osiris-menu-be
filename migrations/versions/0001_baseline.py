"""baseline: tabla request_ids_procesados (idempotencia)

Revision ID: 0001_baseline
Revises:
Create Date: 2026-06-28

Baseline del scaffolding. No incluye tablas de dominio de módulos (llegan con cada
propuesta funcional). Sólo `request_ids_procesados` para idempotencia (D-b/D-e).
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_baseline"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "request_ids_procesados",
        sa.Column("request_id", sa.String(length=36), primary_key=True),
        sa.Column("endpoint", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("request_ids_procesados")
