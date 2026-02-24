# ☕ Java / Spring Boot Daily Fact Agent (Python)

Sends one unique, advanced Java/Spring Boot fact to **adityavsm55@gmail.com** every day at **9:00 AM IST**.

Built with: Python · Anthropic Claude · PostgreSQL · APScheduler · Gmail SMTP

---

## 🚀 Windows Setup (3 steps)

### Step 1 — Get your credentials

**Gmail App Password** (takes 2 min):
1. Go to → https://myaccount.google.com/apppasswords
2. 2-Step Verification must be ON (Google Account → Security → 2-Step Verification)
3. Click **Create** → name it `java-fact-agent`
4. Copy the 16-character password shown (e.g. `abcd efgh ijkl mnop`)

**Anthropic API key**:
1. Go to → https://console.anthropic.com
2. Log in → **API Keys** → **Create Key** → copy it

---

### Step 2 — Run setup.bat

Double-click **`setup.bat`** (or right-click → Run as administrator if needed).

It will automatically:
- ✅ Check Python is installed
- ✅ Create a virtual environment
- ✅ Install all dependencies
- ✅ Create your `.env` file from the template
- ✅ Create the `factdb` PostgreSQL database

---

### Step 3 — Fill in .env

Open `.env` in Notepad and fill in:

```
DB_PASSWORD=your_postgres_password
MAIL_SENDER=your_gmail@gmail.com
MAIL_APP_PASSWORD=abcd efgh ijkl mnop
LLM_API_KEY=sk-ant-xxxxxxxx
```

(MAIL_RECIPIENT is already set to adityavsm55@gmail.com)

---

### Run it

Double-click **`run.bat`**

---

### Send a test email RIGHT NOW

Open a new Command Prompt and run:
```
curl -X POST http://localhost:8080/trigger
```

Check **adityavsm55@gmail.com** — you'll get a formatted HTML email in seconds. ✅

---

### Check how many facts have been sent

```
curl http://localhost:8080/health
```

---

## 📁 Project Structure

```
java-fact-agent-py/
├── main.py              ← Entry point: scheduler + HTTP server (local dev)
├── run_pipeline.py      ← Standalone runner for GitHub Actions
├── pipeline.py          ← Orchestrates generate → save → send
├── fact_generator.py    ← Calls LLM, parses title, hashes content
├── llm_client.py        ← Groq API wrapper
├── database.py          ← PostgreSQL queries (works with Neon)
├── email_sender.py      ← HTML email via Gmail SMTP
├── requirements.txt
├── .env                 ← Local credentials (git-ignored)
├── .gitignore
├── setup.bat            ← One-click Windows setup
├── run.bat              ← One-click Windows run
├── Procfile             ← For PaaS deployment
└── .github/workflows/
    └── daily-fact.yml   ← GitHub Actions cron job
```

---

## ☁️ Deploy for Free (GitHub Actions + Neon PostgreSQL)

This approach is **100% free, forever** — no server needed.

- **GitHub Actions** runs the pipeline daily on a cron schedule
- **Neon.tech** provides a free PostgreSQL database (0.5 GB, always free)

---

### Step 1 — Create a free Neon PostgreSQL database

1. Go to → https://neon.tech and sign up (free, no credit card)
2. **Create Project** → name it `java-fact-agent`
3. Copy the connection details from the dashboard:
   - `Host` (e.g. `ep-cool-name-123456.us-east-2.aws.neon.tech`)
   - `Database` (default: `neondb`)
   - `User` (default: `neondb_owner`)
   - `Password` (shown once — copy it!)

---

### Step 2 — Push to GitHub

```bash
git init
git add .
git commit -m "initial commit"
gh repo create java-fact-agent-py --private --push
```

Or manually:
```bash
git remote add origin https://github.com/YOUR_USERNAME/java-fact-agent-py.git
git push -u origin main
```

---

### Step 3 — Add GitHub Secrets

Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these secrets:

| Secret Name | Value |
|-------------|-------|
| `DB_HOST` | your Neon host (e.g. `ep-cool-name-123456.us-east-2.aws.neon.tech`) |
| `DB_PORT` | `5432` |
| `DB_NAME` | `neondb` (or your Neon database name) |
| `DB_USERNAME` | `neondb_owner` (or your Neon user) |
| `DB_PASSWORD` | your Neon password |
| `GROQ_API_KEY` | your Groq API key |
| `MAIL_SENDER` | your Gmail address |
| `MAIL_APP_PASSWORD` | your 16-char Gmail App Password |
| `MAIL_RECIPIENT` | `adityavsm55@gmail.com` |

---

### Step 4 — You're done! ✅

The GitHub Action runs automatically every day at **9:00 AM IST** (03:30 UTC).

**To trigger manually:** Go to repo → **Actions** tab → **Daily Java Fact** → **Run workflow**

**To check logs:** Actions tab → click on any run to see output

---

## ❓ Troubleshooting

| Problem | Fix |
|---------|-----|
| `python` not recognized | Install from python.org — check "Add to PATH" during install |
| `psql` not recognized | Add PostgreSQL bin folder to PATH (e.g. `C:\Program Files\PostgreSQL\18\bin`) |
| `password authentication failed` | Set correct `DB_PASSWORD` in `.env` |
| `535 Authentication failed` | Gmail App Password is wrong — regenerate it |
| Email goes to spam | Mark as "Not spam" once; Gmail will learn |
| `401` from Anthropic | Check `LLM_API_KEY` in `.env` — no extra spaces |
| Port 8080 already in use | Change `PORT=8081` in `.env` |
