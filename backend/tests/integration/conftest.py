# NADA de imports do teu app aqui em cima!
import os
import pytest
from testcontainers.postgres import PostgresContainer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.settings.base import Base  # isto não cria ligações

# 1) Container + DATABASE_URL
@pytest.fixture(scope="session")
def pg_url():
    with PostgresContainer("postgres:16") as pg:
        url = pg.get_connection_url()  # ex: postgresql+psycopg2://...
        os.environ["DATABASE_URL"] = url  # garantir que o app usa esta DB ao importar
        yield url  # container vive até ao fim da sessão

# 2) Sessionmaker ligado ao container
@pytest.fixture(scope="session")
def pg_sessionmaker(pg_url):
    engine = create_engine(pg_url, future=True)
    Base.metadata.create_all(bind=engine)   # cria schema de teste
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    return TestingSessionLocal

# 3) TestClient com override do get_db (importa app SÓ agora)
@pytest.fixture(scope="function")
def client(pg_sessionmaker):
    # import tardio — agora a DATABASE_URL já aponta para o container
    from app.main import app
    from app.settings.database import get_db

    def _override_get_db():
        db = pg_sessionmaker()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()