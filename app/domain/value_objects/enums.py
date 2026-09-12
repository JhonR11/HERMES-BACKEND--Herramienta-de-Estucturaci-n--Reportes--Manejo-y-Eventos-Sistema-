from enum import StrEnum


class RolUsuario(StrEnum):
    ADMINISTRADOR = "ADMINISTRADOR"
    DOCENTE = "DOCENTE"


class EstadoReporte(StrEnum):
    ACTIVO = "ACTIVO"
    DESHABILITADO = "DESHABILITADO"


class EstadoEvento(StrEnum):
    ACTIVO = "ACTIVO"
    DESHABILITADO = "DESHABILITADO"


class TipoArchivo(StrEnum):
    IMAGEN = "IMAGEN"
    PDF = "PDF"
