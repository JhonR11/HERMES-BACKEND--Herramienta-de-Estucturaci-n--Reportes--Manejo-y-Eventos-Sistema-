"""Esquema inicial exacto de PostgreSQL (enums, tablas, índices, triggers y seed de categorías).

Revision ID: 0001_esquema_inicial
Revises:
Create Date: 2026-09-12

"""

from alembic import op

revision = "0001_esquema_inicial"
down_revision = None
branch_labels = None
depends_on = None


DDL = r"""
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TYPE rol_usuario AS ENUM ('ADMINISTRADOR', 'DOCENTE');
CREATE TYPE estado_reporte AS ENUM ('ACTIVO', 'DESHABILITADO');
CREATE TYPE estado_evento AS ENUM ('ACTIVO', 'DESHABILITADO');
CREATE TYPE tipo_archivo AS ENUM ('IMAGEN', 'PDF');

CREATE TABLE usuarios (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre                VARCHAR(150) NOT NULL,
    correo_institucional  VARCHAR(150) NOT NULL UNIQUE,
    cedula_ciudadania     VARCHAR(20)  UNIQUE,
    password_hash         VARCHAR(255) NOT NULL,
    rol                   rol_usuario  NOT NULL,
    activo                BOOLEAN      NOT NULL DEFAULT TRUE,
    creado_en             TIMESTAMPTZ  NOT NULL DEFAULT now(),
    actualizado_en        TIMESTAMPTZ  NOT NULL DEFAULT now()
);
CREATE INDEX idx_usuarios_rol ON usuarios (rol);
CREATE INDEX idx_usuarios_correo ON usuarios (correo_institucional);

CREATE TABLE categorias_reporte (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre        VARCHAR(100) NOT NULL UNIQUE,
    descripcion   VARCHAR(255)
);
INSERT INTO categorias_reporte (nombre) VALUES
    ('Proyección social'), ('Regionalización'), ('Política lingüística'),
    ('Sector externo'), ('Movilidad académica');

CREATE TABLE reportes (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre_reporte        VARCHAR(200) NOT NULL,
    descripcion_detallada TEXT         NOT NULL,
    categoria_id          UUID         NOT NULL REFERENCES categorias_reporte(id) ON DELETE RESTRICT,
    creado_por            UUID         NOT NULL REFERENCES usuarios(id) ON DELETE RESTRICT,
    estado                estado_reporte NOT NULL DEFAULT 'ACTIVO',
    creado_en             TIMESTAMPTZ  NOT NULL DEFAULT now(),
    actualizado_en        TIMESTAMPTZ  NOT NULL DEFAULT now()
);
CREATE INDEX idx_reportes_categoria ON reportes (categoria_id);
CREATE INDEX idx_reportes_creado_por ON reportes (creado_por);
CREATE INDEX idx_reportes_estado ON reportes (estado);
CREATE INDEX idx_reportes_creado_en ON reportes (creado_en);

CREATE TABLE reporte_docentes (
    reporte_id   UUID NOT NULL REFERENCES reportes(id) ON DELETE CASCADE,
    docente_id   UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    asignado_en  TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (reporte_id, docente_id)
);
CREATE INDEX idx_reporte_docentes_docente ON reporte_docentes (docente_id);

CREATE TABLE reporte_archivos (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reporte_id       UUID NOT NULL REFERENCES reportes(id) ON DELETE CASCADE,
    tipo_archivo     tipo_archivo NOT NULL,
    nombre_original  VARCHAR(255) NOT NULL,
    ruta_almacenada  VARCHAR(500) NOT NULL,
    url_publica      VARCHAR(500),
    tamano_bytes     INTEGER,
    subido_en        TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_reporte_archivos_reporte ON reporte_archivos (reporte_id);
CREATE INDEX idx_reporte_archivos_tipo ON reporte_archivos (tipo_archivo);

CREATE TABLE eventos (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre_evento  VARCHAR(200) NOT NULL,
    descripcion    TEXT NOT NULL,
    foto_url       VARCHAR(500),
    fecha_inicio   TIMESTAMPTZ NOT NULL,
    fecha_fin      TIMESTAMPTZ NOT NULL,
    estado         estado_evento NOT NULL DEFAULT 'ACTIVO',
    creado_por     UUID NOT NULL REFERENCES usuarios(id) ON DELETE RESTRICT,
    creado_en      TIMESTAMPTZ NOT NULL DEFAULT now(),
    actualizado_en TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT chk_fechas_evento CHECK (fecha_fin > fecha_inicio)
);
CREATE INDEX idx_eventos_estado ON eventos (estado);
CREATE INDEX idx_eventos_fecha_fin ON eventos (fecha_fin);

CREATE TABLE noticias (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    titular              VARCHAR(200) NOT NULL,
    descripcion_noticia  TEXT NOT NULL,
    link_opcional        VARCHAR(500),
    foto_url             VARCHAR(500),
    creado_por           UUID NOT NULL REFERENCES usuarios(id) ON DELETE RESTRICT,
    creado_en            TIMESTAMPTZ NOT NULL DEFAULT now(),
    actualizado_en       TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_noticias_creado_en ON noticias (creado_en);

CREATE TABLE refresh_tokens (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id   UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    token        VARCHAR(500) NOT NULL UNIQUE,
    expira_en    TIMESTAMPTZ NOT NULL,
    revocado     BOOLEAN NOT NULL DEFAULT FALSE,
    creado_en    TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_refresh_tokens_usuario ON refresh_tokens (usuario_id);

CREATE OR REPLACE FUNCTION set_actualizado_en()
RETURNS TRIGGER AS $$
BEGIN
    NEW.actualizado_en = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_usuarios_actualizado_en BEFORE UPDATE ON usuarios FOR EACH ROW EXECUTE FUNCTION set_actualizado_en();
CREATE TRIGGER trg_reportes_actualizado_en BEFORE UPDATE ON reportes FOR EACH ROW EXECUTE FUNCTION set_actualizado_en();
CREATE TRIGGER trg_eventos_actualizado_en BEFORE UPDATE ON eventos FOR EACH ROW EXECUTE FUNCTION set_actualizado_en();
CREATE TRIGGER trg_noticias_actualizado_en BEFORE UPDATE ON noticias FOR EACH ROW EXECUTE FUNCTION set_actualizado_en();
"""


