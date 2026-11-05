import os
import re

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def _resolver_database_uri():
    """
    Monta a URI do banco de forma que um caminho SQLite relativo (ex.:
    'sqlite:///crm.db' vindo do .env) sempre aponte para a pasta do
    projeto — evitando que o Flask-SQLAlchemy resolva o caminho relativo
    contra a pasta 'instance/' e crie um banco vazio "fantasma" ali,
    diferente do banco populado pelo seed.py.
    """
    url = os.environ.get("DATABASE_URL")
    if not url:
        return f"sqlite:///{os.path.join(BASE_DIR, 'crm.db')}"

    prefixo = "sqlite:///"
    if url.startswith(prefixo):
        caminho = url[len(prefixo):]
        caminho_absoluto = os.path.isabs(caminho) or re.match(r"^[A-Za-z]:", caminho)
        if not caminho_absoluto:
            caminho = os.path.join(BASE_DIR, caminho)
        return f"sqlite:///{caminho}"

    return url  # outros bancos (PostgreSQL, MySQL etc.) usam a URL como está


class Config:
    """Configuração base. Valores sensíveis vêm de variáveis de ambiente."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "chave-de-desenvolvimento-trocar-em-producao")
    SQLALCHEMY_DATABASE_URI = _resolver_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Token simples usado para autenticar chamadas de sistemas externos
    # (integrações/automações) na API REST.
    API_TOKEN = os.environ.get("API_TOKEN", "token-de-desenvolvimento")


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
