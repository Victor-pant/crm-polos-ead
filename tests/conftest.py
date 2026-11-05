import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

from app import create_app
from config import TestConfig
from extensions import db
from models import Polo, Usuario, Lead


@pytest.fixture
def app():
    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()

        polo = Polo(nome="Pirapozinho")
        db.session.add(polo)
        db.session.flush()

        usuario = Usuario(nome="Teste", email="teste@crm.com", polo_id=polo.id)
        usuario.set_senha("senha123")
        db.session.add(usuario)
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def cliente_autenticado(client):
    client.post("/login", data={"email": "teste@crm.com", "senha": "senha123"})
    return client


@pytest.fixture
def api_headers(app):
    return {"X-API-Token": app.config["API_TOKEN"]}
