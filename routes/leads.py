from datetime import date, datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db
from models import Lead, Interacao, Polo, STATUS_LEAD, TEMPERATURA_LEAD, ORIGENS_LEAD, CANAIS_INTERACAO

bp = Blueprint("leads", __name__, url_prefix="/leads")


def _prioridade(lead: Lead):
    """
    Chave de ordenação da lista inteligente (menor = mais urgente):
    0 = atrasado, 1 = retorno é hoje, 2 = novo, 3 = qualificado, 4 = demais.
    """
    if lead.esta_atrasado:
        return (0, lead.proxima_acao_em or date.min)
    if lead.retorno_e_hoje:
        return (1, lead.proxima_acao_em)
    if lead.status == "Novo":
        return (2, lead.criado_em)
    if lead.status == "Qualificado":
        return (3, lead.atualizado_em)
    return (4, lead.atualizado_em)


@bp.route("/")
@login_required
def listar():
    query = Lead.query

    status = request.args.get("status", "")
    polo_id = request.args.get("polo_id", "")
    origem = request.args.get("origem", "")
    busca = request.args.get("busca", "").strip()

    if status:
        query = query.filter(Lead.status == status)
    if polo_id:
        query = query.filter(Lead.polo_id == int(polo_id))
    if origem:
        query = query.filter(Lead.origem == origem)
    if busca:
        like = f"%{busca}%"
        query = query.filter(db.or_(Lead.nome.ilike(like), Lead.telefone.ilike(like)))

    leads = query.all()
    leads.sort(key=_prioridade)

    return render_template(
        "leads_list.html",
        leads=leads,
        polos=Polo.query.order_by(Polo.nome).all(),
        status_opcoes=STATUS_LEAD,
        origem_opcoes=ORIGENS_LEAD,
        filtro_status=status,
        filtro_polo=polo_id,
        filtro_origem=origem,
        filtro_busca=busca,
    )


@bp.route("/novo", methods=["GET", "POST"])
@login_required
def novo():
    if request.method == "POST":
        lead = Lead(
            nome=request.form["nome"].strip(),
            telefone=request.form["telefone"].strip(),
            email=request.form.get("email", "").strip() or None,
            curso_interesse=request.form.get("curso_interesse", "").strip() or None,
            origem=request.form.get("origem", "Outros"),
            status="Novo",
            temperatura=request.form.get("temperatura", "Frio"),
            polo_id=request.form.get("polo_id") or current_user.polo_id,
            responsavel_id=current_user.id,
        )
        db.session.add(lead)
        db.session.commit()
        flash(f"Lead '{lead.nome}' cadastrado com sucesso.", "success")
        return redirect(url_for("leads.detalhe", lead_id=lead.id))

    return render_template(
        "lead_form.html",
        polos=Polo.query.order_by(Polo.nome).all(),
        origem_opcoes=ORIGENS_LEAD,
        temperatura_opcoes=TEMPERATURA_LEAD,
    )


@bp.route("/<int:lead_id>")
@login_required
def detalhe(lead_id):
    lead = Lead.query.get_or_404(lead_id)
    return render_template(
        "lead_detail.html",
        lead=lead,
        status_opcoes=STATUS_LEAD,
        temperatura_opcoes=TEMPERATURA_LEAD,
        canal_opcoes=CANAIS_INTERACAO,
    )


@bp.route("/<int:lead_id>/atualizar", methods=["POST"])
@login_required
def atualizar(lead_id):
    lead = Lead.query.get_or_404(lead_id)
    lead.status = request.form.get("status", lead.status)
    lead.temperatura = request.form.get("temperatura", lead.temperatura)

    proxima = request.form.get("proxima_acao_em", "")
    lead.proxima_acao_em = datetime.strptime(proxima, "%Y-%m-%d").date() if proxima else None

    db.session.commit()
    flash("Lead atualizado.", "success")
    return redirect(url_for("leads.detalhe", lead_id=lead.id))


@bp.route("/<int:lead_id>/interacoes", methods=["POST"])
@login_required
def nova_interacao(lead_id):
    lead = Lead.query.get_or_404(lead_id)
    mensagem = request.form.get("mensagem", "").strip()
    canal = request.form.get("canal", "whatsapp")

    if not mensagem:
        flash("Digite uma mensagem antes de registrar.", "warning")
        return redirect(url_for("leads.detalhe", lead_id=lead.id))

    interacao = Interacao(
        lead_id=lead.id,
        usuario_id=current_user.id,
        canal=canal,
        direcao="enviada",
        mensagem=mensagem,
        origem_automatica=False,
    )
    db.session.add(interacao)
    db.session.commit()
    flash("Interação registrada.", "success")
    return redirect(url_for("leads.detalhe", lead_id=lead.id))
