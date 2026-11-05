def test_pagina_de_leads_exige_login(client):
    resposta = client.get("/leads/", follow_redirects=True)
    assert resposta.status_code == 200
    assert "Entrar no CRM".encode() in resposta.data


def test_login_com_credenciais_corretas(client):
    resposta = client.post(
        "/login", data={"email": "teste@crm.com", "senha": "senha123"}, follow_redirects=True
    )
    assert resposta.status_code == 200
    assert "Dashboard".encode() in resposta.data


def test_login_com_senha_errada_mostra_erro(client):
    resposta = client.post(
        "/login", data={"email": "teste@crm.com", "senha": "errada"}, follow_redirects=True
    )
    assert "inválidos".encode() in resposta.data


def test_criar_lead_via_formulario(cliente_autenticado):
    resposta = cliente_autenticado.post(
        "/leads/novo",
        data={"nome": "Novo Lead", "telefone": "18988887777", "origem": "Site", "temperatura": "Frio"},
        follow_redirects=True,
    )
    assert resposta.status_code == 200
    assert "Novo Lead".encode() in resposta.data


def test_registrar_interacao_no_lead(cliente_autenticado):
    cliente_autenticado.post(
        "/leads/novo",
        data={"nome": "Lead Interacao", "telefone": "18977776666", "origem": "Site", "temperatura": "Frio"},
    )
    resposta = cliente_autenticado.post(
        "/leads/1/interacoes",
        data={"canal": "whatsapp", "mensagem": "Olá, tudo bem?"},
        follow_redirects=True,
    )
    assert resposta.status_code == 200
    assert "Olá, tudo bem?".encode() in resposta.data
