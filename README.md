## Arranque inmediato

Guía completa de instalación y ejecución desde cero: [GUIA_PUESTA_EN_MARCHA.md](GUIA_PUESTA_EN_MARCHA.md).

```bash
docker compose up --build
```

Al terminar:

| Recurso | URL |
|---|---|
| Swagger | http://localhost:8000/docs |
| OpenAPI | http://localhost:8000/openapi.json |
| Health | http://localhost:8000/health |
| WebSocket de eventos | ws://localhost:8000/api/v1/ws/eventos |

Credenciales del administrador (seed automático):

- **Correo:** `admin@institucion.edu.co`
- **Contraseña:** `changeme` (`ADMIN_EMAIL` / `ADMIN_PASSWORD` en `.env`)

La contraseña se hashea con **bcrypt** en el seed; no hay hashes de ejemplo en SQL.

## Flujo mínimo de verificación

1. `POST /api/v1/auth/login` con el administrador.
2. `POST /api/v1/docentes` (Bearer admin) con nombre, correo y cédula. La contraseña inicial del docente **es su cédula**.
3. `POST /api/v1/auth/login` como docente.
4. `GET /api/v1/reportes/categorias` y `POST /api/v1/reportes`.
5. `GET /api/v1/public/reportes` (sin token) debe mostrar el reporte `ACTIVO`.

### Cambio de contraseña por correo

Configura `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD` y
`SMTP_FROM_EMAIL` en `.env`. Luego el docente solicita el enlace con:

```text
POST /api/v1/auth/password-reset/request
{"correo_institucional": "docente@institucion.edu.co"}
```

El correo contiene un token de un solo uso. La aplicación cliente debe enviar
ese token junto con la nueva contraseña a:

```text
POST /api/v1/auth/password-reset/confirm
{"token": "...", "password_nueva": "nueva-clave-segura"}
```

Los tokens expiran en `PASSWORD_RESET_TOKEN_EXPIRE_MINUTES` (30 minutos por
defecto). Al completar el cambio se revocan los refresh tokens existentes.

Colección Postman: `postman_collection.json` (variables `base_url`, `token_admin`, `token_docente`).

## Decisiones de diseño

- **Eventos vencidos:** doble mecanismo. El listado público exige `estado = ACTIVO` y `fecha_fin > now()`. Además, un worker al arranque (cada `EVENT_EXPIRY_POLL_SECONDS`) marca `DESHABILITADO` los vencidos y notifica por WebSocket.
- **WebSocket vs SSE:** se usa WebSocket en `/api/v1/ws/eventos` porque el requisito pide difusión en tiempo real hacia la página principal y WS cubre reconexión y mensajes de control sin un canal extra.
- **Archivos:** `LocalStorageService` guarda en `UPLOAD_DIR` (`/uploads` en Docker) y se sirve en `/uploads`. El puerto de `StorageService` permite sustituirlo por S3/MinIO sin tocar casos de uso.
- **Migraciones:** Alembic `0001` replica el DDL de PostgreSQL (enums, FKs, índices, triggers, seed de categorías). El administrador se inserta después con hash real.

## Desarrollo local (sin Docker para la API)

PostgreSQL debe estar disponible y `DB_HOST=localhost` en `.env`.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
python -m app.infrastructure.db.seed
uvicorn app.presentation.main:app --reload --port 8000
```
