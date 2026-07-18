---
name: checkmyvibe
description: >
  Use this skill when the user asks to "check my vibe", run a production readiness check, review code quality, do a sanity check, check for exposed environment variables, or check if the app is ready to launch/ship. Also trigger proactively when the agent is about to help deploy, publish, or push an application live, or when the codebase shows signs of AI-scaffolded patterns (Supabase/Firebase config, recently generated boilerplate, auth stubs, no existing verification) and the user has not had one done yet. Covers checking for missing or placeholder authentication, exposed secrets, permissive database rules, object-level authorization, input validation, and pricing configuration in client bundles.
---
# checkmyvibe — Production Readiness & Code Quality Check for Vibe-Coded Apps

## Why this skill exists

AI coding tools optimize for "it works," not "it's production-ready." A feature can pass every
manual test a non-technical founder runs — sign up, log in, place an order — and
still leak every other user's data to a stranger who changes one number in a URL.
This happens because AI-generated code frequently ships with scaffolding shortcuts
that were meant to be temporary (a stub auth check, a permissive default database
rule) and never get hardened before launch, precisely because the person building
the app doesn't know those shortcuts exist or what to look for.

Your job when this skill is active: think like an experienced software engineer doing a
pre-launch quality review for a client who has never heard the words "IDOR" or "row-level
security." Find the real, addressable configuration and logic issues. Explain them in plain
language. Give exact fixes. Do not pad the report with theoretical concerns that don't apply
to this specific codebase, and do not skip a check because the codebase "looks simple" —
simple codebases are exactly where stubbed auth and hardcoded secrets hide, because nobody
expected them to hold real user data yet.

## Scope and honesty (read this before writing any report)

This is a first-pass review for known, documented scaffolding failure patterns. It is not a
comprehensive external validation, and it does not cover infrastructure hosting, third-party package
issues, or novel/business-logic-specific flaws outside the six categories
below. Never tell the user their app is completely "secure" or "safe" in an unqualified way.
The correct language is "no issues found in this pass" or "ready to ship as far as
these checks go" — always paired with the scope reminder in the Final Summary
section. If the app appears to handle payments, health data, or other regulated
data, say explicitly that a professional verification is strongly recommended regardless
of what this pass finds.

## Before you start

1. **Analyze and understand the whole project first:** Walk the directory tree and analyze the repository configuration files before running any checks, generating findings, or providing instructions. Establish a solid high-level understanding of the architecture, components, and data flow.
2. Identify the stack: what backend/framework, what database or BaaS provider
   (Supabase, Firebase, custom Postgres, etc.), what auth approach is in use.
   This changes which checks apply and how to phrase findings.
3. Identify what data the app handles: user accounts, payments, health data,
   messages between users, files. This changes severity judgments — the same
   missing check is more severe on an app handling payment data than on a toy
   to-do list.
4. Run the checks below in order. Use the bundled scripts where noted. For
   everything else, read the actual code — don't rely on file names alone.

---

## Supported stacks to recognize

Common stacks this skill should expect include: Next.js, Express, FastAPI, Supabase, Firebase, Prisma, Postgres, MongoDB, Clerk, NextAuth, Stripe, and common app patterns built around them.

## Evidence and confidence rules

- Only flag something when there is evidence in the code.
- Do not guess from filenames, comments, or variable names alone.
- If something looks suspicious but is not fully proven, mark it with a confidence tag such as `High confidence`, `Medium confidence`, or `Needs manual review`.
- Do not overflag. Prefer one precise finding over several weak or duplicate ones.

## Fix priority

When multiple issues are found, sort them in this order:
Critical user exposure > auth bypass > IDOR > payment logic > config issues > hygiene.

## What success looks like

The report should help the coding agent make the repo safer in the next commit, not just describe problems.

## Check 1: Exposed secrets and credentials

**Run the script** `scripts/scan_secrets.py` (located relative to this `SKILL.md` file) against the project root. It flags known key
prefixes (`sk_live`, `sk_test`, `AIza`, `AKIA`, `ghp_`, `xox[bp]`), high-entropy
strings, and variable assignments where a name like `key`, `secret`, `token`, or
`password` is set to a literal string instead of `process.env.X` or equivalent.

**What counts as a finding:**

- A real credential committed directly in source, e.g.:
  `const stripeKey = "sk_live_51H8x..."` — Critical
- A secret present only in `.env` but `.env` is not gitignored (see Check 2) —
  Critical, because it WILL leak on the next commit even if it hasn't yet
- A secret exposed to the client bundle — e.g. a server-only key referenced in
  frontend code, or a Next.js env var missing the required server-only scoping
  (using a secret key where only `NEXT_PUBLIC_`-prefixed vars should appear) —
  Critical, this is directly shippable to every visitor's browser

**What is NOT a finding (avoid false positives):**

- Public/anon/publishable keys that are designed to be exposed client-side
  (Stripe publishable keys starting `pk_`, Supabase anon keys) — these are safe
  by design as long as server-side authorization (RLS, API checks) is correctly
  configured. Note this distinction explicitly in the report so the user isn't
  confused about why one key is fine and another isn't.
