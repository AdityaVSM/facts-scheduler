import hashlib
import re
import logging
from dataclasses import dataclass
from llm_client import generate_raw_fact

logger = logging.getLogger(__name__)

TOPIC_KEYWORDS = [
    "GC", "Garbage Collector", "JVM", "JIT", "Memory Model",
    "Concurrency", "Thread", "Executor", "Lock", "Volatile",
    "Auto-configuration", "AOP", "Bean", "Transaction", "WebFlux",
    "Reactive", "Observability", "Actuator", "Performance",
]


@dataclass
class GeneratedFact:
    title: str
    content: str
    content_hash: str
    topic_category: str


def generate() -> GeneratedFact:
    raw = generate_raw_fact()
    title = _extract_title(raw)
    content_hash = hashlib.sha256(raw.encode()).hexdigest()
    category = _detect_category(raw)

    logger.info("[FactGen] title='%s' category='%s' hash=%s", title, category, content_hash[:8])
    return GeneratedFact(title=title, content=raw, content_hash=content_hash, topic_category=category)


def _extract_title(raw: str) -> str:
    match = re.search(r"^##\s+(.+)", raw, re.MULTILINE)
    if match:
        return match.group(1).strip()
    # Fallback: first non-blank line
    for line in raw.splitlines():
        stripped = line.strip().lstrip("#").strip()
        if stripped:
            return stripped
    return "Unknown Fact"


def _detect_category(raw: str) -> str:
    upper = raw.upper()
    for keyword in TOPIC_KEYWORDS:
        if keyword.upper() in upper:
            return keyword
    return "General"