def _split_sql_statements(sql: str) -> list[str]:
    statements: list[str] = []
    start = 0
    index = 0
    single_quote = False
    dollar_quote: str | None = None

    while index < len(sql):
        character = sql[index]
        if dollar_quote:
            if sql.startswith(dollar_quote, index):
                index += len(dollar_quote)
                dollar_quote = None
                continue
        elif character == "'":
            if single_quote and index + 1 < len(sql) and sql[index + 1] == "'":
                index += 2
                continue
            single_quote = not single_quote
        elif not single_quote and character == "$":
            end = sql.find("$", index + 1)
            if end != -1:
                dollar_quote = sql[index : end + 1]
                index = end
        elif not single_quote and character == ";":
            statement = sql[start:index].strip()
            if statement:
                statements.append(statement)
            start = index + 1
        index += 1

    statement = sql[start:].strip()
    if statement:
        statements.append(statement)
    return statements


def upgrade() -> None:
    for statement in _split_sql_statements(DDL):
        op.execute(statement)


def downgrade() -> None:
    downgrade_ddl = """
        DROP TRIGGER IF EXISTS trg_noticias_actualizado_en ON noticias;
        DROP TRIGGER IF EXISTS trg_eventos_actualizado_en ON eventos;
        DROP TRIGGER IF EXISTS trg_reportes_actualizado_en ON reportes;
        DROP TRIGGER IF EXISTS trg_usuarios_actualizado_en ON usuarios;
        DROP FUNCTION IF EXISTS set_actualizado_en();
        DROP TABLE IF EXISTS refresh_tokens;
        DROP TABLE IF EXISTS noticias;
        DROP TABLE IF EXISTS eventos;
        DROP TABLE IF EXISTS reporte_archivos;
        DROP TABLE IF EXISTS reporte_docentes;
        DROP TABLE IF EXISTS reportes;
        DROP TABLE IF EXISTS categorias_reporte;
        DROP TABLE IF EXISTS usuarios;
        DROP TYPE IF EXISTS tipo_archivo;
        DROP TYPE IF EXISTS estado_evento;
        DROP TYPE IF EXISTS estado_reporte;
        DROP TYPE IF EXISTS rol_usuario;
        """
    for statement in _split_sql_statements(downgrade_ddl):
        op.execute(statement)
