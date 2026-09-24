import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database import get_db
from app.main import app
from app.models import Document, DocumentChunk


TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://aiagent:aiagent@localhost:5432/aiagent_test",
)

engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture
def db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.query(DocumentChunk).delete()
        db.query(Document).delete()
        db.commit()
        db.close()


@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()