"""mesas, zonas, grupos_mesas y audit_logs (§20)

Revision ID: 0002_mesas_zonas_audit
Revises: 0001_baseline
Create Date: 2026-06-29

Vertical funcional §20: tablas de Zona, Mesa, GrupoMesas y la auditoría persistente
`audit_logs`. La pertenencia a grupo vive en `mesas.grupo_id` (sin arreglo `mesas_ids`).
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_mesas_zonas_audit"
down_revision: str | None = "0001_baseline"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "zonas",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("estado", sa.String(length=20), nullable=False),
        sa.Column("aforo_max", sa.Integer(), nullable=False),
        sa.Column("orden_visualizacion", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "grupos_mesas",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("comanda_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("dissolved_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "mesas",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("zona_id", sa.Uuid(), sa.ForeignKey("zonas.id"), nullable=False),
        sa.Column("numero_visible", sa.String(length=50), nullable=False),
        sa.Column("capacidad", sa.Integer(), nullable=False),
        sa.Column("estado", sa.String(length=20), nullable=False),
        sa.Column("comanda_activa_id", sa.Uuid(), nullable=True),
        sa.Column("reserva_activa_id", sa.Uuid(), nullable=True),
        sa.Column("grupo_id", sa.Uuid(), sa.ForeignKey("grupos_mesas.id"), nullable=True),
        sa.Column("activa", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("entity_type", sa.String(length=50), nullable=False),
        sa.Column("entity_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("mesas")
    op.drop_table("grupos_mesas")
    op.drop_table("zonas")
