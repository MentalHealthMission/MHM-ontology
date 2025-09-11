# ODIM‑MH – Engineering Guide for Coding Agents

## Table of Contents
- Project Overview (quick)
- First Steps for a New Agent (verification & alignment)
- Repository Map (key paths)
- Local Setup (checks first)
- Workflow: Issues → Branch → PR
  - Note on public plan
  - Task selection and user consultation
- Labels (conventions)
- Maintaining the Plan (AGENT-PLAN.md)
- Branch Protection (settings)
- Ontology Tasks Cheat‑Sheet
- Ontology Change Checklist (TBox/ABox)
- Public Website (pre‑w3id)
- Safety & Boundaries
- Quick Commands
- Contacts

This guide sets expectations for coding agents and contributors working on ODIM‑MH. It covers local setup (GitHub CLI auth) and a lightweight, issue‑driven workflow using GitHub Issues and PRs via `gh`.

## Project Overview (quick)

- Aim: represent high‑level digital markers derived from wearable/mobile sensing in health studies. Model how raw measurements become features, how computations are described/attributed, and how results are situated in time and context.
- Design: DL‑safe core ontology; DL‑safe references to SOSA (observations), SKOS (vocabularies), QUDT (units); separate PROV‑O alignment module.
- Naming/prefix: public name ODIM‑MH; recommended prefix `odim:` → `http://connectdigitalstudy.com/ontology#` (pending w3id namespace migration).
- Read next: `docs/ontology-overview.md` (high‑level) and `docs/technical-overview.md` (detailed modeling + standards).

## First Steps for a New Agent (verification & alignment)
- Confirm environment
  - `gh auth status` shows logged‑in user (SSH); if not, ask to run `gh auth login`
  - `docker version` available; if not, confirm whether to proceed without tooling
  - Run profile and validators to establish baseline; report results succinctly
- Align on task
  - Offer 2–4 next steps from `AGENT-PLAN.md` with brief impact; confirm selection with the user
  - If the task touches the public roadmap, confirm adding/updating an entry in `plan.md` via docs PR first
- Proceed
  - Create a short‑lived branch from `main`, open an Issue (if not existing), and begin work per the chosen task
  - Minimize interruptions; ask only essential clarifications

## Repository Map (key paths)

- Root
  - `mhm_ontology.owl`: core ontology
  - `examples.ttl`: example individuals (ABox)
  - `plan.md`: public plan (authoritative, non‑agentic)
  - `AGENT-PLAN.md`: agent execution notes (local‑only)
- Vocabularies: `vocab/` (SKOS schemes + tags)
- Queries: `queries/` (`prov_*.rq`, `sosa_*.rq`, `units_*.rq`, `skos_*.rq`)
- Alignments: `alignments/mhm-prov-align.owl`
- Tooling: `tooling/` (Dockerfile, run_ontology_tools.sh)
- Docs: `docs/ontology-overview.md`, `docs/technical-overview.md`, `docs/codebase-overview.md`

## Local Setup (checks first)

- Verify Git identity
  - Check: `git config --get user.name && git config --get user.email`
  - If missing: prompt the user to set name/email; do not change config without confirmation.
- Verify GitHub CLI auth (gh)
  - Check: `gh auth status`
  - If not logged in: ask the user “Run gh auth login with SSH now?” and proceed only on approval.
  - Optional SSH test: `ssh -T git@github.com` (will prompt on first use).
- Verify Docker availability
  - Check: `docker version`
  - If unavailable: inform the user and ask whether to install/continue without local tooling.
- Verify tooling image
  - Check: `tooling/run_ontology_tools.sh build` only after confirming Docker is available (safe to run multiple times; uses cache).
- Repository sanity checks
  - Syntax/profile: `tooling/run_ontology_tools.sh check-syntax mhm_ontology.owl && tooling/run_ontology_tools.sh profile mhm_ontology.owl DL`
  - Validators: `tooling/run_ontology_tools.sh validate-units && tooling/run_ontology_tools.sh validate-sosa && tooling/run_ontology_tools.sh validate-skos && tooling/run_ontology_tools.sh validate-prov`
  - If any fail: surface the failure succinctly and ask whether to investigate now or proceed with planned task.

## Workflow: Issues → Branch → PR

- Plan: create or reference a GitHub Issue describing the task and acceptance checks; link related items in `AGENT-PLAN.md`.
  - Before starting: search for an existing Issue (`gh issue list --search "<keywords>"`) and link it.
  - If none exists: ask the user for confirmation, then create one (`gh issue create --title "type(scope): subject" --body "- Goal: …\n- Acceptance: …"`).
- Branch naming:
  - `feature/<topic>` for features/modeling
  - `fix/<topic>` for bug fixes
  - `docs/<topic>` for documentation
  - `chore/<topic>` for tooling/infra
