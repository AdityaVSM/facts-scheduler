import os
import random
import logging
import httpx
from groq import Groq

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a senior Java architect and Spring Boot expert who teaches concepts clearly and concisely.

Generate ONE unique, production-relevant insight about a Java, Spring Boot, or software design concept.

Goal: A quick-read format that a developer can absorb in under 2 minutes, while still building a solid mental picture.

Structure (use Markdown formatting):
1) **## Concept Name** — a clear heading
2) **💡 In a Nutshell** — 2-3 sentences explaining the core idea. Use a simple analogy or metaphor to make it click instantly.
3) **🔧 Quick Example** — a short, practical code snippet (in a markdown code block). Keep it realistic but compact (10-20 lines max).
4) **⚡ Key Takeaway** — 2-3 bullet points: when to use it, what to watch out for, or how it compares to an alternative.
5) **🔗 Learn More** — 1 link to an official/reputable source.

Constraints:
- 150-300 words (concise — respect the reader's time)
- Beginner to intermediate friendly but technically accurate
- Widely used concepts, not esoteric ones
- Useful for interviews and day-to-day Java/Spring Boot development
- Conversational tone — like a senior engineer giving a quick tip to a teammate
- Every sentence must teach something — zero fluff
"""


TOPIC_AREAS = [
    # JVM & Core Java
    "JVM internals (class loading, bytecode, JIT compilation)",
    "Garbage Collection (G1, ZGC, Shenandoah, tuning flags)",
    "Java Memory Model (happens-before, volatile, memory barriers)",
    "Concurrency (virtual threads, structured concurrency, CompletableFuture)",
    "Thread pools and Executors (ForkJoinPool, custom thread factories)",
    "Java records, sealed classes, pattern matching",
    "Java Collections internals (HashMap, ConcurrentHashMap, TreeMap)",
    "Java Streams and functional programming best practices",
    "Java performance tuning (profiling, JFR, benchmarking with JMH)",
    "Exception handling best practices and custom exception hierarchies",
    "Java Generics (type erasure, wildcards, bounded types)",
    "Java I/O vs NIO vs NIO.2 (channels, buffers, selectors)",
    # Spring Boot
    "Spring Boot auto-configuration internals",
    "Spring AOP and proxying (CGLIB vs JDK dynamic proxy)",
    "Spring Bean lifecycle and scopes",
    "Spring Boot Actuator and observability (Micrometer, tracing)",
    "Spring transactions (@Transactional pitfalls, propagation levels)",
    "Spring WebFlux and reactive programming",
    "Spring Security (OAuth2, JWT, method security)",
    "Spring Data JPA (N+1 problem, projections, specifications)",
    "Spring Boot testing (slices, Testcontainers, MockBean)",
    "Spring Boot configuration (profiles, externalized config, @ConfigurationProperties)",
    "Spring Boot deployment (Docker, GraalVM native image, layered jars)",
    "Spring Boot caching (@Cacheable, cache providers, eviction strategies)",
    "Spring Boot error handling (global exception handlers, ProblemDetail)",
    # Design Patterns
    "Singleton pattern in Java (eager vs lazy, enum singleton, Spring singletons)",
    "Factory Method and Abstract Factory patterns with real-world Java examples",
    "Strategy pattern (replacing if-else chains, Spring's use of Strategy)",
    "Observer pattern (event-driven design, Spring ApplicationEvent)",
    "Builder pattern (telescoping constructors problem, Lombok @Builder)",
    "Decorator pattern (Java I/O streams, adding behavior dynamically)",
    "Template Method pattern (Spring's JdbcTemplate, RestTemplate internals)",
    "Proxy pattern (JDK dynamic proxy, CGLIB, Spring AOP proxies)",
    "Adapter pattern (legacy integration, Spring HandlerAdapter)",
    "Chain of Responsibility pattern (servlet filters, Spring interceptors)",
    "Repository pattern (Spring Data, separating domain from persistence)",
    "Circuit Breaker pattern (Resilience4j, fault tolerance in microservices)",
    "CQRS and Event Sourcing patterns in Java microservices",
    "Dependency Injection as a pattern (IoC principle, constructor vs field injection)",
]


def generate_raw_fact(previous_titles: list[str] | None = None) -> str:
    http_client = httpx.Client(verify=False)
    client = Groq(api_key=os.getenv("GROQ_API_KEY"), http_client=http_client)
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    # Build a dynamic user prompt with a random topic hint and exclusion list
    suggested_topic = random.choice(TOPIC_AREAS)
    user_prompt = f"Generate a detailed deep-dive article now. Focus on: {suggested_topic}."

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
        max_tokens=800,
        temperature=1.0,
    )

    text = response.choices[0].message.content
    logger.info("[LLM] Received fact (%d chars)", len(text))
    return text