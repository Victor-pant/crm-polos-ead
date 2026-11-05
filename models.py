from datetime import datetime, date

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db

# ---------------------------------------------------------------------------
# Listas fixas usadas em vários pontos (formulários, filtros, seed de dados)
# ---------------------------------------------------------------------------
STATUS_LEAD = ["Novo", "Em atendimento", "Qualificado", "Matrícula", "Matriculado", "Perdido"]
TEMPERATURA_LEAD = ["Frio", "Morno", "Quente"]
ORIGENS_LEAD = [
    "Instagram", "Facebook", "Google", "Indicação", "WhatsApp",
    "Site", "Evento", "Telefone", "Outros",
]
CANAIS_INTERACAO = ["whatsapp", "telefone", "presencial", "email"]
DIRECOES_INTERACAO = ["enviada", "recebida"]


class Polo(db.Model):
    __tablename__ = "polos"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), unique=True, nullable=False)

    usuarios = db.relationship("Usuario", back_populates="polo")
    leads = db.relationship("Lead", back_populates="polo")

    def __repr__(self):
        return f"<Polo {self.nome}>"


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    polo_id = db.Column(db.Integer, db.ForeignKey("polos.id"), nullable=True)

    polo = db.relationship("Polo", back_populates="usuarios")
    leads_responsavel = db.relationship("Lead", back_populates="responsavel")

    def set_senha(self, senha_texto_puro):
        self.senha_hash = generate_password_hash(senha_texto_puro)

    def checar_senha(self, senha_texto_puro):
        return check_password_hash(self.senha_hash, senha_texto_puro)

    def __repr__(self):
        return f"<Usuario {self.email}>"


class Lead(db.Model):
    __tablename__ = "leads"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(160), nullable=False)
    telefone = db.Column(db.String(20), nullable=False, index=True)
    email = db.Column(db.String(160), nullable=True)
    curso_interesse = db.Column(db.String(160), nullable=True)
    origem = db.Column(db.String(40), nullable=False, default="Outros")
    status = db.Column(db.String(30), nullable=False, default="Novo", index=True)
    temperatura = db.Column(db.String(10), nullable=False, default="Frio")

    polo_id = db.Column(db.Integer, db.ForeignKey("polos.id"), nullable=True)
    responsavel_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)

    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    proxima_acao_em = db.Column(db.Date, nullable=True)

    polo = db.relationship("Polo", back_populates="leads")
    responsavel = db.relationship("Usuario", back_populates="leads_responsavel")
    interacoes = db.relationship(
        "Interacao", back_populates="lead",
        order_by="Interacao.criado_em.desc()",
        cascade="all, delete-orphan",
    )

    @property
    def esta_atrasado(self):
        return bool(
            self.proxima_acao_em
            and self.proxima_acao_em < date.today()
            and self.status not in ("Matriculado", "Perdido")
        )

    @property
    def retorno_e_hoje(self):
        return self.proxima_acao_em == date.today()

    def telefone_normalizado(self):
        """Remove tudo que não for dígito e garante o 55 (Brasil) na frente."""
        digitos = "".join(ch for ch in self.telefone if ch.isdigit())
        if not digitos.startswith("55"):
            digitos = "55" + digitos
        return digitos

    def __repr__(self):
        return f"<Lead {self.nome} ({self.status})>"


class Interacao(db.Model):
    __tablename__ = "interacoes"

    id = db.Column(db.Integer, primary_key=True)
    lead_id = db.Column(db.Integer, db.ForeignKey("leads.id"), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)

    canal = db.Column(db.String(20), nullable=False, default="whatsapp")
    direcao = db.Column(db.String(10), nullable=False, default="enviada")
    mensagem = db.Column(db.Text, nullable=False)
    origem_automatica = db.Column(db.Boolean, default=False)  # True = veio de automação/API

    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    lead = db.relationship("Lead", back_populates="interacoes")
    usuario = db.relationship("Usuario")

    def to_dict(self):
        return {
            "id": self.id,
            "lead_id": self.lead_id,
            "canal": self.canal,
            "direcao": self.direcao,
            "mensagem": self.mensagem,
            "origem_automatica": self.origem_automatica,
            "criado_em": self.criado_em.isoformat(),
        }