- Local changes: keep scoped; update docs/examples/queries and `AGENT-PLAN.md` when relevant; run validators locally.
- Commit routine: clear, imperative subjects; group related changes.
  - Examples: `feature(skos): add Question Domain scheme`, `docs(readme): clarify namespaces`, `fix(queries): prefer odim: prefix`
- Push and PR with `gh`:
  - `git push -u origin <branch>`
  - Name PRs for squash merges using "Type/topic" format. The PR title becomes the squash commit subject:
    - Preferred: `Feature/<topic>`, `Fix/<topic>`, `Docs/<topic>`, `Chore/<topic>`, `CI/<topic>`
    - Examples:
      - `Feature/odim-mh branding (#5)`
      - `Feature/docs overview (#4)`
      - `Chore/ci validators (#9)`
    - If using Conventional Commits during development (`type(scope): subject`), convert to the above for the PR title before squashing.
  - Include commit summaries in the squash message: when clicking “Squash and merge”, expand “Commit message” and keep the auto‑generated list of commits (or add a concise bullet list yourself).
  - Repo default for squash messages: this repo is configured to prefill the squash commit title with the PR title and the body with the list of commit messages. To change defaults:
    - `gh api -X PATCH repos <OWNER>/<REPO> -f squash_merge_commit_title=PR_TITLE -f squash_merge_commit_message=COMMIT_MESSAGES`
    - Allowed values:
      - `squash_merge_commit_title`: `PR_TITLE` or `COMMIT_OR_PR_TITLE`
      - `squash_merge_commit_message`: `PR_BODY`, `COMMIT_MESSAGES`, or `BLANK`
  - Agent-generated squash messages: agents should explicitly provide a curated squash body that starts with a one-line change summary followed by detailed bullets. Keep the auto-generated commit list only if it adds value beyond the curated bullets.
    - Recommended structure for the squash message body:
      - First line: `<area>: <short change summary>`
        - Example: `branding: adopt ODIM-MH name and odim: prefix (no IRI changes)`
      - Then a concise bullet list of notable changes:
        - `- Set ontology label/title to ODIM-MH`
        - `- Add odim: prefix mapped to CONNECT base`
        - `- Prefer odim: in examples, vocab, queries`
        - `- Update README and docs to reference ODIM-MH`
        - `- Narrow validate-prov to queries/prov_*.rq`
      - Close with issue linkage if not already: `Closes #NN`.
    - CLI example to merge with curated subject/body (use different envs/users as needed):
      - `SUBJ=$(gh pr view <PR#> -q .title --json title)`
      - `BODY=$'branding: adopt ODIM-MH name and odim: prefix (no IRI changes)\n\n- Set ontology label/title to ODIM-MH\n- Add odim: prefix mapped to CONNECT base\n- Prefer odim: in examples, vocab, queries\n- Update README and docs to reference ODIM-MH\n- Narrow validate-prov to queries/prov_*.rq\n\nCloses #NN'`
      - `gh pr merge <PR#> --squash --subject "$SUBJ" --body "$BODY"`
  - Create PR with a multiline body using one of:
    - `$'...'` quoting (expands newlines):
      - `gh pr create --base main --title "type(scope): subject" --body $'Closes #NN\n\nSummary line 1\n\nDetails line 2'`
    - Body file (robust for longer text):
      - `cat > /tmp/pr_body.md <<'EOF'` then write content, end with `EOF`
      - `gh pr create --base main --title "type(scope): subject" --body-file /tmp/pr_body.md`
  - Link issue in body (e.g., `Closes #123`); `gh pr ready` when reviewable
  - Include the task's Acceptance checklist in the PR body for reviewers
  - Optional: add labels to the PR (mirrors issue triage)
    - `gh pr edit <PR#> --add-label "type: ci" --add-label "scope: gh-setup"`
- PR checklist:
  - [ ] Syntax/profile pass
  - [ ] All validators pass: units / sosa / skos / prov
  - [ ] Docs updated (README, `docs/*.md`), examples/queries adjusted if impacted
  - [ ] `AGENT-PLAN.md` updated if scope touches roadmap
  - Branch lifecycle after merge
   - Confirm the PR is merged (via GitHub UI or `gh pr view --web`)
   - Delete remote branch: `git push origin --delete <branch>`
   - Delete local branch: `git branch -d <branch>`
   - Each task lives in its own short‑lived branch
### Note on public plan
- For non‑agentic work, update `plan.md` via a docs‑only PR first (authoritative plan), then record execution notes in `AGENT-PLAN.md`.

