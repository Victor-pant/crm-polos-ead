from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user

from extensions import db
from models import Usuario

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")

        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and usuario.checar_senha(senha):
            login_user(usuario)
            proximo = request.args.get("next")
            return redirect(proximo or url_for("dashboard.index"))

        flash("E-mail ou senha inválidos.", "danger")

    return render_template("login.html")


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você saiu do sistema.", "info")
    return redirect(url_for("auth.login"))
