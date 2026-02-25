# Mini Integrator – API → SQLite → Monitoring

Mini integrador que consume datos desde una API pública (JSONPlaceholder), aplica transformación/mapeo, persiste en base de datos local (SQLite) con idempotencia (upsert) y expone monitoreo básico mediante métricas Prometheus y un endpoint de healthcheck.

---

## Objetivo

Demostrar integración entre:

API pública → Transformación de datos → Base de datos local → Monitoreo del proceso

---

## Fuente de datos

API utilizada:
https://jsonplaceholder.typicode.com/

Endpoints consumidos:
- GET /users
- GET /posts

---

## Arquitectura

```
mini-integrator/
│
├── src/
│   ├── __init__.py
│   ├── app.py
│   ├── db.py
│   ├── http_client.py
│   ├── transform.py
│   ├── repository.py
│   ├── metrics.py
│   └── sync.py
│
├── models.sql
├── requirements.txt
├── .env.example
├── README.md
└── .gitignore
```

---

## Requisitos

- Python 3.10+ (probado con 3.11)
- Windows
- pip
- (Opcional) Anaconda

---

## Instalación

### Crear entorno (Conda)

conda create -n mini_integrator python=3.11
conda activate mini_integrator

### O con venv

python -m venv venv
venv\Scripts\activate

### Instalar dependencias

pip install -r requirements.txt

---

## Configuración

Copiar archivo de variables:

copy .env.example .env

Variables principales:

- API_BASE_URL
- SOURCE_NAME
- SQLITE_PATH
- HTTP_TIMEOUT_SECONDS
- HTTP_MAX_RETRIES
- HTTP_BACKOFF_BASE_SECONDS
- PROMETHEUS_MULTIPROC_DIR

---

## Inicializar base de datos

La base se crea automáticamente al ejecutar el sync.

Manual:

python src\db.py

---

## Ejecutar sincronización manual

python src\sync.py

El proceso:

- Consume /users y /posts
- Aplica transformación
- Realiza upsert (evita duplicados)
- Relaciona posts con usuarios
- Registra logs
- Actualiza métricas

---

## Idempotencia

Se define una llave de negocio:

UNIQUE(source, external_id)

Persistencia:

INSERT ... ON CONFLICT(source, external_id) DO UPDATE

Ejecutar múltiples veces el proceso no genera duplicados.

---

## Transformación / Mapeo aplicado

No se guarda únicamente el payload crudo.

### Users

- source
- external_id
- full_name (normalizado)
- username_norm (lowercase)
- email_norm (lowercase)
- city
- synced_at (ISO UTC)
- raw_payload (JSON original)

### Posts

- source
- external_id
- external_user_id
- title_norm (lowercase)
- body_clean (limpieza de texto)
- synced_at
- raw_payload

Relación:

posts.user_id es FK local resuelta por (source, external_user_id)

---

## Logs

Se registran:

- Inicio de ejecución
- Cantidad procesada
- Cantidad upserted
- Duración total
- Errores con stacktrace

---

## Monitoreo

Endpoints:

GET /health
GET /metrics

Modo multiproceso (recomendado)

### Consola A (Servidor)

conda activate mini_integrator
cd C:\Users\User\mini-integrator
set PROMETHEUS_MULTIPROC_DIR=%CD%\metrics_data
uvicorn src.app:app --host 0.0.0.0 --port 8000

### Consola B (Sync)

conda activate mini_integrator
cd C:\Users\User\mini-integrator
set PROMETHEUS_MULTIPROC_DIR=%CD%\metrics_data
python src\sync.py

Ver métricas:

http://localhost:8000/metrics

Métricas expuestas:

- integration_runs_total
- integration_runs_success_total
- integration_runs_failed_total
- integration_records_processed_total
- integration_records_upserted_total
- integration_run_duration_seconds

---

## Evidencia de ejecución exitosa

Start sync source=jsonplaceholder api_base=https://jsonplaceholder.typicode.com
Fetched users=10 posts=100
Sync success run_id=2 upserted_users=10 upserted_posts=100 duration_ms=960

---

## Cumplimiento de requisitos

✔ Consumo API REST pública  
✔ Transformación antes de persistencia  
✔ Persistencia en base local  
✔ Idempotencia (source + external_id)  
✔ Logs  
✔ Ejecución manual  
✔ Monitoreo Prometheus  
✔ Relación usuarios–posts  
✔ Manejo de errores HTTP + retry/backoff  

---

## Decisiones técnicas

Se utilizó SQLite para simplificar instalación local y cumplir con el alcance en el tiempo sugerido (6–10 horas), manteniendo arquitectura modular que permitiría migración sencilla a PostgreSQL o integración en Django si fuese requerido.


