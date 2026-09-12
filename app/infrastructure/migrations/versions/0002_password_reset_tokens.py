"""Añade tokens de un solo uso para recuperación de contraseña."""

from alembic import op


revision = "0002_password_reset_tokens"
down_revision = "0001_esquema_inicial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE password_reset_tokens (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            usuario_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
            token_hash VARCHAR(64) NOT NULL UNIQUE,
            expira_en TIMESTAMPTZ NOT NULL,
            usado BOOLEAN NOT NULL DEFAULT FALSE,
            creado_en TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )
    op.execute(
        "CREATE INDEX idx_password_reset_tokens_usuario ON password_reset_tokens (usuario_id)"
    )
    op.execute(
        "CREATE INDEX idx_password_reset_tokens_expira ON password_reset_tokens (expira_en)"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS password_reset_tokens")