import os
from fastapi import FastAPI
from starlette.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, generate_latest
from prometheus_client import multiprocess

app = FastAPI(title="Mini Integrator Monitor")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/metrics")
def metrics():
    prom_dir = os.environ.get("PROMETHEUS_MULTIPROC_DIR")
    if prom_dir:
        registry = CollectorRegistry()
        multiprocess.MultiProcessCollector(registry)
        data = generate_latest(registry)
        return Response(content=data, media_type=CONTENT_TYPE_LATEST)

    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)