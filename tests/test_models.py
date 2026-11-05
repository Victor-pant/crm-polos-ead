from datetime import date, timedelta

from extensions import db
from models import Lead, Usuario


def test_senha_e_verificada_com_hash(app):
    with app.app_context():
        usuario = Usuario.query.filter_by(email="teste@crm.com").first()
        assert usuario.checar_senha("senha123") is True
        assert usuario.checar_senha("senha-errada") is False
        assert usuario.senha_hash != "senha123"  # nunca guardar senha em texto puro


def test_telefone_normalizado_adiciona_codigo_do_brasil(app):
    with app.app_context():
        lead = Lead(nome="Teste", telefone="18999998888")
        assert lead.telefone_normalizado() == "5518999998888"

        lead_com_55 = Lead(nome="Teste2", telefone="5518999998888")
        assert lead_com_55.telefone_normalizado() == "5518999998888"


def test_lead_atrasado_quando_proxima_acao_no_passado(app):
    with app.app_context():
        lead = Lead(nome="Atrasado", telefone="18900000000",
                     proxima_acao_em=date.today() - timedelta(days=1), status="Em atendimento")
        assert lead.esta_atrasado is True


def test_lead_nao_atrasado_se_ja_matriculado(app):
    with app.app_context():
        lead = Lead(nome="Matriculado", telefone="18900000001",
                     proxima_acao_em=date.today() - timedelta(days=5), status="Matriculado")
        assert lead.esta_atrasado is False
