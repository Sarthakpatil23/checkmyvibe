# checkmyvibe

Production Readiness and Code Quality Audit for AI Coding Assistants

Catch scaffolding shortcuts, exposed credentials, mock authentication, permissive database policies, and client-side pricing leaks before deployment.

[![npm version](https://img.shields.io/npm/v/checkmyvibe?color=24292e&style=flat-square)](https://www.npmjs.com/package/checkmyvibe)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue?style=flat-square)](LICENSE)
[![Dependencies](https://img.shields.io/badge/dependencies-0-success?style=flat-square)](package.json)
[![Analysis](https://img.shields.io/badge/analysis-100%25%20local-blueviolet?style=flat-square)](#local-execution-and-privacy)
[![Supported Agents](https://img.shields.io/badge/agents-Claude%20Code%20%7C%20Cursor%20%7C%20Codex%20%7C%20Gemini%20%7C%20OpenCode-333333?style=flat-square)](#platform-support)

---

### Table of Contents

- [Quick Start](#quick-start)
- [Overview](#overview)
- [Architecture & Workflow](#architecture--workflow)
- [Readiness Checks](#readiness-checks)
- [Scoped Audits](#scoped-audits)
- [Sample Audit Report](#sample-audit-report)
- [Platform Support](#platform-support)
- [Manual Installation](#manual-installation)
- [Local Execution and Privacy](#local-execution-and-privacy)
- [Scope and Disclaimer](#scope-and-disclaimer)
- [Contributing](#contributing)
- [License](#license)

---

## Quick Start

Install and configure `checkmyvibe` in your current project:

```bash
npx checkmyvibe
```

The installer detects your environment (Claude Code, Cursor, OpenCode, Codex, Gemini CLI, or Antigravity) and configures the skill and slash commands locally or globally.

Once configured, run the audit through your AI coding assistant:

```text
/checkmyvibe
```

Alternatively, use natural language:

> "Check my vibe and verify if this codebase is ready to ship to production."

---

## Overview

AI coding tools—including Claude Code, Cursor, Windsurf, Copilot, v0, Bolt, Lovable, and Replit—enable developers to construct full-stack applications rapidly.

However, **AI models optimize for immediate functionality ("it works right now"), not production readiness ("it holds customer data securely").**

A project can pass every manual functional check—user registration, authentication, database operations, payment completion—while concealing critical scaffolding shortcuts:

- **Exposed Credentials and Inlined Service Roles:** Hardcoded API keys (`sk-proj-...`, `sk-ant-...`) or Supabase `service_role` JWTs embedded in client bundles or React Server Component serialization trees.
- **Mock and Stubbed Authentication:** Placeholder routines (`function isAuthenticated() { return true; }`), hardcoded mock profiles (`{ id: "mock-id", role: "admin" }`), or middleware that passes requests unconditionally.
- **Permissive Database Rules:** Supabase tables with Row-Level Security (RLS) disabled or configured with `USING (true)`, or Firebase security rules left on default-allow test mode.
- **Broken Object-Level Authorization (IDOR / BOLA):** Endpoints and Next.js Server Actions querying records directly by ID (`WHERE id = $1`) without asserting user or tenant ownership (`AND user_id = $2`).
- **Client-Controlled Pricing:** Checkout routes trusting the `amount` or `price` submitted in client request bodies instead of resolving catalog prices server-side.
- **Unverified Webhooks:** Payment webhook handlers processing events without cryptographic HMAC signature validation or idempotency deduplication.

`checkmyvibe` bridges the gap between rapid prototyping and production engineering. It equips your AI coding assistant with deterministic verification scripts, structured failure patterns, and a remediation workflow that identifies vulnerabilities, explains their real-world impact, and provides drop-in patches.

---

## Architecture & Workflow

`checkmyvibe` pairs zero-dependency Python inspection scripts with the semantic reasoning capabilities of your AI coding assistant:

```text
+-----------------------------------------------------------------------+
|  User triggers audit: /checkmyvibe (or a scoped scan)                 |
+-----------------------------------┬-----------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|  Agent discovers checkmyvibe & loads SKILL.md                         |
|  - Identifies framework, database, auth provider, and payment stack   |
+-----------------------------------┬-----------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|  Deterministic Python Verification Engine (scripts/*.py)              |
|  - scan_secrets.py           - check_auth_patterns.py                 |
|  - check_gitignore.py        - check_db_config.py                     |
|  - check_payment_config.py                                            |
+-----------------------------------┬-----------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|  Agent Semantic Code & Architectural Analysis                         |
|  - Traces IDOR / BOLA across route handlers and Server Actions        |
|  - Evaluates SSRF risks, private IP access, and AI markdown DOM XSS   |
|  - Inspects webhook signature validation and subscription lifecycle   |
+-----------------------------------┬-----------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|  Prioritized Remediation Report Generation                            |
|  - Structured severity levels: Critical, Should Fix, Worth Reviewing  |
|  - Concrete code diffs showing before and after fixes                 |
|  - Output written directly to checkmyvibe-report.md                   |
+-----------------------------------------------------------------------+
```

### Execution Pillars

1. **Deterministic Speed:** Bundled Python 3 scripts scan patterns, AST structures, `.gitignore` entries, and file trees in milliseconds without external network calls.
2. **Contextual Reasoning:** Your AI coding assistant examines data flow, cross-file imports, multi-tenant boundaries, and framework idioms (e.g., Next.js App Router Server Actions vs. Client Components).
3. **Actionable Remediation:** Findings include exact file paths, line ranges, impact descriptions, and copy-pasteable code patches.
4. **Persistent Audit Artifact:** The full review is saved to `checkmyvibe-report.md` in the project root for review, team tracking, and commit verification.

---

## Readiness Checks

The inspection suite covers seven core categories:

| ID | Category | Target Scope | Key Vulnerabilities Detected |
| :---: | :--- | :--- | :--- |
| **1** | **Exposed Secrets & Credentials** | Source code, config files, client bundles | Cloud & AI API keys (OpenAI, Anthropic, Groq, Resend), Supabase `service_role` tokens, database URIs (`postgres://`), live Stripe keys (`sk_live_`), RSC prop leaks, and public exposure via `NEXT_PUBLIC_*` / `VITE_*`. |
| **2** | **Version Control & Container Isolation** | Repository files, `.gitignore`, Dockerfiles | Working-directory `.env*` files missing from `.gitignore`, Dockerfile `COPY . .` commands lacking `.dockerignore` coverage, committed `.npmrc` tokens, and secrets in git history. |
| **3** | **Authentication & Session Guards** | Middleware, route handlers, auth providers | Mock auth helpers (`mockAuth`, `return true`), dummy user returns, Clerk matcher gaps, Supabase server routes using unverified `getSession()` instead of `getUser()`, missing NextAuth secrets, and plaintext password hashing. |
| **4** | **Database & BaaS Access Controls** | Supabase, Firebase, Neon, Prisma, Drizzle | Supabase tables with RLS disabled or set to `USING (true)`, Firebase test-mode allow rules, Neon unpooled serverless connections, missing SSL transport flags, and public SQLite files in web roots. |
| **5** | **Broken Object-Level Authorization (IDOR / BOLA)** | REST routes, Next.js Server Actions, tRPC | Missing tenant or user ownership filters (`WHERE id = $1` instead of `WHERE id = $1 AND user_id = $2`), public invocation of unauthenticated Server Actions, and unverified organization ID access. |
| **6** | **Server Input Handling, SSRF & DOM XSS** | Fetch utilities, proxy routes, markdown renderers | SSRF in URL scrapers/image proxies without private RFC1918 / cloud metadata blocking, DOM XSS in AI markdown rendering (`react-markdown` without `rehype-sanitize`), SQL concatenation, and wildcard CORS with credentials. |
| **7** | **Payment, Webhook & Subscription Integrity** | Checkout endpoints, webhook listeners | Client-side price tampering (trusting `req.body.price`), missing HMAC verification (Stripe, Dodo Payments, Lemon Squeezy, Polar, Paddle, Razorpay), missing event deduplication, and unhandled subscription terminations. |

---

## Scoped Audits

To audit specific subsystems during iterative development without running the complete test suite, use targeted scopes:

| Slash Command | Scope Keyword | Checks Executed | Primary Use Case |
| :--- | :--- | :--- | :--- |
| `/checkmyvibe-secrets` | `/checkmyvibe secrets` | **Checks 1a, 1b, 2** | Pre-commit check: API keys, env vars, `.gitignore`, and container configs |
| `/checkmyvibe-auth` | `/checkmyvibe auth` | **Check 3** | Auditing authentication flows, session handling, and middleware guards |
| `/checkmyvibe-db` | `/checkmyvibe db` | **Check 4** | Auditing Supabase RLS, Firebase rules, and database connection pooling |
| `/checkmyvibe-backend` | `/checkmyvibe backend` | **Checks 1a, 3, 4, 5, 6 (srv), 7 (srv)** | Comprehensive audit of server routes, Server Actions, IDOR, and webhooks |
| `/checkmyvibe-frontend` | `/checkmyvibe frontend` | **Checks 1b, 3 (cli), 6 (XSS), 7 (cli)** | Inspecting client bundles, RSC prop serialization, and UI pricing assumptions |
| `/checkmyvibe-payment` | `/checkmyvibe payment` | **Check 7** | Auditing checkout routes, payment webhooks, and subscription lifecycle |
| `/checkmyvibe` | *(no argument)* | **All Checks (1a - 7)** | Full production readiness audit across the entire repository |

You can also restrict any scan to a specific directory path:

```text
/checkmyvibe src/app/api
/checkmyvibe secrets .
```

---

## Sample Audit Report

Below is an example of the output generated in `checkmyvibe-report.md`:

````markdown
# Production Readiness Review

**Stack:** Next.js 14 (App Router), Supabase, Stripe, Tailwind CSS  
**Findings:** 2 Critical, 1 Should Fix, 1 Worth Reviewing  
**Verdict:** NOT READY TO SHIP — Resolve Critical items prior to production deployment.

---

### [CRITICAL] Insecure Supabase Server Session Verification

- **Problem:** Route handler verifies authentication via `supabase.auth.getSession()` inside a Server Action.
- **Impact:** `getSession()` reads local cookie data without validating the cryptographic signature against the Supabase Auth server. Spoofed or expired tokens may be accepted as valid.
- **Remediation:** Replace with `await supabase.auth.getUser()`, which validates the token directly against the Supabase Auth service:

```typescript
// Before
const { data: { session } } = await supabase.auth.getSession();

// After
const { data: { user }, error } = await supabase.auth.getUser();
if (error || !user) {
  return { error: "Unauthorized" };
}
```

- **File Reference:** `src/app/actions/documents.ts:18-24`

---

### [CRITICAL] Missing Object-Level Authorization (IDOR) on Invoice Route

- **Problem:** The `/api/invoices/[id]` endpoint queries records solely by `params.id` without validating ownership.
- **Impact:** Any authenticated user can view arbitrary customer invoices and billing metadata by incrementing the record identifier.
- **Remediation:** Scope the database query to the authenticated user's identifier:

```typescript
const invoice = await db.query(
  "SELECT * FROM invoices WHERE id = $1 AND user_id = $2",
  [params.id, sessionUser.id]
);
if (!invoice) {
  return new Response("Not Found", { status: 404 });
}
```

- **File Reference:** `src/app/api/invoices/[id]/route.ts:12-28`

---

### [SHOULD FIX] Webhook Handler Missing Idempotency Validation

- **Problem:** The Stripe webhook handler does not record or check processed `event.id` values.
- **Impact:** Network retries from Stripe may result in duplicate credit allocations or duplicate order processing.
- **Remediation:** Record incoming `event.id` values inside a transactional table and return early if the event has already been recorded.
- **File Reference:** `src/app/api/webhooks/stripe/route.ts:45-62`
````

---

## Platform Support

`checkmyvibe` uses open formats—Markdown instruction specifications and standard Python 3 scripts—making it compatible with any coding agent supporting file reading and command execution:

### Claude Code
Full native support. Running `npx checkmyvibe` installs the skill into `.claude/skills/checkmyvibe` and registers slash commands in `.claude/commands/`.

### Cursor
When a `.cursor/` directory is present, the installer copies `adapters/checkmyvibe.mdc` into `.cursor/rules/checkmyvibe.mdc`.
- **Manual Configuration:** Copy `adapters/checkmyvibe.mdc` into `.cursor/rules/`. Cursor automatically references `checkmyvibe` when assessing code quality or readiness.

### Codex CLI, Gemini CLI, and Google Antigravity
The installer appends the snippet from `adapters/AGENTS-SNIPPET.md` to `AGENTS.md` (or `GEMINI.md`).
- **Manual Configuration:** Append the following block to your `AGENTS.md`:

```markdown
## checkmyvibe (production readiness & code quality audit)
When the user asks to "check my vibe", run a production readiness check, review code quality,
or run a scoped check (`secrets`, `auth`, `db`, `backend`, `frontend`, `payment`) — locate and
follow `.claude/skills/checkmyvibe/SKILL.md` or `~/.claude/skills/checkmyvibe/SKILL.md`.
```

### OpenCode
When `.opencode/` is detected, the installer places `adapters/opencode-checkmyvibe.md` into `.opencode/command/checkmyvibe.md`, enabling the `/checkmyvibe <scope>` command directly within OpenCode.

### Windsurf, Roo Code, Cline, and GitHub Copilot
Point your assistant to `SKILL.md` or place `SKILL.md` directly into your workspace instruction directory.

---

## Manual Installation

To install without using `npx`:

1. Clone or copy this repository into your agent's skills location:
   - **Project Scope (Claude Code):** `.claude/skills/checkmyvibe/`
   - **Global Scope (Claude Code):** `~/.claude/skills/checkmyvibe/`
2. Ensure the following repository layout is preserved:

```text
checkmyvibe/
|-- SKILL.md
|-- scripts/
|   |-- check_auth_patterns.py
|   |-- check_db_config.py
|   |-- check_gitignore.py
|   |-- check_payment_config.py
|   `-- scan_secrets.py
|-- references/
|   `-- vibe_risk_patterns.md
|-- commands/
`-- adapters/
```

3. *(Optional)* Copy the command files from `commands/` into `.claude/commands/` (or `~/.claude/commands/`) to register slash commands.

---

## Local Execution and Privacy

- **Zero Runtime Dependencies:** `checkmyvibe` requires no third-party npm runtime dependencies, eliminating supply-chain attack vectors.
- **Fully Local Analysis:** All scanning runs locally on your machine using your local Python 3 interpreter and coding assistant. No code, tokens, or repository metadata are transmitted to external verification endpoints.
- **Cross-Platform:** Works on Linux, macOS, and Windows. Automatically resolves between `python` and `python3` binary paths.

---

## Scope and Disclaimer

> [!WARNING]
> **`checkmyvibe` is not an alternative to an external security audit, penetration test, or formal compliance assessment (SOC2, HIPAA, PCI-DSS).**
>
> It functions as an automated first-pass readiness filter designed to identify common scaffolding shortcuts, placeholder logic, and configuration vulnerabilities introduced by AI coding tools during rapid development. Applications processing sensitive consumer data, protected health information, or high-volume financial transactions should undergo formal human security reviews prior to release.

---

## Contributing

Contributions addressing new AI code patterns, framework quirks, or payment provider configurations are welcome.

1. Fork the repository: [github.com/Sarthakpatil23/checkmyvibe](https://github.com/Sarthakpatil23/checkmyvibe)
2. Add your pattern or script test case under `scripts/` or `SKILL.md`.
3. Open a Pull Request detailing the pattern, its risk profile, and suggested remediation.

---

## License

This project is licensed under the [Apache 2.0 License](LICENSE).