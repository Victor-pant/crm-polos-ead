from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from sqlalchemy import func

from extensions import db
from models import Lead, STATUS_LEAD

bp = Blueprint("dashboard", __name__)


@bp.route("/")
@login_required
def index():
    total_leads = Lead.query.count()
    matriculados = Lead.query.filter_by(status="Matriculado").count()
    taxa_conversao = round((matriculados / total_leads) * 100, 1) if total_leads else 0
    atrasados = sum(1 for lead in Lead.query.all() if lead.esta_atrasado)

    return render_template(
        "dashboard.html",
        total_leads=total_leads,
        matriculados=matriculados,
        taxa_conversao=taxa_conversao,
        atrasados=atrasados,
    )


@bp.route("/dashboard/dados")
@login_required
def dados():
    """JSON consumido pelo JavaScript da página para montar os gráficos (Chart.js)."""

    por_status = dict(
        db.session.query(Lead.status, func.count(Lead.id)).group_by(Lead.status).all()
    )
    por_origem = dict(
        db.session.query(Lead.origem, func.count(Lead.id)).group_by(Lead.origem).all()
    )
    por_polo = dict(
        db.session.query(Lead.polo_id, func.count(Lead.id)).group_by(Lead.polo_id).all()
    )

    from models import Polo
    nomes_polo = {p.id: p.nome for p in Polo.query.all()}
    por_polo_nomeado = {nomes_polo.get(pid, "Sem polo"): total for pid, total in por_polo.items()}

    return jsonify({
        "status": {"labels": STATUS_LEAD, "valores": [por_status.get(s, 0) for s in STATUS_LEAD]},
        "origem": {"labels": list(por_origem.keys()), "valores": list(por_origem.values())},
        "polo": {"labels": list(por_polo_nomeado.keys()), "valores": list(por_polo_nomeado.values())},
    })
