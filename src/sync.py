import os
import time
import logging
from dotenv import load_dotenv

from db import init_db, get_conn
from http_client import get_json
from transform import map_user, map_post
from repository import upsert_user, get_user_id, upsert_post

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger("integrator.sync")


INSERT_RUN = """
INSERT INTO integration_runs (started_at, status, source)
VALUES (datetime('now'), 'running', ?);
"""

GET_LAST_RUN_ID = "SELECT last_insert_rowid() AS id;"

FINISH_RUN = """
UPDATE integration_runs SET
  finished_at=datetime('now'),
  status=?,
  processed_users=?,
  processed_posts=?,
  upserted_users=?,
  upserted_posts=?,
  error_message=?,
  duration_ms=?
WHERE id=?;
"""


def run_sync() -> None:
    load_dotenv()
    init_db()

    api_base = os.environ.get("API_BASE_URL", "https://jsonplaceholder.typicode.com").rstrip("/")
    source = os.environ.get("SOURCE_NAME", "jsonplaceholder")

    t0 = time.time()

    processed_users = processed_posts = 0
    upserted_users = upserted_posts = 0
    run_id = None

    logger.info("Start sync source=%s api_base=%s", source, api_base)

    try:
        # create run row
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(INSERT_RUN, (source,))
            cur.execute(GET_LAST_RUN_ID)
            run_id = cur.fetchone()["id"]
            conn.commit()

        # fetch from API
        users = get_json(f"{api_base}/users")
        posts = get_json(f"{api_base}/posts")

        user_rows = [map_user(source, u) for u in users]
        post_rows = [map_post(source, p) for p in posts]

        processed_users = len(user_rows)
        processed_posts = len(post_rows)

        logger.info("Fetched users=%s posts=%s", processed_users, processed_posts)

        # upsert into DB (users first)
        with get_conn() as conn:
            cur = conn.cursor()

            for u in user_rows:
                upsert_user(cur, u)
                upserted_users += 1

            for p in post_rows:
                uid = get_user_id(cur, source, p["external_user_id"])
                if uid is None:
                    logger.warning(
                        "Skipping post external_id=%s (user not found external_user_id=%s)",
                        p["external_id"], p["external_user_id"]
                    )
                    continue

                p["user_id"] = uid
                upsert_post(cur, p)
                upserted_posts += 1

            conn.commit()

        dur_ms = int((time.time() - t0) * 1000)
        logger.info(
            "Sync success run_id=%s upserted_users=%s upserted_posts=%s duration_ms=%s",
            run_id, upserted_users, upserted_posts, dur_ms
        )

        # finish run success
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                FINISH_RUN,
                ("success", processed_users, processed_posts, upserted_users, upserted_posts, None, dur_ms, run_id)
            )
            conn.commit()

    except Exception as e:
        dur_ms = int((time.time() - t0) * 1000)
        logger.exception("Sync failed run_id=%s err=%s", run_id, e)

        if run_id is not None:
            with get_conn() as conn:
                cur = conn.cursor()
                cur.execute(
                    FINISH_RUN,
                    ("failed", processed_users, processed_posts, upserted_users, upserted_posts, str(e)[:900], dur_ms, run_id)
                )
                conn.commit()

        raise


if __name__ == "__main__":
    run_sync()