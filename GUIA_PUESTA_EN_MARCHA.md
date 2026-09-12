# Guía de puesta en marcha

Esta guía explica cómo preparar, ejecutar y verificar el backend desde cero en Windows, macOS o Linux. El proyecto es una API de FastAPI que usa PostgreSQL, Alembic, JWT y almacenamiento local de archivos.

## 1. Requisitos

Instala lo siguiente antes de comenzar:

- Git.
- Docker Desktop, con Docker Compose habilitado (opción recomendada).
- O bien Python 3.12 y PostgreSQL 16 para ejecutar la API sin Docker.

Comprueba las instalaciones:

```bash
git --version
docker --version
docker compose version
```

Para la alternativa local:

```bash
python --version
psql --version
```

## 2. Obtener el código

Clona el repositorio y entra en la carpeta del backend:

```bash
git clone <URL_DEL_REPOSITORIO>
cd backend
```

Si ya tienes el código, abre una terminal en la carpeta que contiene `docker-compose.yml` y `requirements.txt`.

## 3. Crear la configuración

En Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

En macOS o Linux:

```bash
cp .env.example .env
```

La configuración incluida permite iniciar el proyecto rápidamente. Antes de usarlo fuera de desarrollo, cambia al menos:

- `JWT_SECRET_KEY`: una clave larga y aleatoria.
- `ADMIN_PASSWORD`: la contraseña inicial del administrador.
- `DB_PASSWORD`: la contraseña de PostgreSQL.
- `CORS_ORIGINS`: los orígenes permitidos por el frontend, separados por comas.

No subas `.env` al repositorio ni compartas sus secretos.

## 4. Ejecutar con Docker (recomendado)

Con Docker Desktop iniciado, ejecuta:

```bash
docker compose up --build
```

Este comando:

1. Construye la imagen de Python 3.12.
2. Inicia PostgreSQL 16.
3. Espera a que PostgreSQL responda.
4. Ejecuta `alembic upgrade head` para crear o actualizar el esquema.
5. Inserta el administrador inicial si todavía no existe.
6. Arranca la API en el puerto `8000`.

Para dejar los servicios ejecutándose en segundo plano:

```bash
docker compose up --build -d
```

Para ver los registros:

```bash
docker compose logs -f api
```

Para detener los servicios sin borrar los datos:

```bash
docker compose down
```

Para borrar también la base de datos y los archivos subidos almacenados en volúmenes Docker:

```bash
docker compose down -v
```

## 5. Verificar que funciona

Cuando el contenedor de la API esté listo, abre:

| Recurso | Dirección |
| --- | --- |
| Swagger UI | http://localhost:8000/docs |
| OpenAPI | http://localhost:8000/openapi.json |
| Healthcheck | http://localhost:8000/health |
| WebSocket | ws://localhost:8000/api/v1/ws/eventos |

El healthcheck debe responder:

```json
{"status":"ok"}
```

Credenciales iniciales, tomadas de `.env`:

- Correo: `admin@institucion.edu.co`
- Contraseña: `changeme`

En un entorno real, utiliza los valores que hayas configurado en `ADMIN_EMAIL` y `ADMIN_PASSWORD`.

## 6. Flujo funcional mínimo

Puedes probar la API desde Swagger o con `postman_collection.json`:

1. Ejecuta `POST /api/v1/auth/login` con las credenciales del administrador.
2. Usa el token como `Bearer` y ejecuta `POST /api/v1/docentes`.
3. Inicia sesión con el docente creado. Su contraseña inicial es su cédula.
4. Consulta `GET /api/v1/reportes/categorias`.
5. Crea un reporte mediante `POST /api/v1/reportes`.
6. Comprueba el listado público con `GET /api/v1/public/reportes`.

La colección de Postman utiliza las variables `base_url`, `token_admin` y `token_docente`.

## 7. Ejecutar sin Docker

Este modo requiere que PostgreSQL esté instalado y ejecutándose.

### 7.1 Crear la base de datos

Crea una base de datos y un usuario que coincidan con los valores de `.env`. Por ejemplo, desde `psql`:

```sql
CREATE USER app_user WITH PASSWORD 'changeme';
CREATE DATABASE reportes_db OWNER app_user;
```

En `.env`, cambia `DB_HOST` a `localhost` y conserva `DB_PORT=5432`. También puedes definir directamente `DATABASE_URL`:

```dotenv
DATABASE_URL=postgresql+asyncpg://app_user:changeme@localhost:5432/reportes_db
```

### 7.2 Crear el entorno e instalar dependencias

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Si PowerShell bloquea la activación, ejecuta una vez:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

macOS o Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 7.3 Migrar, crear el administrador y arrancar

```bash
alembic upgrade head
python -m app.infrastructure.db.seed
uvicorn app.presentation.main:app --reload --port 8000
```

La API quedará disponible en `http://localhost:8000`. Mantén la terminal abierta mientras desarrollas.

## 8. Ejecutar las pruebas

Con el entorno virtual activo:

```bash
pytest
```

También puedes ejecutar una prueba concreta:

```bash
pytest tests/test_password.py -q
```

## 9. Comandos útiles de mantenimiento

Ver el estado de los contenedores:

```bash
docker compose ps
```

Reconstruir la API después de cambiar dependencias o el Dockerfile:

```bash
docker compose build --no-cache api
docker compose up
```

Aplicar nuevas migraciones existentes:

```bash
docker compose exec api alembic upgrade head
```

Crear una migración después de modificar los modelos requiere revisar el archivo generado antes de aplicarlo:

```bash
docker compose exec api alembic revision --autogenerate -m "descripcion del cambio"
docker compose exec api alembic upgrade head
```

## 10. Problemas frecuentes

### El puerto 8000 o 5432 ya está ocupado

Cambia el puerto público en `.env` y vuelve a iniciar:

```dotenv
PORT=8001
DB_PORT=5433
```

`DB_PORT` solo debe cambiarse si también cambias el puerto publicado de PostgreSQL o si usas la ejecución local. Dentro de Docker, la API se conecta al servicio `db` por el puerto interno `5432`.

### Docker no encuentra `.env`

Confirma que `.env` está en la misma carpeta que `docker-compose.yml` y que fue creado a partir de `.env.example`.

### La API no conecta con PostgreSQL

Revisa los registros:

```bash
docker compose logs db
docker compose logs api
```

En Docker, `DB_HOST` debe ser `db`. En ejecución local, debe ser `localhost`.

### Cambiaste la contraseña del administrador y no se actualiza

El seed solo crea el administrador si no existe. Cambiar `ADMIN_PASSWORD` no modifica un usuario ya creado. Para desarrollo, puedes eliminar el volumen y levantar de nuevo:

```bash
docker compose down -v
docker compose up --build
```

Esto borra todos los datos locales de PostgreSQL y los archivos subidos.
