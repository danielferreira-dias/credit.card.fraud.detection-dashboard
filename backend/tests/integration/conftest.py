# NADA de imports do teu app aqui em cima!
import os
import pytest
from testcontainers.postgres import PostgresContainer
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.settings.base import Base  # isto não cria ligações

# 1) Container + DATABASE_URL
@pytest.fixture(scope="session")
def pg_url():
    with PostgresContainer("postgres:16") as pg:
        url = pg.get_connection_url()  # ex: postgresql+psycopg2://...
        # Convert to async URL
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://")
        os.environ["DATABASE_URL"] = url  # garantir que o app usa esta DB ao importar
        yield url  # container vive até ao fim da sessão

# 2) Async sessionmaker ligado ao container
@pytest.fixture(scope="session")
async def pg_sessionmaker(pg_url):
    async_engine = create_async_engine(pg_url, echo=False)

    # Create tables
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    TestingAsyncSessionLocal = sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        autocommit=False,
        autoflush=False
    )
    return TestingAsyncSessionLocal

# 3) TestClient com override do get_db (importa app SÓ agora)
@pytest.fixture(scope="function")
def client(pg_sessionmaker):
    # import tardio — agora a DATABASE_URL já aponta para o container
    from app.main import app
    from app.settings.database import get_db

    async def _override_get_db():
        async with pg_sessionmaker() as session:
            yield session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()