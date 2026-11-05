def test_api_sem_token_retorna_401(client):
    resposta = client.get("/api/leads")
    assert resposta.status_code == 401


def test_api_criar_e_listar_lead(client, api_headers):
    resposta_criar = client.post(
        "/api/leads",
        json={"nome": "Lead via API", "telefone": "18966665555", "origem": "WhatsApp"},
        headers=api_headers,
    )
    assert resposta_criar.status_code == 201
    lead_id = resposta_criar.get_json()["id"]

    resposta_listar = client.get("/api/leads", headers=api_headers)
    assert resposta_listar.status_code == 200
    nomes = [lead["nome"] for lead in resposta_listar.get_json()]
    assert "Lead via API" in nomes


def test_api_registrar_interacao_automatica(client, api_headers):
    resposta_criar = client.post(
        "/api/leads",
        json={"nome": "Lead Automacao", "telefone": "18955554444"},
        headers=api_headers,
    )
    lead_id = resposta_criar.get_json()["id"]

    resposta_interacao = client.post(
        f"/api/leads/{lead_id}/interacoes",
        json={"mensagem": "Mensagem registrada por integração externa", "direcao": "recebida"},
        headers=api_headers,
    )
    assert resposta_interacao.status_code == 201
    corpo = resposta_interacao.get_json()
    assert corpo["origem_automatica"] is True