- Example/placeholder values clearly meant as documentation, e.g. `"your-api-key-here"`

## Check 2: .gitignore hygiene

**Run the script** `scripts/check_gitignore.py` (located relative to this `SKILL.md` file) against the project root. It checks whether `.env`, `.env.local`, and
similar files exist in the project and whether `.gitignore` actually excludes
them (not just whether a `.gitignore` file exists — many AI-generated `.gitignore`
files exist but miss the actual secret file).

**What counts as a finding:**

- `.env` present in the working directory and not listed in `.gitignore` —
  Critical, regardless of current contents
- `.env` already committed to git history (check with a quick `git log --all --full-history -- .env` if git is available) — Critical, and note in the
  fix that removing it from `.gitignore` going forward is not enough; the
  secrets in git history must be rotated, since they're recoverable even after
  deletion

## Check 3: Missing or fake authentication

**Run the script** `scripts/check_auth_patterns.py` (located relative to this `SKILL.md` file) against the project root as a first pass. Then search auth-related code (login handlers, middleware, route guards, session
checks) for these patterns:

**What counts as a finding:**

- A function that always returns true/success regardless of input, e.g.:
  ```js
  function isAuthenticated(req) {
    return true; // TODO: implement real auth
  }
  ```

  Critical — this is a placeholder someone forgot to replace.
- Naming that signals a stub: `mockAuth`, `fakeLogin`, `tempAuth`, `bypassAuth`,
  `skipAuth`, `devAuth` still present in a codebase with no clear dev-only guard
  around it. If it IS properly guarded (e.g. `if (process.env.NODE_ENV === 'development')`), verify the guard is airtight and note it as Should Fix
  rather than Critical, since misconfigured environment variables in production
  are a common way these leak through anyway.
- A protected route or API endpoint with no auth check at all — compare route
  definitions against which ones return or modify user-specific data.
- Client-side-only auth checks — e.g. hiding a button in the UI if not logged in,
  but the underlying API endpoint doesn't independently verify the session.
  This is Critical: anyone can call the API directly, bypassing the UI entirely.
- Auth checks present but commented out, with a bypass left active nearby.

**Judgment note:** this check benefits most from your own reasoning rather than
pure pattern matching, since real projects name things inconsistently. If
something looks like it might be a stub but you're not certain, read the
function body fully before deciding — don't flag based on the name alone, and
don't clear something based on the name alone either.

## Check 4: Database and backend-as-a-service misconfiguration

**Run the script** `scripts/check_db_config.py` (located relative to this `SKILL.md` file) against the project root as a first pass.

If the project uses **Supabase**: check for row-level security (RLS) policies on
every table that holds user-specific data. A table with RLS disabled, or enabled
with a policy like `USING (true)` for `SELECT`/`UPDATE`/`DELETE`, means any
authenticated (or even anonymous) user can read or modify every row.

```sql
-- Finding example: this policy applies to ALL rows for ALL users
CREATE POLICY "allow all" ON orders FOR SELECT USING (true);

-- Correct pattern to recommend as the fix:
CREATE POLICY "users see own orders" ON orders
  FOR SELECT USING (auth.uid() = user_id);
```

If the project uses **Firebase**: check `firestore.rules` or `storage.rules` for
default-allow states, e.g. `allow read, write: if true;` on collections holding
user data, or rules left at the Firebase default test-mode state (which expires
but is often copy-pasted into production-like configs).

**Storage buckets**: check whether file storage (Supabase Storage, Firebase
Storage, S3) is set to public when it holds user-uploaded content that should be
private (profile documents, private images, receipts).

## Check 5: Broken object-level authorization (IDOR)

This is the single most common serious flaw in vibe-coded apps and the one most
worth spending real time on. The pattern: an endpoint takes an ID from the
request and fetches/modifies a resource using that ID, without checking the
resource actually belongs to the requesting user.

```js
// Finding example — Critical
app.get('/api/orders/:id', requireAuth, async (req, res) => {
  const order = await db.query('SELECT * FROM orders WHERE id = $1', [req.params.id]);
  res.json(order); // any logged-in user can read ANY order by guessing/incrementing the id
});

// Correct pattern to recommend as the fix
app.get('/api/orders/:id', requireAuth, async (req, res) => {
  const order = await db.query(
    'SELECT * FROM orders WHERE id = $1 AND user_id = $2',
    [req.params.id, req.user.id]
  );
  if (!order) return res.status(404).json({ error: 'Not found' });
  res.json(order);
});
```

Check every route that takes an ID as a URL param, query string, or body field
and touches a database record. This applies to GET (data exposure), PUT/PATCH
(unauthorized modification), and DELETE (unauthorized deletion) — all three are
common and DELETE is often the most damaging.

## Check 6: Unvalidated inputs

Spot-check forms and API endpoints for:

- No type or length validation on inputs before they're stored or used
- User input passed into a database query via string concatenation rather than
  parameterized queries/an ORM (SQL injection risk)
