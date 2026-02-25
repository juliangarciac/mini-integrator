from prometheus_client import Counter, Histogram

RUNS_TOTAL = Counter("integration_runs_total", "Total runs", ["source"])
RUNS_SUCCESS = Counter("integration_runs_success_total", "Successful runs", ["source"])
RUNS_FAILED = Counter("integration_runs_failed_total", "Failed runs", ["source"])

RECORDS_PROCESSED = Counter("integration_records_processed_total", "Records processed", ["source", "entity"])
RECORDS_UPSERTED = Counter("integration_records_upserted_total", "Records upserted", ["source", "entity"])

RUN_DURATION_SECONDS = Histogram("integration_run_duration_seconds", "Run duration in seconds", ["source"])