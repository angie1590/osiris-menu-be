"""Fixtures de test. DB sqlite por archivo temporal para evitar problemas cross-loop."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from osiris.db import Base, get_session
from osiris.main import app
from osiris.shared import models as _models  # noqa: F401  (registra tablas en Base.metadata)


@pytest.fixture()
def client(tmp_path) -> Iterator[TestClient]:
    db_path = tmp_path / "test.db"

    # Crea el esquema con un engine síncrono (metadata es dialect-agnóstica).
    sync_engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(sync_engine)
    sync_engine.dispose()

    async_engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}")
    TestSession = async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)

    async def _override_get_session():
        async with TestSession() as session:
            yield session

    app.dependency_overrides[get_session] = _override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
