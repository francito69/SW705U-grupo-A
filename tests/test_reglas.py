"""Pruebas unitarias de las reglas de dominio (sin HTTP)."""

from datetime import date, datetime

import pytest

from app.core import tiempo
from app.core.errores import ReglaNegocio, _campo, _mensaje
from app.core.texto import normalizar
from app.modulos.agenda.service import turnos_del_dia, validar_horario
from app.modulos.auditoria.service import ip_valida
from app.modulos.convenios.service import calcular_copago
from app.modulos.hce.models import Triaje
from app.modulos.hce.service import alertas_triaje, coincidencias_alergia, imc

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    ("precio", "cobertura", "fijo", "esperado"),
    [
        (80, 80, 20, (48.0, 32.0)),
        (80, 75, 15, (48.75, 31.25)),
        (140, 85, 25, (97.75, 42.25)),
        (100, 100, 0, (100.0, 0.0)),
        (80, 0, 0, (0.0, 80.0)),
        (10, 50, 20, (0.0, 10.0)),
    ],
)
def test_copago_segun_rn03(precio, cobertura, fijo, esperado):
    assert calcular_copago(precio, cobertura, fijo) == esperado


def test_turnos_de_lunes_a_sabado():
    jueves = turnos_del_dia(date(2026, 11, 12))

    assert len(jueves) == 20
    assert jueves[0][1].strftime("%H:%M") == "08:00"
    assert jueves[9][1].strftime("%H:%M") == "12:30"
    assert jueves[10][1].strftime("%H:%M") == "14:00"
    assert jueves[-1][1].strftime("%H:%M") == "18:30"
    assert turnos_del_dia(date(2026, 11, 15)) == []


def test_validar_horario_rechaza_bloques_irregulares():
    with pytest.raises(ReglaNegocio):
        validar_horario(datetime(2030, 1, 7, 9, 10))


@pytest.mark.parametrize(
    ("alergias", "medicamento", "coincide"),
    [
        ("Penicilina y sulfas", "Amoxicilina 500 mg", True),
        ("Penicilina y sulfas", "Cotrimoxazol forte", True),
        ("AINEs", "Ibuprofeno", True),
        ("Ácido acetilsalicílico", "Aspirina 100 mg", True),
        ("Ácido acetilsalicílico", "Ácido fólico", False),
        ("Ibuprofeno", "Ibuprofeno 400 mg", True),
        ("Látex", "Paracetamol", False),
        (None, "Paracetamol", False),
    ],
)
def test_coincidencias_de_alergia(alergias, medicamento, coincide):
    assert bool(coincidencias_alergia(alergias, [medicamento])) is coincide


def test_alertas_e_imc_del_triaje():
    triaje = Triaje(
        presion_sistolica=150,
        presion_diastolica=85,
        temperatura=38.5,
        frecuencia_cardiaca=90,
        saturacion_oxigeno=95,
        peso=80,
        talla=1.75,
    )

    assert alertas_triaje(triaje) == ["Presión arterial elevada (150/85 mmHg)", "Fiebre (38.5 °C)"]
    assert imc(triaje) == 26.1


def test_utilidades():
    assert normalizar("  Hipertensión   Arterial ") == "hipertension arterial"
    assert tiempo.edad(date(2000, 12, 31), date(2026, 11, 12)) == 25
    assert ip_valida("testclient") == "0.0.0.0"
    assert ip_valida("10.20.1.15") == "10.20.1.15"


def test_mensajes_de_validacion_en_espanol():
    assert _campo(("body", "diagnosticos", 0, "codigo_cie10")) == "diagnosticos[0].codigo_cie10"
    assert _mensaje({"type": "missing"}) == "es obligatorio"
    assert _mensaje({"type": "string_too_short", "ctx": {"min_length": 3}}) == "debe tener al menos 3 caracteres"
    assert _mensaje({"type": "value_error", "msg": "Value error, Texto propio"}) == "Texto propio"
    assert _mensaje({"type": "desconocido", "msg": "otro"}) == "otro"
