"""Capa de datos asíncrona: engine asyncpg, Base declarativa y sesión async."""

from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from .config import settings


class Base(DeclarativeBase):
    """Base declarativa común para todos los modelos SQLAlchemy."""


engine = create_async_engine(settings.DATABASE_URL, future=True, echo=False)

SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncIterator[AsyncSession]:
    """Dependencia FastAPI que entrega una sesión async por request."""
    async with SessionLocal() as session:
        yield session
