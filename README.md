# checkmyvibe

A structured, zero-dependency, local production readiness and code quality workflow packaged as an Agent Skill for AI coding assistants (such as Claude Code, Cursor, Codex, and Gemini CLI).

AI-generated ("vibe-coded") applications built on modern AI tools frequently ship with serious, well-documented configuration and quality issues—such as exposed API keys, fake authentication stubs, permissive default database rules, and client-side pricing logic. **checkmyvibe** solves this by packaging readiness and verification checks directly into an Agent Skill. When you ask your coding agent to "run checkmyvibe" or "perform a readiness check", the agent uses checkmyvibe's local helper scripts and its own reasoning capabilities to analyze your codebase, producing a prioritized report detailing what configuration issues or gaps exist, why they matter, and how to fix them.

---

## What This Checks For

*   **Exposed Secrets & API Keys:** Identifies hardcoded API keys, JWT secrets, database credentials, and high-entropy strings across your files (using standard prefixes like `sk_live`, `AIza`, `AKIA`, and `ghp_`).
*   **Version Control Leakage:** Verifies if sensitive files (like `.env`) exist in the project but are not properly excluded in your `.gitignore` file.
*   **Fake & Stubbed Authentication:** Greps for common mock authentication markers (such as functions named `mockAuth`, `fakeLogin`, `tempAuth`, or logic that returns `true` unconditionally to bypass authentication checks).
*   **Database Misconfigurations:** Identifies permissive default rules (such as `allow read, write: if true;` in Firebase/Firestore configs) and checks if Row-Level Security (RLS) is enabled on Supabase database schemas.
*   **Broken Object-Level Authorization (BOLA/IDOR):** Analyzes API routes to check if endpoints fetch resources by ID without validating that the authenticated user owns or has permission to access that resource.
*   **Client-Side Payment & Pricing Logic:** Scans checkout routes and payment integrations to check if prices or transaction values are calculated or accepted directly from client-side parameters rather than securely fetched on the server.

---

## What This Does NOT Check For (Disclaimer)

> [!WARNING]
> **checkmyvibe is not a substitute for a full professional external security audit.**
> This tool is a first-pass quality and readiness checklist meant to highlight common mistakes and temporary scaffolding shortcuts made by AI coding models during rapid prototyping. It does not perform dynamic runtime analysis, penetration testing, deep static analysis, dependency vulnerability checks, or comprehensive logic auditing. Do not rely solely on checkmyvibe to declare your application hardened for production.

---

## Installation

### Method 1: Using npx (Recommended)
You can install and copy the skill automatically to your project or global environment by running:

```bash
npx checkmyvibe
```

The installer will detect if you have a `.claude` configuration directory in your project root and offer to install it either locally (project-level) or globally for your user.

### Method 2: Manual Installation
If you prefer not to use `npx`, copy the files manually:

1. Create a `checkmyvibe` directory inside your agent's skills path:
   * **Project-level (Claude Code):** `.claude/skills/checkmyvibe/`
   * **Global/Personal (Claude Code):** `~/.claude/skills/checkmyvibe/`
2. Copy `SKILL.md`, the `scripts/` folder, and the `references/` folder into that directory.

---

## Usage

Once installed, your AI coding agent will automatically recognize the `checkmyvibe` skill when relevant. You can trigger the workflow explicitly:

### Claude Code / Gemini CLI
Open your terminal in the workspace and ask:
> "Run checkmyvibe on this project"
*Or:*
> "Perform a production readiness check using checkmyvibe"

The agent will walk through the checks, execute the local python validation scripts, and print a prioritized markdown report (Critical / Should Fix / Worth Reviewing) with instructions on how to correct the issues.

---

## License

This project is open-source and licensed under the [Apache 2.0 License](LICENSE).