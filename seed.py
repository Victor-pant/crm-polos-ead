"""
Popula o banco de dados com dados de demonstração: polos, um usuário de
teste e alguns leads em diferentes estágios. Rode com:

    python seed.py
"""
from datetime import date, timedelta

from app import create_app
from extensions import db
from models import Polo, Usuario, Lead, Interacao

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    pirapozinho = Polo(nome="Pirapozinho")
    santo_anastacio = Polo(nome="Santo Anastácio")
    db.session.add_all([pirapozinho, santo_anastacio])
    db.session.flush()

    maria = Usuario(nome="Maria Comercial", email="maria@unoeste-pi.com.br", polo_id=pirapozinho.id)
    maria.set_senha("123456")
    db.session.add(maria)
    db.session.flush()

    hoje = date.today()
    leads_demo = [
        dict(nome="Ana Souza", telefone="18999991111", origem="Instagram", status="Novo",
             temperatura="Morno", polo_id=pirapozinho.id, proxima_acao_em=hoje),
        dict(nome="Bruno Lima", telefone="18999992222", origem="WhatsApp", status="Em atendimento",
             temperatura="Quente", polo_id=pirapozinho.id, proxima_acao_em=hoje - timedelta(days=2)),
        dict(nome="Carla Mendes", telefone="18999993333", origem="Indicação", status="Qualificado",
             temperatura="Quente", polo_id=santo_anastacio.id, proxima_acao_em=hoje + timedelta(days=3)),
        dict(nome="Diego Alves", telefone="18999994444", origem="Google", status="Matrícula",
             temperatura="Quente", polo_id=santo_anastacio.id),
        dict(nome="Elaine Rocha", telefone="18999995555", origem="Facebook", status="Matriculado",
             temperatura="Quente", polo_id=pirapozinho.id),
        dict(nome="Fábio Torres", telefone="18999996666", origem="Site", status="Perdido",
             temperatura="Frio", polo_id=santo_anastacio.id),
        dict(nome="Gabriela Nunes", telefone="18999997777", origem="WhatsApp", status="Novo",
             temperatura="Frio", polo_id=pirapozinho.id),
    ]

    for dados in leads_demo:
        lead = Lead(responsavel_id=maria.id, **dados)
        db.session.add(lead)
        db.session.flush()
        db.session.add(Interacao(
            lead_id=lead.id, usuario_id=maria.id, canal="whatsapp", direcao="enviada",
            mensagem=f"Olá {dados['nome'].split()[0]}, tudo bem? Vi seu interesse em nossos cursos!",
        ))

    db.session.commit()
    print("Banco de dados populado com sucesso: 2 polos, 1 usuário e 7 leads de exemplo.")
    print("Login: maria@unoeste-pi.com.br / senha: 123456")
