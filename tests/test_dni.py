"""HU03 - Formato del DNI del paciente: particion de equivalencia y valores limite (tabla 2.1)."""

import pytest
from pydantic import ValidationError

from app.modulos.hce.schemas import PacienteCrear

pytestmark = pytest.mark.unit

FILIACION = {
    "tipo_documento": "DNI",
    "nombres": "Lucia",
    "apellido_paterno": "Prueba",
    "apellido_materno": "Ficticia",
    "fecha_nacimiento": "1990-05-14",
    "sexo": "F",
    "telefono": "987654321",
    "id_convenio": 1,
}


def _paciente(**cambios) -> PacienteCrear:
    return PacienteCrear(**{**FILIACION, "numero_documento": "45871236", **cambios})


@pytest.mark.parametrize(
    ("entrada", "guardado"),
    [
        pytest.param("45871236", "45871236", id="D-01-ocho-digitos"),
        pytest.param("01234567", "01234567", id="D-02-empieza-con-cero"),
        pytest.param(" 45871236 ", "45871236", id="D-08-espacios-al-inicio-y-al-final"),
    ],
)
def test_dni_valido_se_acepta(entrada, guardado):
    assert _paciente(numero_documento=entrada).numero_documento == guardado


@pytest.mark.parametrize(
    "entrada",
    [
        pytest.param("4587123", id="D-03-siete-digitos"),
        pytest.param("458712369", id="D-04-nueve-digitos"),
        pytest.param("4587123A", id="D-05-con-letra"),
        pytest.param("", id="D-06-vacio"),
        pytest.param("4587 1236", id="D-07-espacio-interno"),
        pytest.param("４５８７１２３６", id="D-09-digitos-de-ancho-completo"),
        pytest.param("٤٥٨٧١٢٣٦", id="D-10-digitos-arabigos"),
    ],
)
def test_dni_invalido_se_rechaza(entrada):
    with pytest.raises(ValidationError, match="El DNI debe tener 8 dígitos"):
        _paciente(numero_documento=entrada)


@pytest.mark.parametrize(
    "entrada",
    [
        pytest.param("9８７６５４３２１", id="celular-ancho-completo"),
        pytest.param("9٨٧٦٥٤٣٢١", id="celular-arabigo"),
    ],
)
def test_celular_con_digitos_unicode_se_rechaza(entrada):
    with pytest.raises(ValidationError, match="El celular debe tener 9 dígitos"):
        _paciente(telefono=entrada)
