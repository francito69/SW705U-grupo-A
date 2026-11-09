def test_salud_responde_ok(client):
    respuesta = client.get("/salud")

    assert respuesta.status_code == 200
    assert respuesta.json() == {"estado": "ok"}


def test_lista_los_convenios_ficticios(client):
    respuesta = client.get("/convenios")

    assert respuesta.status_code == 200
    codigos = [convenio["codigo_convenio"] for convenio in respuesta.json()]
    assert len(codigos) == 7
    assert codigos[0] == "PARTICULAR"
    assert "SOAT" in codigos