### Task selection and user consultation
- Present 2–4 viable options from `AGENT-PLAN.md` (e.g., A1 Pages landing, A5 CI for latest, B3 CI validators, or a small ontology fix), with one‑line impact summaries.
- If the user has a preference, follow it. If unclear, propose a default that unblocks the next phase (e.g., A1, then A2/A5).
- Ask only essential clarifying questions. Assume sufficient context from this repo + AGENTS/PLAN; avoid trivia.

## Maintaining the Plan (AGENT-PLAN.md)

- Purpose: orient contributors and provide assignable tasks; keep concise and current.
- Structure: Context snapshot, Public plan mirror/sync, Part A (Public‑facing), Part B (GitHub setup), Part C (Namespace migration prep).
- Add a task using this template:
  - Title: `type(scope): subject` (e.g., `docs(pages): add index.html`)
  - Context: why this is needed now, links to files
  - Goal: one‑sentence outcome
  - Steps: numbered, actionable list
  - Acceptance: clear checks (URLs exist, validators pass, settings applied)
  - Deliverables: files/paths updated, PR link, Issue number
- Linkage:
  - Public tasks MUST first be added to `plan.md` via docs PR (authoritative plan), then referenced in AGENT‑PLAN.md with execution notes.
  - Create an Issue for each task and add `(Issue #NN)` next to the plan line in `plan.md`.
  - In the PR body include `Closes #NN` to auto‑close on merge.
  - Label issues/PRs for triage and scope (examples):
    - `gh issue edit <NN> --add-label "type: ci" --add-label "scope: gh-setup"`
    - `gh pr edit <NN> --add-label "type: ci" --add-label "scope: gh-setup"`
  - Commit cadence for plan and features:
    - Make small, frequent commits on feature branches; push early and keep PRs open.
    - After completing a feature slice, add a separate commit updating `AGENT-PLAN.md` (Working Branches Log, notes). Keep plan/docs commits separate from ontology/code changes.
    - For public plan updates, open a docs‑only PR to `plan.md` first, then reference it from `AGENT-PLAN.md`.
  - Sync agent docs back to private overlay (remote): if this repo includes the injected helper `tooling/overlay_sync_remote.sh`, run:
    - `tooling/overlay_sync_remote.sh --remote james-c/agent-overlays --key MHM-ontology --open-pr`
    - This writes updates (AGENTS.md, AGENT-PLAN.md, key tooling) directly to the overlay repo via a branch + PR. Do not commit agent-only files here.