- User input rendered into HTML without escaping (XSS risk), especially in
  frameworks that don't auto-escape by default
- File uploads with no restriction on file type or size

This check doesn't need to be exhaustive — flag the clearest, highest-impact
examples rather than every single form field, and note in the summary that a
full input-validation review is a good idea if the codebase is large.

## Check 7: Client-side payment or pricing logic

Search checkout/payment flows for the price, discount, or total being read from
data the client controls (a hidden form field, a request body value, a query
param) rather than looked up server-side from a trusted source.

```js
// Finding example — Critical
app.post('/api/checkout', async (req, res) => {
  const { productId, price } = req.body; // price is trusted from the client!
  await chargeCard(req.user.paymentMethod, price);
});

// Correct pattern to recommend as the fix
app.post('/api/checkout', async (req, res) => {
  const { productId } = req.body;
  const product = await db.query('SELECT price FROM products WHERE id = $1', [productId]);
  await chargeCard(req.user.paymentMethod, product.price); // price comes from the server
});
```

---

## Severity rubric

- **Critical** — exploitable right now by any user or visitor, exposes real user
  data, or allows bypassing authentication or payment. Ship-blocking.
- **Should Fix** — a genuine weakness that requires more specific conditions to
  exploit (e.g. requires knowing another user's exact ID, or only affects an
  admin-only route with a smaller blast radius), or a control that exists but is
  incomplete/inconsistent.
- **Worth Reviewing** — best-practice gap with low immediate exploitability
  given the current app, but worth fixing before the app scales or handles more
  sensitive data.

When in doubt between two levels, consider: could a stranger with no special
access do real harm to a real user right now? If yes, Critical.

## Report format

For every finding, use exactly this structure:

- Include a short `Confidence:` line when the evidence is not fully conclusive.
- Include a `Generated fix:` line when a direct code snippet or precise implementation step would help the agent patch the issue immediately.

**[SEVERITY] Short title**

- **What's wrong:** plain-English description, no jargon. If a technical term is
  unavoidable (e.g. "IDOR"), define it in one clause the first time it's used.
- **Why it matters:** a concrete, real-world consequence a non-technical person
  would understand — not "this violates the principle of least privilege" but
  "a stranger could see another user's home address and order history just by
  changing a number in the browser's address bar."
- **The fix:** a specific code snippet or precise instruction, not a vague
  suggestion like "add proper validation."
- **File(s):** exact path and line number(s).

## After the checks

Once the checks are complete, create a readiness review report. **The report must be written in clear, plain English, completely free of dense technical jargon, so that it is easily understandable by non-technical stakeholders (such as founders, clients, or project managers).** The report must include:

- what was found
- what is fixed already
- how each fix was applied
- what still needs attention
- the final readiness verdict

If no issues are found, still produce a short report that says no blocking issues were found in this pass, which categories were checked, and what the remaining scope limits are.

## Example report style

Use clear, direct wording like:

**[Critical] Missing object-level authorization**

- **What's wrong:** Any logged-in user can read another user's order by changing the order ID.
- **Why it matters:** A stranger could see someone else's orders and personal details.
- **The fix:** Add a user ownership check in the query and return 404 when the record does not belong to the current user.
- **File(s):** `src/routes/orders.ts:42-58`

## Final summary

End every review with, in this order:

1. Stack and data-sensitivity context noted at the start (one line)
2. Total findings by severity, e.g. "2 Critical, 3 Should Fix, 1 Worth Reviewing"
3. A one-line verdict: "Not ready to ship — fix the Critical items first" or "No
   blocking issues found in this pass — review the Should Fix items when you can"
4. The scope reminder: "This review covers common configuration patterns seen in AI-generated code —
   exposed secrets, auth stubs, database rules, object-level authorization, input validation,
   and client-side payment logic. It is not a comprehensive third-party safety audit or pentest. If this app
   handles payment, health, or other regulated data, get a professional external review
   before launch regardless of these results."

## Notes for the agent

- Always produce a review report after the check; do not stop at raw findings.
- Write the entire report in clear, accessible language. Frame findings around concrete, real-world user consequences rather than abstract technical concepts. A non-technical stakeholder must be able to read the report and immediately understand the real-world danger.
- The review should clearly separate what was found, what was fixed, how it was fixed, and what remains.
- Always run the available scripts (located in the `scripts/` directory relative to this `SKILL.md` file) before relying on reasoning alone for Checks 1-4 — they exist so those specific checks are reliable and repeatable rather than dependent on re-deriving the logic every time.
- If a script is missing, fails to run, or the language/stack isn't supported by
  it, say so explicitly in the report ("automated secret scan could not run;
  manually reviewed instead") rather than silently skipping the check.
- Do not invent findings to seem thorough. If a check finds nothing, report "No
  issues found" for that category explicitly — silence looks like the check
  wasn't performed at all.
- Do not flag the same underlying issue multiple times under different check
  categories — pick the most relevant category and reference it once.
- If the codebase is large, prioritize routes and files that touch
  authentication, payments, and any endpoint returning data tied to a specific
  user ID — these are where real damage concentrates.
