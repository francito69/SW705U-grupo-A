"""Edad cumplida del paciente a una fecha dada: valores limite (tabla 2.2)."""

from datetime import date

import pytest

from backend.core.tiempo import calcular_edad

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    ("nacimiento", "referencia", "esperada"),
    [
        pytest.param(date(1990, 5, 14), date(2026, 5, 14), 36, id="E-01-cumple-anos-ese-dia"),
        pytest.param(date(1990, 5, 14), date(2026, 5, 13), 35, id="E-02-un-dia-antes-del-cumpleanos"),
        pytest.param(date(1990, 5, 14), date(2026, 5, 15), 36, id="E-03-un-dia-despues-del-cumpleanos"),
        pytest.param(date(2026, 11, 22), date(2026, 11, 22), 0, id="E-04-nacido-el-mismo-dia"),
        pytest.param(date(2004, 2, 29), date(2027, 2, 28), 22, id="E-06-29-feb-en-ano-no-bisiesto"),
        pytest.param(date(2004, 2, 29), date(2027, 3, 1), 23, id="E-07-29-feb-cumple-el-1-mar"),
        pytest.param(date(2000, 12, 31), date(2026, 1, 1), 25, id="E-08-cambio-de-ano"),
    ],
)
def test_edad_cumplida_en_los_limites(nacimiento, referencia, esperada):
    assert calcular_edad(nacimiento, referencia) == esperada


def test_fecha_de_nacimiento_futura_se_rechaza():
    with pytest.raises(ValueError, match="posterior"):
        calcular_edad(date(2026, 11, 23), date(2026, 11, 22))
