import os
import random
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


TOPIC_AREAS = [
    "JVM internals (class loading, bytecode, JIT compilation)",
    "Garbage Collection (G1, ZGC, Shenandoah, tuning flags)",
    "Java Memory Model (happens-before, volatile, memory barriers)",
    "Concurrency (virtual threads, structured concurrency, CompletableFuture)",
    "Thread pools and Executors (ForkJoinPool, custom thread factories)",
    "Spring Boot auto-configuration internals",
    "Spring AOP and proxying (CGLIB vs JDK dynamic proxy)",
    "Spring Bean lifecycle and scopes",
    "Spring Boot Actuator and observability (Micrometer, tracing)",
    "Spring transactions (@Transactional pitfalls, propagation levels)",
    "Spring WebFlux and reactive programming",
    "Java records, sealed classes, pattern matching",
    "Spring Security (OAuth2, JWT, method security)",
    "Spring Data JPA (N+1 problem, projections, specifications)",
    "Java performance tuning (profiling, JFR, benchmarking with JMH)",
    "Spring Boot testing (slices, Testcontainers, MockBean)",
    "Java Collections internals (HashMap, ConcurrentHashMap, TreeMap)",
    "Spring Boot configuration (profiles, externalized config, @ConfigurationProperties)",
    "Java Streams and functional programming best practices",
    "Spring Boot deployment (Docker, GraalVM native image, layered jars)",
]


def generate_raw_fact(previous_titles: list[str] | None = None) -> str:
    http_client = httpx.Client(verify=False)
    client = Groq(api_key=os.getenv("GROQ_API_KEY"), http_client=http_client)
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    # Build a dynamic user prompt with a random topic hint and exclusion list
    suggested_topic = random.choice(TOPIC_AREAS)
    user_prompt = f"Generate a new Java/Spring Boot fact now. Focus on: {suggested_topic}."

    if previous_titles:
        # Include up to 30 most recent titles to avoid
        titles_to_avoid = previous_titles[:30]
        avoid_list = "\n".join(f"- {t}" for t in titles_to_avoid)
        user_prompt += (
            f"\n\nIMPORTANT: Do NOT repeat any of these previously covered topics:\n{avoid_list}"
            "\n\nPick a completely different concept that is not in the above list."
        )

    logger.info("[LLM] Requesting fact from Groq model=%s, topic_hint='%s'", model, suggested_topic)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=600,
        temperature=1.0,
    )

    text = response.choices[0].message.content
    logger.info("[LLM] Received fact (%d chars)", len(text))
    return text