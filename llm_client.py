import os
import logging
import httpx
from groq import Groq

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a senior Java architect and Spring Boot expert.

Generate ONE unique, advanced, production-relevant fact about Java or Spring Boot.

Constraints:
- Under 500 words, minimum 200 words
- add link to best reputable source and official source if possible
- beginner to intermediate level
- widely used concepts, not esoteric ones
- must be useful for interviews and day to day coding of Java/Spring Boot developers
- Must include:
  1) Concept name (as heading, prefixed with ## )
  2) Short explanation
  3) Tiny example (code or config in a markdown code block)
  4) One-line: "Why this matters in production: ..."

Cover diverse areas including:
- JVM internals, GC, JIT, Java memory model
- Concurrency, thread pools
- Spring Boot auto-config, AOP, bean lifecycle
- Best practices for building and deploying Spring Boot apps
- Transactions, WebFlux, Observability, Performance tuning

Tone: Crisp, senior engineer level, no fluff.
"""


def generate_raw_fact() -> str:
    http_client = httpx.Client(verify=False)
    client = Groq(api_key=os.getenv("GROQ_API_KEY"), http_client=http_client)
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    logger.info("[LLM] Requesting fact from Groq model=%s", model)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "Generate a new Java/Spring Boot fact now."},
        ],
        max_tokens=600,
        temperature=0.8,
    )

    text = response.choices[0].message.content
    logger.info("[LLM] Received fact (%d chars)", len(text))
    return text