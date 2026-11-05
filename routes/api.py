"""
API REST do CRM.

Permite que sistemas externos (planilhas, formulários de captação, scripts
de importação etc.) consultem e cadastrem leads e registrem interações no
histórico, autenticando-se pelo cabeçalho X-API-Token.
"""

from functools import wraps

from flask import Blueprint, request, jsonify, current_app

from extensions import db
from models import Lead, Interacao, STATUS_LEAD

bp = Blueprint("api", __name__, url_prefix="/api")


def requer_token(f):
    """Autenticação simples por token para chamadas de automação/integração."""

    @wraps(f)
    def decorado(*args, **kwargs):
        token_enviado = request.headers.get("X-API-Token", "")
        if token_enviado != current_app.config.get("API_TOKEN"):
            return jsonify({"erro": "Token de API inválido ou ausente."}), 401
        return f(*args, **kwargs)

    return decorado


@bp.route("/leads", methods=["GET"])
@requer_token
def listar_leads():
    telefone = request.args.get("telefone")
    query = Lead.query
    if telefone:
        digitos = "".join(ch for ch in telefone if ch.isdigit())
        query = query.filter(Lead.telefone.like(f"%{digitos[-8:]}%"))

    leads = query.order_by(Lead.criado_em.desc()).all()
    return jsonify([
        {
            "id": lead.id,
            "nome": lead.nome,
            "telefone": lead.telefone,
            "status": lead.status,
            "origem": lead.origem,
            "polo": lead.polo.nome if lead.polo else None,
        }
        for lead in leads
    ])


@bp.route("/leads", methods=["POST"])
@requer_token
def criar_lead():
    dados = request.get_json(silent=True) or {}
    if not dados.get("nome") or not dados.get("telefone"):
        return jsonify({"erro": "Campos 'nome' e 'telefone' são obrigatórios."}), 400

    lead = Lead(
        nome=dados["nome"],
        telefone=dados["telefone"],
        email=dados.get("email"),
        curso_interesse=dados.get("curso_interesse"),
        origem=dados.get("origem", "Outros"),
        status=dados.get("status", "Novo") if dados.get("status") in STATUS_LEAD else "Novo",
        polo_id=dados.get("polo_id"),
    )
    db.session.add(lead)
    db.session.commit()
    return jsonify({"id": lead.id, "mensagem": "Lead criado."}), 201


@bp.route("/leads/<int:lead_id>/interacoes", methods=["GET"])
@requer_token
def listar_interacoes(lead_id):
    lead = Lead.query.get_or_404(lead_id)
    return jsonify([i.to_dict() for i in lead.interacoes])


@bp.route("/leads/<int:lead_id>/interacoes", methods=["POST"])
@requer_token
def criar_interacao(lead_id):
    lead = Lead.query.get_or_404(lead_id)
    dados = request.get_json(silent=True) or {}

    if not dados.get("mensagem"):
        return jsonify({"erro": "Campo 'mensagem' é obrigatório."}), 400

    interacao = Interacao(
        lead_id=lead.id,
        canal=dados.get("canal", "whatsapp"),
        direcao=dados.get("direcao", "recebida"),
        mensagem=dados["mensagem"],
        origem_automatica=True,
    )
    db.session.add(interacao)
    db.session.commit()
    return jsonify(interacao.to_dict()), 201

