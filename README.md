# checkmyvibe 🛡️

<div align="center">

**Production Readiness & Code Quality Agent Skill for AI Coding Assistants**

*Catch scaffolding traps, exposed secrets, fake auth, database misconfigurations, and client-side pricing leaks before your users or attackers do.*

[![npm version](https://img.shields.io/npm/v/checkmyvibe?color=blue&style=flat-square)](https://www.npmjs.com/package/checkmyvibe)
[![License](https://img.shields.io/badge/license-Apache--2.0-green?style=flat-square)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-0-success?style=flat-square)](package.json)
[![Privacy](https://img.shields.io/badge/privacy-100%25%20local-blueviolet?style=flat-square)](#-zero-dependencies--100-local-privacy)
[![Harnesses](https://img.shields.io/badge/agents-Claude%20Code%20%7C%20Cursor%20%7C%20Codex%20%7C%20Gemini%20%7C%20OpenCode-orange?style=flat-square)](#-multi-agent--platform-support)

[Quick Start](#-quick-start) • [Why checkmyvibe?](#-why-checkmyvibe) • [How It Works](#-how-it-works) • [What It Checks](#-the-7-deep-readiness-checks) • [Scoped Scans](#-targeted--scoped-scanning) • [Sample Report](#-sample-report-preview) • [Agent Setup](#-multi-agent--platform-support)

</div>

---

## ⚡ Quick Start

Install and configure `checkmyvibe` in under 30 seconds:

```bash
npx checkmyvibe
```

The interactive installer detects your environment (Claude Code, Cursor, OpenCode, Codex, Gemini CLI) and installs the skill and slash commands locally or globally.

Then ask your AI coding assistant:

```text
/checkmyvibe
```
*or simply prompt:*
> *"Check my vibe and verify if this codebase is ready to ship to production."*

---

## 💡 Why checkmyvibe?

AI coding assistants—like Claude Code, Cursor, Windsurf, Copilot, v0, Bolt, Lovable, and Replit—have made it possible to build full-stack web applications in a single afternoon.

However, **AI models optimize for "it works right now", not "it is production-ready."**

A feature can pass every manual test you run—sign up, log in, create a record, complete a checkout—while harboring catastrophic scaffolding shortcuts under the hood:

* 🔑 **Inlined API Keys & Service Roles:** Hardcoded `sk-proj-...` tokens or Supabase `service_role` secrets leaked into client-side bundles or React Server Component HTML payloads.
* 🚪 **Fake & Stubbed Authentication:** Mock handlers (`function isAuthenticated() { return true; }`), dummy user objects (`{ id: "mock-id", role: "admin" }`), or middleware calling `next()` unconditionally.
* 🔓 **Permissive Database Rules:** Supabase tables with Row-Level Security (RLS) disabled or set to `USING (true)`, or Firebase rules left on default-allow / expired test mode.
* 🕵️ **Broken Object-Level Authorization (IDOR/BOLA):** Endpoints (`/api/orders/:id`, Next.js Server Actions) that fetch or mutate records by ID without checking if the active user actually owns them.
* 💳 **Client-Controlled Pricing:** Checkout routes trusting `price` or `amount` sent directly from client request bodies instead of resolving them server-side.
* 🎣 **Unverified Webhooks:** Payment webhooks (Stripe, Lemon Squeezy, Dodo Payments, Polar, Razorpay) processing events without validating cryptographic HMAC signatures.

**`checkmyvibe` bridges the gap between rapid vibe-prototyping and real-world engineering.** It provides your coding agent with deterministic helper scripts, architectural patterns, and a strict verification workflow so it can audit your code, point out the exact flaws in plain English, and provide drop-in patches.

---

## ⚙️ How It Works

`checkmyvibe` combines deterministic Python inspection scripts with the contextual reasoning of your AI coding assistant:

```
┌────────────────────────────────────────────────────────┐
│  You run: /checkmyvibe (or a scoped scan)              │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│  Agent discovers checkmyvibe & reads SKILL.md          │
│  - Understands repository stack, architecture & data   │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│  Runs Local Python Verification Scripts (scripts/*.py) │
│  - scan_secrets.py          - check_auth_patterns.py   │
│  - check_gitignore.py       - check_db_config.py       │
│  - check_payment_config.py                             │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│  Agent Performs Semantic Code & Architecture Review    │
│  - Traces IDOR / BOLA across routes & Server Actions   │
│  - Audits SSRF, AI markdown DOM XSS, mass assignment   │
│  - Validates webhook idempotency & subscription state  │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│  Generates Prioritized Executive & Developer Report    │
│  - Plain-English breakdown (What's wrong & Why it hurts)│
│  - Exact file paths, line numbers & drop-in fixes       │
│  - Writes detailed report to checkmyvibe-report.md     │
│  - Post-fix verification before & after metric         │
└────────────────────────────────────────────────────────┘
```

1. **Deterministic Speed:** Bundled zero-dependency Python 3 scripts scan regex patterns, file trees, `.gitignore` entries, and AST configs in milliseconds.
2. **Contextual Reasoning:** Your AI agent inspects data flow, cross-file references, multi-tenant boundaries, and complex framework idioms (e.g. Next.js App Router Server Actions vs Client Components).
3. **Actionable Remediation:** Issues are categorized into **Critical**, **Should Fix**, and **Worth Reviewing** with exact code diffs so you can fix them in your next commit.
4. **Persistent Markdown Report (`checkmyvibe-report.md`):** Automatically saves a complete, formatted audit document in your project root for easy viewing, client sharing, and issue tracking.

---

## 🔍 The 7 Deep Readiness Checks

| # | Category | What is Checked | High-Risk Patterns Flagged |
| :-: | :--- | :--- | :--- |
| **1** | **Exposed Secrets & Credential Hygiene** | Server-side & client-side source code, bundles, and config files | OpenAI (`sk-proj-`), Anthropic (`sk-ant-`), Groq, Resend, Supabase `service_role` JWTs, database connection URIs (`postgres://`), live Stripe keys (`sk_live_`), Next.js RSC server-to-client prop leaks, and secrets exposed via `NEXT_PUBLIC_*` / `VITE_*`. |
| **2** | **Version Control & Container Leakage** | Repository configuration, `.gitignore`, `.dockerignore`, and commit history | Sensitive `.env*` files present in working directory but omitted from `.gitignore`; Dockerfile `COPY . .` without `.dockerignore` (secrets baked into image layers); committed `.npmrc` auth tokens; `.env` files lingering in git history. |
| **3** | **Authentication & Session Guards** | Route guards, middleware, session checks, and auth provider configurations | Mock auth stubs (`mockAuth`, `fakeLogin`, `return true`), dummy user returns, Clerk v5 matcher exclusions & missing `auth.protect()`, NextAuth missing secrets, Supabase server using insecure `getSession()` instead of `getUser()`, unverified Firebase client tokens, and plaintext password hashing. |
| **4** | **Database & BaaS Misconfiguration** | Supabase, Firebase, Neon, Prisma, Drizzle, MongoDB, and embedded DBs | Supabase tables with Row-Level Security (RLS) disabled or set to `USING (true)`; Firestore default-allow or expiring test rules; Neon unpooled connections in serverless functions; missing SSL transport encryption; public SQLite database files in `public/`; and NoSQL/MongoDB query selector injection. |
| **5** | **Broken Object-Level Authorization (IDOR / BOLA)** | REST endpoints, Next.js Server Actions (`'use server'`), and tRPC / GraphQL resolvers | Missing user/tenant ownership filters (`WHERE id = $1` instead of `WHERE id = $1 AND user_id = $2`); unsecured Server Actions invoked directly as public RPCs; multi-tenant organization boundary bypasses where user membership in `orgId` is not verified. |
| **6** | **Server Input Handling, SSRF & DOM XSS** | Form handlers, API endpoints, proxy routes, and AI markdown rendering | Server-Side Request Forgery (SSRF) in link scrapers/image proxies without private RFC1918 / AWS metadata IP blocking; DOM XSS in AI markdown rendering (`react-markdown` without `rehype-sanitize`); raw SQL concatenation; Prisma/Mongoose mass assignment; and wildcard CORS (`origin: '*', credentials: true`). |
| **7** | **Payment, Webhook & Subscription Integrity** | Checkout flows, webhook handlers, and subscription lifecycle management | Client-side price tampering (trusting `req.body.price`); missing cryptographic HMAC webhook verification across Stripe, Dodo Payments, Lemon Squeezy, Polar.sh, Paddle, and Razorpay; missing webhook idempotency (`event.id` deduplication); and unhandled subscription cancellation events (`customer.subscription.deleted`). |

---

## 🎯 Targeted / Scoped Scanning

Need fast feedback on a specific subsystem without running the entire test suite? Use scoped scans during active development:

| Slash Command | Scope Keyword | Checks Executed | Best For |
| :--- | :--- | :--- | :--- |
| `/checkmyvibe-secrets` | `/checkmyvibe secrets` | **Checks 1a + 1b + 2** | Pre-commit sanity check: API keys, env vars, `.gitignore` & Docker protection |
| `/checkmyvibe-auth` | `/checkmyvibe auth` | **Check 3** | Reviewing login/signup flows, session validation, route guards, and middleware |
| `/checkmyvibe-db` | `/checkmyvibe db` | **Check 4** | Auditing Supabase RLS policies, Firebase security rules, and database connection pooling |
| `/checkmyvibe-backend` | `/checkmyvibe backend` | **Checks 1a, 3, 4, 5, 6 (srv), 7 (srv)** | Comprehensive audit of server routes, Server Actions, IDOR/BOLA, and webhook handlers |
| `/checkmyvibe-frontend` | `/checkmyvibe frontend` | **Checks 1b, 3 (cli), 6 (XSS), 7 (cli)** | Inspecting client bundles, RSC prop serialization, AI markdown XSS, and UI pricing logic |
| `/checkmyvibe-payment` | `/checkmyvibe payment` | **Check 7** | Reviewing checkout routes, payment gateway webhooks, and subscription lifecycle |
| `/checkmyvibe` | *(no argument)* | **All Checks (1a – 7)** | Complete pre-launch production readiness audit across your entire project |

> **Pro-Tip:** You can also pass a directory target to any command:
> ```text
> /checkmyvibe src/app/api
> /checkmyvibe secrets .
> ```

---

## 📋 Sample Report Preview

When `checkmyvibe` completes its review, your agent produces a structured, human-readable report designed for both engineers and non-technical founders:

````markdown
## 🛡️ checkmyvibe Production Readiness Review

**Stack:** Next.js 14 (App Router) + Supabase + Stripe + Tailwind CSS  
**Findings:** 🚨 2 Critical, ⚠️ 1 Should Fix, ℹ️ 1 Worth Reviewing  
**Verdict:** 🛑 **Not ready to ship** — fix the Critical items before deploying to production.

---

### 🚨 [Critical] Insecure Supabase Server Session Verification
* **What's wrong:** The route handler uses `supabase.auth.getSession()` inside a Server Action to verify the user.
* **Why it matters:** `getSession()` reads local cookie data without revalidating the cryptographic signature with the Supabase Auth server. Spoofed or expired cookies can be accepted as valid.
* **The fix:** Switch to `await supabase.auth.getUser()`, which validates the authentication token against the Supabase Auth API:
  ```ts
  // Before
  const { data: { session } } = await supabase.auth.getSession();
  // After
  const { data: { user }, error } = await supabase.auth.getUser();
  if (error || !user) return { error: "Unauthorized" };
  ```
* **File:** `src/app/actions/documents.ts:18-24`

---

### 🚨 [Critical] Missing Object-Level Authorization (IDOR) on Invoice Route
* **What's wrong:** The `/api/invoices/[id]` endpoint fetches invoices purely by `params.id` without checking if the invoice belongs to the requesting user.
* **Why it matters:** Any authenticated user can view any other customer's billing history and address simply by incrementing the ID in the URL.
* **The fix:** Add a user ownership constraint to the database query:
  ```ts
  const invoice = await db.query(
    'SELECT * FROM invoices WHERE id = $1 AND user_id = $2',
    [params.id, sessionUser.id]
  );
  if (!invoice) return new Response('Not Found', { status: 404 });
  ```
* **File:** `src/app/api/invoices/[id]/route.ts:12-28`

---

### ⚠️ [Should Fix] Webhook Handler Missing Idempotency Check
* **What's wrong:** The Stripe webhook handler does not track processed `event.id` values.
* **Why it matters:** If Stripe retries a webhook due to a temporary network timeout, your endpoint will grant duplicate credits or generate duplicate orders.
* **The fix:** Record `event.id` in your database within a transaction and return early if it has already been processed.
* **File:** `src/app/api/webhooks/stripe/route.ts:45-62`
````

---

## 🤖 Multi-Agent & Platform Support

`checkmyvibe` is built on open standards—plain Markdown instructions and standard Python 3 scripts. Any coding agent that can read files and execute shell commands can run it natively:

### 1. Claude Code
Native zero-config support. Running `npx checkmyvibe` installs the skill into `.claude/skills/checkmyvibe` and registers all `/checkmyvibe*` slash commands in `.claude/commands/`.

### 2. Cursor
When a `.cursor/` folder exists, `npx checkmyvibe` copies `adapters/checkmyvibe.mdc` into `.cursor/rules/checkmyvibe.mdc`.
* **Manual Setup:** Copy `adapters/checkmyvibe.mdc` into `.cursor/rules/`. Cursor will automatically trigger `checkmyvibe` when asked about code quality or production readiness.

### 3. Codex CLI, Gemini CLI & Antigravity
The installer automatically appends the `adapters/AGENTS-SNIPPET.md` block to your `AGENTS.md` (or `GEMINI.md`).
* **Manual Setup:** Add this snippet to your `AGENTS.md`:
  ```markdown
  ## checkmyvibe (production readiness & code quality audit)
  When the user asks to "check my vibe", run a production readiness check, review code quality,
  or run a scoped check (`secrets`, `auth`, `db`, `backend`, `frontend`, `payment`) — locate and
  follow `.claude/skills/checkmyvibe/SKILL.md` or `~/.claude/skills/checkmyvibe/SKILL.md`.
  ```

### 4. OpenCode
When `.opencode/` is detected, the installer places `adapters/opencode-checkmyvibe.md` into `.opencode/command/checkmyvibe.md`, enabling the `/checkmyvibe <scope>` command directly in OpenCode.

### 5. Windsurf, Roo Code, Cline & GitHub Copilot
Point your agent to `SKILL.md` or place `SKILL.md` in your project's agent instructions folder.

---

## 📦 Manual Installation

If you prefer not to use `npx`, install manually:

1. Clone or copy this repository into your agent's skills directory:
   * **Project-level (Claude Code):** `.claude/skills/checkmyvibe/`
   * **Global-level (Claude Code):** `~/.claude/skills/checkmyvibe/`
2. Ensure the following files are present:
   ```text
   checkmyvibe/
   ├── SKILL.md
   ├── scripts/
   │   ├── check_auth_patterns.py
   │   ├── check_db_config.py
   │   ├── check_gitignore.py
   │   ├── check_payment_config.py
   │   └── scan_secrets.py
   ├── references/
   │   └── vibe_risk_patterns.md
   ├── commands/
   └── adapters/
   ```
3. *(Optional)* Copy the files from `commands/` into `.claude/commands/` (or `~/.claude/commands/`) to enable slash commands.

---

## 🔒 Zero Dependencies & 100% Local Privacy

* **0 Runtime npm Dependencies:** `checkmyvibe` has zero npm package dependencies. No dependency bloat, no supply-chain risks.
* **100% Local & Private:** Nothing is sent to third-party verification servers. All code analysis occurs directly on your machine using your own AI assistant and local Python 3.
* **Cross-Platform:** Runs seamlessly on macOS, Linux, and Windows. Automatically adapts between `python` and `python3` executables.

---

## ⚠️ Scope & Disclaimer

> [!WARNING]
> **`checkmyvibe` is not a replacement for a formal external security audit, penetration test, or SOC2 compliance certification.**
>
> `checkmyvibe` is an automated first-pass readiness filter engineered to catch common architectural shortcuts, configuration bugs, and scaffolded placeholders introduced by AI models during rapid development. If your application handles sensitive personal data, medical records, or high-volume payment processing, a comprehensive human security review is strongly recommended before launching.

---

## 🤝 Contributing

Have you encountered a new AI coding footgun, framework trap, or unhandled payment provider pattern? Contributions are warmly welcome!

1. Fork the repository: [github.com/Sarthakpatil23/checkmyvibe](https://github.com/Sarthakpatil23/checkmyvibe)
2. Add the pattern or script test case to `scripts/` or `SKILL.md`.
3. Submit a Pull Request.

---

## 📄 License

This project is open-source and licensed under the [Apache 2.0 License](LICENSE).