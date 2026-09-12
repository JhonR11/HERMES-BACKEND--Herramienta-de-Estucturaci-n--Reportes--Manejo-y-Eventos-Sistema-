from sqlalchemy import Enum as SAEnum

from app.domain.value_objects.enums import EstadoEvento, EstadoReporte, RolUsuario, TipoArchivo

rol_usuario_enum = SAEnum(
    RolUsuario,
    name="rol_usuario",
    native_enum=True,
    create_type=False,
    values_callable=lambda x: [e.value for e in x],
)
estado_reporte_enum = SAEnum(
    EstadoReporte,
    name="estado_reporte",
    native_enum=True,
    create_type=False,
    values_callable=lambda x: [e.value for e in x],
)
estado_evento_enum = SAEnum(
    EstadoEvento,
    name="estado_evento",
    native_enum=True,
    create_type=False,
    values_callable=lambda x: [e.value for e in x],
)
tipo_archivo_enum = SAEnum(
    TipoArchivo,
    name="tipo_archivo",
    native_enum=True,
    create_type=False,
    values_callable=lambda x: [e.value for e in x],
)
