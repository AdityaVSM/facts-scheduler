import os
import smtplib
import logging
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fact_generator import GeneratedFact

logger = logging.getLogger(__name__)


def send(fact: GeneratedFact):
    sender = os.getenv("MAIL_SENDER")
    password = os.getenv("MAIL_APP_PASSWORD")
    recipient = os.getenv("MAIL_RECIPIENT", "adityavsm55@gmail.com")

    logger.info("[Email] Sending '%s' to %s", fact.title, recipient)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"☕ Java Fact of the Day: {fact.title}"
    msg["From"] = sender
    msg["To"] = recipient

    html_body = _build_html(fact)
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.ehlo()
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, recipient, msg.as_string())

    logger.info("[Email] Delivered successfully: '%s'", fact.title)


def _build_html(fact: GeneratedFact) -> str:
    html_content = _markdown_to_html(fact.content)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <style>
    body      {{ font-family: 'Segoe UI', Arial, sans-serif; background:#f5f5f5; margin:0; padding:0; }}
    .card     {{ max-width:680px; margin:32px auto; background:#ffffff;
                border-radius:10px; box-shadow:0 2px 10px rgba(0,0,0,.12); overflow:hidden; }}
    .header   {{ background:#1a1a2e; color:#e0e0e0; padding:22px 28px; }}
    .header h1{{ margin:0; font-size:18px; font-weight:600; }}
    .badge    {{ display:inline-block; margin-top:8px; background:#16213e;
                color:#a3cef1; font-size:12px; padding:3px 10px; border-radius:20px; }}
    .body     {{ padding:28px; color:#222; line-height:1.7; font-size:15px; }}
    .body h2  {{ color:#1a1a2e; font-size:17px; margin-top:0; }}
    pre       {{ background:#1e1e2e; color:#cdd6f4; padding:16px; border-radius:6px;
                overflow-x:auto; font-size:13px; line-height:1.5; }}
    code      {{ background:#eef0f5; padding:2px 6px; border-radius:4px; font-size:13px; }}
    .prod-tip {{ background:#fff8e1; border-left:4px solid #f9a825; padding:10px 14px;
                border-radius:4px; margin-top:16px; font-size:14px; }}
    .footer   {{ background:#f0f0f0; text-align:center; padding:14px;
                font-size:12px; color:#888; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="header">
      <h1>☕ Java / Spring Boot — Daily Fact</h1>
      <span class="badge">📂 {fact.topic_category}</span>
    </div>
    <div class="body">
      {html_content}
    </div>
    <div class="footer">
      Delivered by Java Fact Agent &middot; Runs daily at 9:00 AM IST
    </div>
  </div>
</body>
</html>"""


def _markdown_to_html(markdown: str) -> str:
    lines = markdown.split("\n")
    html = []
    in_code = False

    for line in lines:
        if line.startswith("```"):
            if not in_code:
                html.append("<pre><code>")
                in_code = True
            else:
                html.append("</code></pre>")
                in_code = False
            continue

        if in_code:
            html.append(_escape(line))
            continue

        if line.startswith("## "):
            html.append(f"<h2>{_escape(line[3:])}</h2>")
        elif line.startswith("# "):
            html.append(f"<h2>{_escape(line[2:])}</h2>")
        elif line.lower().startswith("why this matters"):
            html.append(f'<div class="prod-tip">💡 <strong>{_escape(line)}</strong></div>')
        elif line.strip() == "":
            html.append("<br/>")
        else:
            # Inline bold + code
            formatted = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", line)
            formatted = re.sub(r"`([^`]+)`", r"<code>\1</code>", formatted)
            html.append(f"<p style='margin:4px 0'>{formatted}</p>")

    return "\n".join(html)


def _escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
