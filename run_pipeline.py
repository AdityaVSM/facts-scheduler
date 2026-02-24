"""
Standalone pipeline runner for GitHub Actions (no web server needed).
Usage: python run_pipeline.py
"""
import os
import sys
import logging

# Load .env only if it exists (local dev); in GitHub Actions, env vars come from secrets
from dotenv import load_dotenv
load_dotenv()

import database
import pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def main():
    logger.info("Initializing database...")
    database.init_db()

    logger.info("Running pipeline...")
    success = pipeline.run()

    if success:
        logger.info("Pipeline completed successfully.")
        sys.exit(0)
    else:
        logger.error("Pipeline failed (all duplicates). Exiting with code 1.")
        sys.exit(1)


if __name__ == "__main__":
    main()
