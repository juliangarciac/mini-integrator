import os
import time
import logging
import requests
from dotenv import load_dotenv

logger = logging.getLogger("integrator.http")


class HttpError(Exception):
    pass


def get_settings():
    load_dotenv()
    timeout = float(os.environ.get("HTTP_TIMEOUT_SECONDS", "10"))
    max_retries = int(os.environ.get("HTTP_MAX_RETRIES", "3"))
    backoff_base = float(os.environ.get("HTTP_BACKOFF_BASE_SECONDS", "0.8"))
    return timeout, max_retries, backoff_base


def get_json(url: str):
    timeout, max_retries, backoff_base = get_settings()
    last_exc = None

    for attempt in range(max_retries):
        try:
            r = requests.get(url, timeout=timeout)

            if 500 <= r.status_code < 600:
                raise HttpError(f"Server error {r.status_code} on {url}")

            if r.status_code >= 400:
                raise HttpError(f"Client error {r.status_code} on {url}: {r.text[:200]}")

            return r.json()

        except (requests.Timeout, requests.ConnectionError, HttpError) as e:
            last_exc = e
            sleep_s = backoff_base * (2 ** attempt)

            logger.warning(
                "GET failed attempt=%s/%s url=%s err=%s -> sleep=%.2fs",
                attempt + 1,
                max_retries,
                url,
                e,
                sleep_s
            )

            time.sleep(sleep_s)

    raise HttpError(f"Failed after retries url={url} last_error={last_exc}")