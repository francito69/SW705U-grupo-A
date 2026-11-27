"""Errores de dominio y su traducción a respuestas HTTP con mensajes en español."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class ErrorDominio(Exception):
    codigo = 400

    def __init__(self, mensaje: str, **datos):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.datos = datos


class NoEncontrado(ErrorDominio):
    codigo = 404


class Prohibido(ErrorDominio):
    codigo = 403


class Conflicto(ErrorDominio):
    codigo = 409


class ReglaNegocio(ErrorDominio):
    codigo = 422


ETIQUETAS = {
    "tipo_documento": "Tipo de documento",
    "numero_documento": "Número de documento",
    "nombres": "Nombres",
    "apellido_paterno": "Apellido paterno",
    "apellido_materno": "Apellido materno",
    "fecha_nacimiento": "Fecha de nacimiento",
    "telefono": "Teléfono",
    "email": "Correo",
    "direccion": "Dirección",
    "id_convenio": "Convenio",
    "motivo": "Motivo",
    "motivo_consulta": "Motivo de consulta",
    "diagnosticos": "Diagnósticos",
    "codigo_cie10": "Código CIE-10",
    "presion_sistolica": "Presión sistólica",
    "presion_diastolica": "Presión diastólica",
    "temperatura": "Temperatura",
    "frecuencia_cardiaca": "Frecuencia cardiaca",
    "frecuencia_respiratoria": "Frecuencia respiratoria",
    "saturacion_oxigeno": "Saturación de oxígeno",
    "peso": "Peso",
    "talla": "Talla",
    "fecha_hora_inicio": "Fecha y hora",
    "password": "Contraseña",
    "username": "Usuario",
}

MENSAJES = {
    "missing": "es obligatorio",
    "string_too_short": "debe tener al menos {min_length} caracteres",
    "string_too_long": "debe tener como máximo {max_length} caracteres",
    "string_pattern_mismatch": "no tiene el formato correcto",
    "greater_than_equal": "debe ser mayor o igual a {ge}",
    "less_than_equal": "debe ser menor o igual a {le}",
    "greater_than": "debe ser mayor que {gt}",
    "less_than": "debe ser menor que {lt}",
    "int_parsing": "debe ser un número entero",
    "int_from_float": "debe ser un número entero",
    "float_parsing": "debe ser un número",
    "decimal_parsing": "debe ser un número",
    "bool_parsing": "debe ser verdadero o falso",
    "date_parsing": "debe ser una fecha válida (AAAA-MM-DD)",
    "date_from_datetime_parsing": "debe ser una fecha válida (AAAA-MM-DD)",
    "datetime_parsing": "debe ser una fecha y hora válidas",
    "datetime_from_date_parsing": "debe ser una fecha y hora válidas",
    "literal_error": "debe ser uno de: {expected}",
    "enum": "debe ser uno de: {expected}",
    "too_short": "debe tener al menos {min_length} elemento(s)",
    "too_long": "debe tener como máximo {max_length} elemento(s)",
    "json_invalid": "el cuerpo de la solicitud no es un JSON válido",
}


def _campo(loc: tuple) -> str:
    partes = [str(p) for p in loc if p not in ("body", "query", "path")]
    texto = ""
    for parte in partes:
        texto += f"[{parte}]" if parte.isdigit() else (f".{parte}" if texto else parte)
    return texto


def _mensaje(error: dict) -> str:
    tipo = error.get("type", "")
    if tipo == "value_error":
        mensaje = str(error.get("msg", ""))
        if mensaje.startswith("Value error, "):
            return mensaje.removeprefix("Value error, ")
        if "email" in mensaje.lower():
            return "no es un correo electrónico válido"
        return mensaje
    plantilla = MENSAJES.get(tipo)
    if plantilla is None:
        return str(error.get("msg", "valor no válido"))
    try:
        return plantilla.format(**error.get("ctx", {}))
    except (KeyError, IndexError):
        return plantilla


def registrar_manejadores(app: FastAPI) -> None:
    @app.exception_handler(ErrorDominio)
    async def _error_dominio(_: Request, exc: ErrorDominio) -> JSONResponse:
        return JSONResponse(status_code=exc.codigo, content={"detail": exc.mensaje, **exc.datos})

    @app.exception_handler(RequestValidationError)
    async def _error_validacion(_: Request, exc: RequestValidationError) -> JSONResponse:
        errores = []
        for error in exc.errors():
            campo = _campo(tuple(error.get("loc", ())))
            errores.append({"campo": campo, "mensaje": _mensaje(error)})
        primero = errores[0] if errores else {"campo": "", "mensaje": "datos no válidos"}
        nombre = primero["campo"].split(".")[-1].split("[")[0]
        etiqueta = ETIQUETAS.get(nombre, primero["campo"])
        detalle = f"{etiqueta}: {primero['mensaje']}" if etiqueta else primero["mensaje"]
        return JSONResponse(status_code=422, content={"detail": detalle, "errores": errores})
