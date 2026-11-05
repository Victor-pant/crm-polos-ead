"""
Dados fictícios de demonstração (2 polos, 1 usuária e 24 leads com histórico).

Usado por:
- seed.py (python seed.py) para recriar o banco local com dados de exemplo;
- app.py, quando a variável de ambiente AUTO_SEED=1 estiver definida (ex.: no
  Render), para popular automaticamente um banco vazio na primeira execução.

Todos os nomes, telefones e e-mails são fictícios (LGPD).
"""
import random
from datetime import date, datetime, timedelta

from extensions import db
from models import Polo, Usuario, Lead, Interacao

NOMES = [
    "Ana Souza", "Bruno Lima", "Carla Mendes", "Diego Alves", "Elaine Rocha", "Fábio Torres",
    "Gabriela Nunes", "Heitor Campos", "Isabela Prado", "João Ferreira", "Karina Duarte",
    "Lucas Moreira", "Mariana Teles", "Natan Ribeiro", "Olívia Santos", "Paulo Henrique",
    "Rafaela Costa", "Sérgio Matos", "Tatiane Lopes", "Vinícius Araújo", "Yasmin Oliveira",
    "Wesley Barbosa", "Larissa Fontes", "Renato Dias",
]
CURSOS = ["Administração", "Pedagogia", "Gestão de RH", "Ciências Contábeis",
          "Análise e Des. de Sistemas", "Enfermagem", "Logística", "Pós em Psicopedagogia"]
ORIGENS = (["Instagram"] * 5 + ["WhatsApp"] * 5 + ["Indicação"] * 4 + ["Facebook"] * 3
           + ["Google"] * 2 + ["Site"] * 2 + ["Evento"] * 2 + ["Telefone"])
STATUS = (["Novo"] * 5 + ["Em atendimento"] * 6 + ["Qualificado"] * 4 + ["Matrícula"] * 2
          + ["Matriculado"] * 5 + ["Perdido"] * 2)
TEMP = {"Novo": "Frio", "Em atendimento": "Morno", "Qualificado": "Quente",
        "Matrícula": "Quente", "Matriculado": "Quente", "Perdido": "Frio"}


def popular_demo():
    """Insere os dados de demonstração no banco atual (que deve estar vazio)."""
    rnd = random.Random(7)
    pz = Polo(nome="Pirapozinho")
    sa = Polo(nome="Santo Anastácio")
    db.session.add_all([pz, sa])
    db.session.flush()

    maria = Usuario(nome="Maria Comercial", email="maria@unoeste-pi.com.br", polo_id=pz.id)
    maria.set_senha("123456")
    db.session.add(maria)
    db.session.flush()

    status = STATUS[:]
    rnd.shuffle(status)
    hoje = date.today()
    for i, nome in enumerate(NOMES):
        st = status[i]
        prox = None
        if st in ("Novo", "Em atendimento", "Qualificado", "Matrícula"):
            prox = hoje + timedelta(days=rnd.choice([-3, -1, 0, 0, 1, 2, 4, 6]))
        criado = (datetime.combine(hoje - timedelta(days=rnd.randint(3, 40)), datetime.min.time())
                  + timedelta(hours=rnd.randint(8, 15), minutes=rnd.randint(0, 59)))
        lead = Lead(
            nome=nome, telefone=f"1899{rnd.randint(1000000, 9999999)}",
            email=nome.split()[0].lower() + "@email.com", curso_interesse=rnd.choice(CURSOS),
            origem=ORIGENS[i], status=st,
            temperatura=TEMP[st] if rnd.random() < .8 else rnd.choice(["Frio", "Morno", "Quente"]),
            polo_id=(pz.id if i % 3 else sa.id), responsavel_id=maria.id,
            proxima_acao_em=prox, criado_em=criado,
        )
        db.session.add(lead)
        db.session.flush()
        primeiro = nome.split()[0]
        msgs = [
            ("whatsapp", "enviada", f"Olá {primeiro}, tudo bem? Vi seu interesse no curso de {lead.curso_interesse}. Posso te passar as informações?"),
            ("whatsapp", "recebida", "Oi! Quero saber valores e como funcionam as provas presenciais."),
            ("telefone", "enviada", "Ligação explicando mensalidade, bolsa de desconto e calendário de provas no polo."),
            ("presencial", "recebida", "Visitou o polo para conhecer a estrutura e tirar dúvidas sobre documentos."),
        ]
        qtd = 1 if st == "Novo" else rnd.randint(2, 4)
        for j, (canal, direcao, msg) in enumerate(msgs[:qtd]):
            db.session.add(Interacao(
                lead_id=lead.id, usuario_id=maria.id, canal=canal, direcao=direcao, mensagem=msg,
                criado_em=criado + timedelta(days=j, minutes=rnd.randint(5, 90)),
            ))
    db.session.commit()