- Example entry:
  - docs(pages): add index.html (Issue #42)
    - Context: publish minimal landing for GitHub Pages
    - Goal: landing page with links to docs and artifacts
    - Steps: create `docs/index.html`; add links; commit on `docs/pages-landing`
    - Acceptance: `https://…/MHM-ontology/` loads; links work
    - Deliverables: `docs/index.html`, PR #.., Closes #42

### Working Branches Log (local)
- Keep a short list in `AGENT-PLAN.md` to coordinate across agents (example):
  - [ ] branch: `docs/pages-landing` → PR #___ (open) — owner: @handle
  - [ ] branch: `chore/ci-validators` → PR #___ (open) — owner: @handle
- [x] branch: `feature/odim-branding-phase-b` → PR #___ (merged) — owner: @handle (remote/local deleted)

## Labels (conventions)

- Purpose: standardize triage and scope; automation keeps labels in sync.
- Source of truth: `.github/labels.yml` (synced by `.github/workflows/labels.yml`).
- Categories to apply on each Issue/PR:
  - Type: one of `type: feature`, `type: fix`, `type: docs`, `type: chore`, `type: ci`.
  - Scope: one of `scope: ontology`, `scope: vocab`, `scope: queries`, `scope: tooling`, `scope: docs`, `scope: gh-setup`.
  - Status: optional workflow indicator `status: needs triage`, `status: in progress`, `status: blocked`, `status: ready for review`.
- Usage:
  - Issues: add 1 Type + 1 Scope during triage; update Status as work progresses.
  - PRs: mirror the linked Issue’s Type/Scope; set `status: ready for review` when handing off.
  - Commands:
    - `gh issue edit <NN> --add-label "type: ci" --add-label "scope: gh-setup"`
    - `gh pr edit <NN> --add-label "type: ci" --add-label "scope: gh-setup"`
  - Notes: The sync workflow does not prune by default; custom labels remain unless manually removed.

## Ontology Tasks Cheat‑Sheet

## Branch Protection (settings)

- Goal: require PRs and CI to pass before merging into `main`.
- Required checks (names must match jobs):
  - `check-syntax`, `profile-dl`, `validate-units`, `validate-sosa`, `validate-skos`, `validate-prov`.
- GitHub UI path: Settings → Branches → Branch protection rules → Add rule → Branch name pattern `main` → enable:
  - Require a pull request before merging (min. 1 approving review)
  - Require status checks to pass before merging, then select the six checks above; require branches up to date.
  - Require conversation resolution before merging
  - Do NOT allow force pushes or deletions
  - Enforce for admins (recommended)
- CLI (requires admin permission on repo):
  - `gh pr view 9 --json commits -q '.commits[-1].oid'` then list check runs with `gh api repos <OWNER>/<REPO>/commits/<SHA>/check-runs --jq '.check_runs[].name'` to confirm names.
  - Apply protection:
    - `gh api -X PUT repos <OWNER>/<REPO>/branches/main/protection --input protection.json`
    - Where `protection.json` contains required review and checks configuration; see comments in Issue #11.
  - Recommended (no local token): use the Branch Protection workflow with a repo secret:
    - Add repository secret `REPO_ADMIN_TOKEN` (fine‑grained PAT with Administration: write on this repo).
    - Run the `Branch Protection` workflow (workflow_dispatch). It uses `actions/github-script` with `github-token: ${{ secrets.REPO_ADMIN_TOKEN }}` to call the admin API and apply settings. The secret is masked in logs and not exposed to PRs from forks.

- Core ontology: `mhm_ontology.owl` (DL‑safe); keep imports minimal
- Examples: `examples.ttl` (ABox, showcase patterns)
- SKOS vocabularies: `vocab/*.ttl`; tags: `vocab/skos-tags.ttl`
- SPARQL checks: `queries/*.rq` (ASK queries by topic)
- Tooling wrapper: `tooling/run_ontology_tools.sh` (profile, report, validators)

## Ontology Change Checklist (TBox/ABox)
- Add `rdfs:label` (and `skos:prefLabel@en` where using SKOS); optional `IAO:0000115` definition
- Prefer `odim:` prefix; keep changes DL‑safe; avoid new imports
- If adding SKOS concepts: include `skos:inScheme`, top concepts if applicable, and language‑tagged labels; extend `queries/skos_*.rq` if needed
- Update examples to illustrate new patterns; keep examples in `examples.ttl`
- Add/adjust SPARQL ASK queries to validate new modeling
- Run all validators and ensure README/docs mention new user‑facing patterns

 

## Agent Interaction Guidelines
- Use a checks‑first approach: verify state before proposing actions
- Be explicit about what you will run; get approval for installs or config changes
- Summarize options and recommend a default when the path is ambiguous
- Avoid unnecessary questions; assume the repository + this guide provide sufficient context unless a real blocker emerges
 - Comments on Issues/PRs: write as the USER addressing repo readers/contributors (not agent→user). Avoid referring to “the agent”; use first‑person where appropriate.

### Admin actions and tokens (one‑off)
- Some repo settings (e.g., branch protection) require admin permissions. Use a separate admin token only when needed:
  - Create a fine‑grained PAT: Settings → Developer settings → Fine‑grained tokens
    - Resource owner: organization owning this repo
    - Repository access: this repository
    - Permissions: Administration → Read and write
  - Preferred: store locally in `.env` (not committed). Use `.env.example` as a template, then:
    - `cp .env.example .env` and paste the token into `GH_ADMIN_TOKEN=`
    - Run admin scripts that read the token from `.env`:
      - `bash tooling/apply_branch_protection.sh`
  - Alternative (one-off): export in shell for the command: `GH_TOKEN=$GH_ADMIN_TOKEN gh api …`

## Public Website (pre‑w3id)

- Use GitHub Pages (this repo) with `docs/` on `main`
- Publish:
  - `docs/index.html` (landing)
  - `docs/latest/odim-mh.ttl` and `docs/latest/odim-mh.owl` (machine‑readable)
  - Optional: `docs/releases/vX.Y.Z/…` snapshots; `docs/contexts/odim-mh.jsonld`
- These will become targets for w3id redirects when the namespace is live

## Safety & Boundaries

- No secrets or personal data in the repo
- Keep core in OWL DL profile; use separate modules for OWL Full if needed
- Do not change base IRIs without an approved migration plan (see `AGENT-PLAN.md`)

## Quick Commands

- Build tools: `tooling/run_ontology_tools.sh build`
- Syntax: `tooling/run_ontology_tools.sh check-syntax mhm_ontology.owl`
- Profile: `tooling/run_ontology_tools.sh profile mhm_ontology.owl DL`
- Report: `tooling/run_ontology_tools.sh report mhm_ontology.owl`
- Validate: `tooling/run_ontology_tools.sh validate-units|validate-sosa|validate-skos|validate-prov`

## Contacts

- Maintainer: @james-c (Mental Health Mission)
- Organization: Mental Health Mission — mention for reviews as needed

---
Note: `AGENTS.md` is locally ignored via `.git/info/exclude` to allow iterative drafting. Remove the exclude entry and commit when ready to share.
