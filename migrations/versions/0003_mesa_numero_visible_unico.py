"""numero_visible único por zona (case-insensitive) — §20 hardening

Revision ID: 0003_mesa_numero_visible_unico
Revises: 0002_mesas_zonas_audit
Create Date: 2026-06-29

Índice único funcional `lower(numero_visible)` por `zona_id` (REG-20-15, D-h1). Incluye
mesas inactivas. Si hay duplicados locales previos, limpiar/renombrar antes de aplicar.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003_mesa_numero_visible_unico"
down_revision: str | None = "0002_mesas_zonas_audit"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index(
        "uq_mesas_zona_numero_lower",
        "mesas",
        ["zona_id", sa.text("lower(numero_visible)")],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_mesas_zona_numero_lower", table_name="mesas")
