# AI PR guardrails – starter repo

A sample setup for using an AI coding assistant (Cursor) safely with GitHub:
the **PR template asks**, the **workflow checks**, the **AI reviewer comments**,
**CODEOWNERS approves**, the **ruleset enforces**.

```
.github/
  pull_request_template.md   # pre-fills every PR description
  CODEOWNERS                 # who must approve which paths
  workflows/pr-policy.yml    # GitHub Action that checks the PR description and changed files
REVIEW.md                    # review checklist – used locally in Cursor and by the AI reviewer on PRs
.cursor/rules/billing.mdc    # Cursor AI rules for billing/ and pricing/
.cursorignore                # files Cursor's AI must never read
billing/ledger.py            # sample "money path" code
docs/notes.md                # sample low-risk file
```

**Who decides what**

| Check | Kind | Blocks the merge? |
|---|---|---|
| `pr-policy`, tests | Deterministic | Yes |
| AI review using `REVIEW.md` | Probabilistic | No – it only comments |
| Conversation resolution | A human answers each AI comment | Yes |
| CODEOWNERS approval | Human | Yes |

## 1. Set up (10 minutes)

1. Create a new GitHub repo (private is fine) and push these files to `main`.
2. In `.github/CODEOWNERS`, replace `@YOUR-GITHUB-USERNAME` with your GitHub username. Commit to `main`.
3. Open **Actions** tab → enable workflows if GitHub asks.
4. Optional: create the labels `ai-assisted` and `money-path` under **Issues → Labels** to pick colours. If they don't exist, GitHub creates them the first time the workflow adds them.
5. Add a branch ruleset: **Settings → Rules → Rulesets → New branch ruleset**
   - Name: `protect-main`, Enforcement: **Active**, Target: **Default branch**
   - ✅ Require a pull request before merging
     - Required approvals: `1`
     - ✅ Dismiss stale pull request approvals when new commits are pushed
     - ✅ Require review from Code Owners
     - ✅ Require conversation resolution before merging *(every AI or human review comment must be resolved)*
   - ✅ Require status checks to pass → add `check` (the job in `pr-policy`; it appears after the workflow has run once)
   - ✅ Block force pushes
   - Save.
6. Optional – turn on the AI reviewer (needs a GitHub Copilot plan or trial that includes code review):
   - Manual: on any PR, open **Reviewers** and pick **Copilot**.
   - Automatic: in the same ruleset, enable **Automatically request Copilot code review** (and **Review new pushes** if you want a re-review on every push).
   - Copilot reads `REVIEW.md` automatically. Leave it on **comment-only**; don't let it approve.

> Rulesets on **private** repos need GitHub Pro / Team / Enterprise. On a free account, make the repo **public** to test.
> Copilot code review uses GitHub AI Credits and Actions minutes, so it costs money on paid plans.

## 2. Test it

Create branches and open PRs into `main`:

| Test | Do this | Expected result |
|---|---|---|
| A. Empty form | Edit `docs/notes.md`, open PR, tick nothing | ❌ `pr-policy` fails: tick AI box and risk tier |
| B. Low-risk, done right | Same PR, edit description: tick "No AI used" + "Low" | ✅ passes (workflow re-runs on edit) |
| C. Under-declared money change | Edit `billing/ledger.py`, tick "AI-assisted" + "Medium" | ❌ fails: billing code must be High; labels `ai-assisted`, `money-path` added |
| D. Money change done right | Change tick to "High" | ✅ check passes, but merge still needs Code Owner approval |
| E. Large PR | Add 500+ lines anywhere | ⚠️ warning in the Actions log, not a failure |
| F. Weaken the reviewer in a money PR | In one PR, delete the "Never float" line from `REVIEW.md` **and** edit `billing/ledger.py`, tick "High" | ❌ fails: instruction files can't change with billing code; label `ai-instructions` |
| G. Change the reviewer on its own | Edit only `REVIEW.md`, tick "No AI used" + "Low" | ✅ check passes, but CODEOWNERS approval required |
| H. AI comments must be answered | Add Copilot as reviewer on test D; leave its comments open | 🔒 merge blocked until each comment is resolved (fixed or replied to) |

## 3. Things that will surprise you

- **You can't approve your own PR.** GitHub never counts the author as a reviewer, so with "Require review from Code Owners" on, your own billing PR stays blocked. To see the full flow, add a second GitHub account (or a colleague) as a collaborator and as a code owner. As a repo admin you can also tick "Merge without waiting for requirements" to bypass – which is exactly why bypass should be limited in real orgs.
- **CODEOWNERS must be on `main`** before it takes effect on PRs.
- **The status check name** shown in the ruleset is the job name (`check`), not the file name.
- **The AI reviewer reads `REVIEW.md` from the PR's own branch**, not from `main`. That's why test F exists: a PR could otherwise weaken the review rules and be reviewed under them. CODEOWNERS stops the edit from *merging*; the `pr-policy` check stops it from riding along with billing code.

## 4. Try the Cursor side

1. Open the repo in Cursor.
2. Open `billing/ledger.py` and ask the agent: *"add a function to apply a 10% discount"*.
3. The `billing.mdc` rule is attached automatically for `billing/**` files – the AI should use `Decimal`, not `float`.
   (Rules steer the AI but aren't guaranteed – that's why the GitHub checks exist.)
4. Create `.env` with a fake key and ask Cursor about it – `.cursorignore` keeps it out of the AI's context.
5. Before opening a PR, ask Cursor: *"Review my changes against REVIEW.md"*. This is the same checklist the PR reviewer uses, so you catch most comments before anyone else sees them.

## 5. Rolling out to a whole org

- Put `pull_request_template.md` in your org's special `.github` repository → it becomes the default for all repos without their own.
- Use **organisation rulesets** (Org Settings → Repository → Rulesets) to apply branch rules across many repos.
- Copy the workflow into a shared template repo, or require it via org rulesets on GitHub Enterprise.
