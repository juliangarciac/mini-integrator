\# Mini Integrator – API → SQLite → Monitoring



Mini integrador que consume datos desde una API pública (JSONPlaceholder), aplica transformación/mapeo, persiste en base de datos local (SQLite) con idempotencia (upsert) y expone monitoreo básico mediante métricas Prometheus y un endpoint de healthcheck.



---



\## 🎯 Objetivo



Demostrar integración entre:



API pública → Transformación de datos → Base de datos local → Monitoreo del proceso



---



\## 🔗 Fuente de datos



API utilizada:

\- https://jsonplaceholder.typicode.com/



Endpoints consumidos:

\- GET /users

\- GET /posts



---



\## 🏗 Arquitectura





mini-integrator/

│

├── src/

│ ├── init.py

│ ├── app.py # API monitoreo (/health, /metrics)

│ ├── db.py # Conexión SQLite + init schema

│ ├── http\_client.py # Cliente HTTP con retry + backoff

│ ├── transform.py # Reglas de transformación/mapeo

│ ├── repository.py # Persistencia + upsert + relaciones

│ ├── metrics.py # Métricas Prometheus

│ └── sync.py # Proceso manual de sincronización

│

├── models.sql

├── requirements.txt

├── .env.example

├── README.md

└── .gitignore





---



\## ⚙️ Requisitos



\- Python 3.10+ (probado con 3.11)

\- Windows

\- pip

\- (Opcional) Anaconda para entorno virtual



---



\## 📦 Instalación



\### 1️⃣ Crear entorno



Conda:



```bat

conda create -n mini\_integrator python=3.11

conda activate mini\_integrator



O con venv estándar:



python -m venv venv

venv\\Scripts\\activate

2️⃣ Instalar dependencias

pip install -r requirements.txt

🔧 Configuración



Copiar archivo de variables:



copy .env.example .env



Variables principales:



API\_BASE\_URL



SOURCE\_NAME



SQLITE\_PATH



HTTP\_TIMEOUT\_SECONDS



HTTP\_MAX\_RETRIES



HTTP\_BACKOFF\_BASE\_SECONDS



PROMETHEUS\_MULTIPROC\_DIR



🗄 Inicializar base de datos



La base se crea automáticamente al ejecutar el sync.



Manual:



python src\\db.py

▶ Ejecutar sincronización manual

python src\\sync.py



El proceso:



Consume /users y /posts



Aplica transformación



Realiza upsert (evita duplicados)



Relaciona posts con usuarios



Registra logs



Actualiza métricas



🔁 Idempotencia



Se define una llave de negocio:



UNIQUE(source, external\_id)



Persistencia:



INSERT ... ON CONFLICT(source, external\_id) DO UPDATE



Ejecutar múltiples veces el proceso no genera duplicados.



🔄 Transformación / Mapeo aplicado



No se guarda únicamente el payload crudo.



Users



source



external\_id



full\_name (normalizado)



username\_norm (lowercase)



email\_norm (lowercase)



city



synced\_at (ISO UTC)



raw\_payload (JSON original)



Posts



source



external\_id



external\_user\_id



title\_norm (lowercase)



body\_clean (limpieza de texto)



synced\_at



raw\_payload



Relación:



posts.user\_id es FK local resuelta por (source, external\_user\_id)



🧾 Logs



Se registran:



Inicio de ejecución



Cantidad procesada



Cantidad upserted



Duración total



Errores (con stacktrace)



📊 Monitoreo



Endpoints:



GET /health



GET /metrics



Modo multiproceso (recomendado)



Como el sync corre en proceso separado del servidor:



Consola A (Servidor)

conda activate mini\_integrator

cd C:\\Users\\User\\mini-integrator

set PROMETHEUS\_MULTIPROC\_DIR=%CD%\\metrics\_data

uvicorn src.app:app --host 0.0.0.0 --port 8000

Consola B (Sync)

conda activate mini\_integrator

cd C:\\Users\\User\\mini-integrator

set PROMETHEUS\_MULTIPROC\_DIR=%CD%\\metrics\_data

python src\\sync.py



Ver métricas:



http://localhost:8000/metrics



Métricas expuestas



integration\_runs\_total



integration\_runs\_success\_total



integration\_runs\_failed\_total



integration\_records\_processed\_total



integration\_records\_upserted\_total



integration\_run\_duration\_seconds



🧪 Evidencia de ejecución exitosa



Ejemplo real:



Start sync source=jsonplaceholder api\_base=https://jsonplaceholder.typicode.com

Fetched users=10 posts=100

Sync success run\_id=2 upserted\_users=10 upserted\_posts=100 duration\_ms=960

✅ Cumplimiento de requisitos



✔ Consumo API REST pública

✔ Transformación antes de persistencia

✔ Persistencia en base local

✔ Idempotencia (source + external\_id)

✔ Logs

✔ Ejecución manual

✔ Monitoreo Prometheus

✔ Relación usuarios–posts

✔ Manejo de errores HTTP + retry/backoff



📌 Decisiones técnicas



Se utilizó SQLite para simplificar instalación local y cumplir con el alcance en el tiempo sugerido (6–10 horas), manteniendo arquitectura modular que permitiría migración sencilla a PostgreSQL o integración en un framework como Django si fuese requerido.



