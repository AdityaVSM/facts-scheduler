import logging
import time
import database
import fact_generator
import email_sender

logger = logging.getLogger(__name__)

MAX_DEDUP_RETRIES = 3


def run() -> bool:
    """
    Full pipeline: Generate → Deduplicate → Persist → Email.
    Returns True on success, False if skipped (all duplicates).
    """
    logger.info("[Pipeline] Starting daily fact pipeline")

    # Step 1: Generate with deduplication retries
    fact = None
    for attempt in range(1, MAX_DEDUP_RETRIES + 1):
        logger.info("[Pipeline] Generation attempt %d/%d", attempt, MAX_DEDUP_RETRIES)
        candidate = fact_generator.generate()

        if database.title_exists(candidate.title) or database.hash_exists(candidate.content_hash):
            logger.warning("[Pipeline] Duplicate on attempt %d — retrying...", attempt)
            continue

        fact = candidate
        break

    if fact is None:
        logger.error("[Pipeline] All %d attempts produced duplicates. Skipping today.", MAX_DEDUP_RETRIES)
        return False

    # Step 2: Persist
    database.save_fact(fact.title, fact.content, fact.content_hash, fact.topic_category)

    # Step 3: Send email (retry once on failure)
    _send_with_retry(fact)

    logger.info("[Pipeline] Done. Fact '%s' delivered.", fact.title)
    return True


def _send_with_retry(fact):
    try:
        email_sender.send(fact)
    except Exception as e:
        logger.warning("[Pipeline] Email failed: %s — retrying in 10s...", e)
        time.sleep(10)
        email_sender.send(fact)   # Let this exception propagate if it fails again
