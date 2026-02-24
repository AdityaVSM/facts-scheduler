import os
import logging
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv
import json

import database
import pipeline

# ── Logging ────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── HTTP health + manual trigger server ───────────────────────────────────
class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Suppress default noisy HTTP logs

    def do_GET(self):
        if self.path == "/health":
            body = json.dumps({
                "status": "UP",
                "timestamp": datetime.now().isoformat(),
                "totalFactsSent": database.total_facts(),
            }).encode()
            self._respond(200, body)
        else:
            self._respond(404, b'{"error": "not found"}')

    def do_POST(self):
        if self.path == "/trigger":
            logger.info("[API] Manual trigger received")
            # Run pipeline in background so HTTP response is immediate
            t = threading.Thread(target=_safe_run, daemon=True)
            t.start()
            body = json.dumps({"triggered": True, "timestamp": datetime.now().isoformat()}).encode()
            self._respond(200, body)
        else:
            self._respond(404, b'{"error": "not found"}')

    def _respond(self, code, body):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def _safe_run():
    try:
        pipeline.run()
    except Exception as e:
        logger.error("[Scheduler] Pipeline failed: %s", e, exc_info=True)


# ── Entry point ────────────────────────────────────────────────────────────
def main():
    load_dotenv()

    # Init DB
    database.init_db()

    # Scheduler — 9:00 AM IST = 03:30 UTC
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(
        _safe_run,
        trigger=CronTrigger(hour=3, minute=30),
        id="daily_fact",
        name="Daily Java Fact",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("[Scheduler] Scheduled daily at 9:00 AM IST (03:30 UTC)")

    # HTTP server
    port = int(os.getenv("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), Handler)
    logger.info("[Server] Listening on http://localhost:%d", port)
    logger.info("[Server] POST /trigger to send a fact NOW")
    logger.info("[Server] GET  /health  to check status")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        scheduler.shutdown()


if __name__ == "__main__":
    main()
