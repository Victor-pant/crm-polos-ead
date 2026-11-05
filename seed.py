"""
Recria o banco de dados com dados fictícios de demonstração: 2 polos, 1 usuária
de teste e 24 leads em diferentes estágios, com histórico de interações.

    python seed.py
"""
from app import create_app
from extensions import db
from demo_data import popular_demo

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()
    popular_demo()
    print("Banco de dados populado com sucesso: 2 polos, 1 usuário e 24 leads de exemplo.")
    print("Login: maria@unoeste-pi.com.br / senha: 123456")
