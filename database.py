import psycopg2
import psycopg2.extras
import os
import logging

logger = logging.getLogger(__name__)


def get_connection():
    conn_params = dict(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "factdb"),
        user=os.getenv("DB_USERNAME", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
    )
    # Neon and other cloud Postgres providers require SSL
    sslmode = os.getenv("DB_SSLMODE", "")
    if sslmode:
        conn_params["sslmode"] = sslmode
    elif conn_params["host"] not in ("localhost", "127.0.0.1"):
        conn_params["sslmode"] = "require"
    return psycopg2.connect(**conn_params)


def init_db():
    """Create the sent_facts table if it doesn't exist."""
    sql = """
        CREATE TABLE IF NOT EXISTS sent_facts (
            id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            title         VARCHAR(500) NOT NULL,
            content       TEXT NOT NULL,
            content_hash  VARCHAR(64) NOT NULL UNIQUE,
            topic_category VARCHAR(100),
            sent_at       TIMESTAMP DEFAULT NOW()
        );
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
    logger.info("[DB] Table ready.")


def title_exists(title: str) -> bool:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM sent_facts WHERE title = %s LIMIT 1", (title,))
            return cur.fetchone() is not None


def hash_exists(content_hash: str) -> bool:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM sent_facts WHERE content_hash = %s LIMIT 1", (content_hash,))
            return cur.fetchone() is not None


def save_fact(title: str, content: str, content_hash: str, topic_category: str):
    sql = """
        INSERT INTO sent_facts (title, content, content_hash, topic_category)
        VALUES (%s, %s, %s, %s)
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (title, content, content_hash, topic_category))
        conn.commit()
    logger.info("[DB] Fact saved: '%s'", title)


def get_previous_titles() -> list[str]:
    """Return all previously sent fact titles."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT title FROM sent_facts ORDER BY sent_at DESC")
            return [row[0] for row in cur.fetchall()]


def total_facts() -> int:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM sent_facts")
            return cur.fetchone()[0]
