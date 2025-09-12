# ODIM‑MH – Workplan for Coding Agents

This plan orients new coding agents to the current repository state and lays out discrete, assignabWorking Branches Log (local coordination)
- Note: set "owner" to the GitHub account the agent is acting on behalf of (the human maintainer/user), not the agent name.
- [ ] branch: `docs/pages-landing` → PR #___ (open) — owner: @james-c — Task: A1
- [ ] branch: `feature/ontology-visualization` → PR #___ (open) — owner: @james-c — Task: A7 (Issue #15)
- [x] branch: `chore/ci-validators` → PR #9 (merged) — owner: @james-c — Task: B3
- [x] branch: `chore/labels` → PR #10 (merged) — owner: @james-c — Task: B6
- [x] branch: `chore/branch-protection-workflow` → PR #12 (merged) — owner: @james-c — Task: B2
- [x] branch: `feature/odim-branding-phase-b` → PR #___ (merged) — owner: @james-c — Task: branding Option B (remote/local deleted)s. Agents should work issue‑by‑issue with short branches and PRs. Validate all ontology changes using the Docker tooling under `tooling/`.

Context snapshot
- Name and prefix: ODIM‑MH (public name). Recommended prefix `odim:` → `http://connectdigitalstudy.com/ontology#` (pending w3id). Legacy `connect:` remains an alias.
- Core ontology: `mhm_ontology.owl` kept OWL DL with DL‑safe references to SOSA/SKOS/QUDT.
- Vocabularies: SKOS schemes in `vocab/` + tags in `vocab/skos-tags.ttl`.
- Examples and queries: `examples.ttl` and `queries/*.rq` with validators wired in `tooling/run_ontology_tools.sh`.
- Branding: Option B implemented (docs and examples use `odim:`). Option C (w3id namespace + IRIs migration) is planned.

How to work
- Use GitHub Issues to pick up a task. One task per PR.
- Branch names: `feature/<topic>`, `fix/<topic>`, `docs/<topic>`, `chore/<topic>`.
- Run validators locally: `tooling/run_ontology_tools.sh validate-units|validate-sosa|validate-skos|validate-prov`.
- PR checklist: syntax/profile pass, validators pass, docs updated, this plan updated if scope changes.
- Record keeping: for each active task, record the working branch and PR in the Working Branches Log below.

Acceptance criteria conventions
- Every task lists nested checkboxes. Acceptance criteria are satisfied when all nested checkboxes are checked and any URLs/services referenced are reachable.
- The corresponding GitHub Issue MUST include an "Acceptance" bullet list mirroring these checkboxes.
- The PR body SHOULD copy the Acceptance list for easy review, and reviewers check them off before merge.
- After merge, mark the top-level task checkbox here and close the linked Issue.
 - Agent tip: after a PR merges, verify status via `gh pr view <N> --json state,mergedAt` and check off the task here. If the task had sub‑items, ensure they’re all satisfied first.

Public plan mirror and sync
- Authoritative public plan: `plan.md` (committed). Keep all non‑agentic development work there.
- Agent‑only items (e.g., onboarding, local conventions, internal automation) live here only and NEVER in `plan.md`.
- When adding a new public task:
  1) Open an Issue describing the task and acceptance.
  2) Submit a docs‑only PR that adds the task to `plan.md` with a checkbox and references the Issue (e.g., `(Issue #NN)`).
  3) In this file, add an “Agent execution notes” line under the relevant section, referencing the same Issue. Do not fork the authoritative content.
- When updating an existing public task: change `plan.md` via PR first; then reflect any execution notes here.

---

Part A — Public‑Facing Materials (GitHub Pages, pre‑w3id)

- [ ] A1: Pages landing page (Issue #____) — Branch: `docs/pages-landing`
  - [ ] Create `docs/index.html` on `main`
  - [ ] Include links to ontology overview, technical overview, codebase overview
  - [ ] Include links to latest TTL/OWL artifacts
  - [ ] Deployed at https://mentalhealthmission.github.io/MHM-ontology/

- [ ] A2: Publish latest artifacts (Issue #____) — Branch: `docs/publish-latest`
  - [ ] Convert TTL: `robot convert --input mhm_ontology.owl --format ttl --output docs/latest/odim-mh.ttl`
  - [ ] Copy OWL: `cp mhm_ontology.owl docs/latest/odim-mh.owl`
  - [ ] `docs/latest/odim-mh.ttl` accessible on Pages
  - [ ] `docs/latest/odim-mh.owl` accessible on Pages

- [ ] A3: JSON‑LD context (optional) (Issue #____) — Branch: `docs/jsonld-context`
  - [ ] Add `docs/contexts/odim-mh.jsonld`
  - [ ] Link from landing page

- [ ] A4: Versioned snapshots on releases (Issue #____) — Branch: `docs/releases-setup`
  - [ ] Create `docs/releases/vX.Y.Z/odim-mh.ttl|owl` during a tagged release
  - [ ] Verify URLs serve from Pages

- [ ] A5: CI to publish latest (recommended) (Issue #____) — Branch: `chore/ci-publish-latest`
  - [ ] Add GitHub Actions workflow to build TTL and update `docs/latest`
  - [ ] Ensure job runs on push to `main`
  - [ ] Protect `main` to require green checks (see Part B)

- [ ] A6: Draft w3id redirects (no submission yet) (Issue #____) — Branch: `docs/w3id-draft`
  - [ ] Draft `w3id/odim-mh/.htaccess` with content negotiation to Pages URLs
  - [ ] Draft `w3id/odim-mh/README.md` with maintainers and targets
  - [ ] Capture drafts in repo (not committed) or gists for review

- [ ] A7: Ontology visualizations (Issue #21) — Branch: `docs/visualizations-setup`
  - [ ] Unify scripts: keep Python SPARQL generators; remove duplicates; decide on `owl2dot.py`
  - [ ] Standardize outputs: write canonical SVGs (unsuffixed) and avoid committing multi-engine variants
  - [ ] Update docs: `docs/visualizations/README.md`, `tooling/README.md`; link visuals from `docs/ontology-overview.md`
  - [ ] Optional CI: title-lint for PRs and a check that visuals are up to date

- [ ] A7: Ontology visualization with Graphviz (Issue #15) — Branch: `feature/ontology-visualization`
    - [x] Add Graphviz visualization tool to Docker image
  - [ ] Create scripts to convert OWL to DOT format 
  - [ ] Add visualization commands to `tooling/run_ontology_tools.sh`
  - [ ] Generate SVG diagrams in `docs/visualizations/`
  - [ ] Update landing page to include links to visualizations

---

Part B — GitHub Setup and Protections

- [ ] B1: GitHub CLI access (agent‑side) (Issue #____) — Branch: `chore/gh-auth-docs`
  - [ ] `gh auth login` (SSH)
  - [ ] Add SSH key if needed; `gh auth status` OK
  - [ ] `gh repo view` works

- [x] B2: Branch protection: require PRs to main (Issue #11) — Branch: `chore/branch-protection`
  - [x] Add rule for `main`: require PRs, status checks, and reviews
  - [x] Restrict direct pushes (optional)

- [x] B3: CI validation checks (Issue #7) — Branch: `chore/ci-validators`
  - [x] Add `.github/workflows/ci.yml`
  - [x] Jobs: check-syntax, profile-DL, validate-units, validate-sosa, validate-skos, validate-prov
  - [x] CI runs on PR and `main`

- [ ] B4: PR hygiene (Issue #____) — Branch: `chore/pr-template`
  - [ ] Add `.github/PULL_REQUEST_TEMPLATE.md` with checklist
  - [ ] Template renders on new PRs

- [ ] B5: Code owners (optional) (Issue #____) — Branch: `chore/codeowners`
  - [ ] Add `.github/CODEOWNERS` (e.g., `* @james-c`)
  - [ ] Branch protection set to require CODEOWNERS review (optional)

- [x] B6: Labels setup (Issue #8) — Branch: `chore/labels`
  - [x] Add `.github/labels.json` with desired labels (e.g., type/scope/status)
  - [x] Add `.github/workflows/labels.yml` to sync labels (or document manual process)
  - [x] Run sync or apply labels manually once; verify presence in repo

---

Part C — Namespace Migration Prep (Option C, next phase)

- [ ] C1: Decide canonical base IRI (Issue #____) — Branch: `docs/namespace-decision`
  - [ ] Choose `https://w3id.org/odim-mh#` (or alternative) and record decision

- [ ] C2: Prefix policy (Issue #____) — Branch: `docs/prefix-policy`
  - [ ] Ensure all TTL/RQ define `PREFIX odim: <https://w3id.org/odim-mh#>` post‑migration
  - [ ] Remove inline IRIs in examples/queries

- [ ] C3: Bridging and deprecation (Issue #____) — Branch: `feature/iri-bridging`
  - [ ] Add `owl:equivalentClass/Property` between old and new IRIs
  - [ ] Mark old IRIs `owl:deprecated true`

- [ ] C4: Catalog and docs (Issue #____) — Branch: `docs/migration-notes`
  - [ ] Update `catalog-v001.xml`
  - [ ] Add migration notes to README and docs

---

Assignment format (per task)
- Issue title: `type(scope): subject` (e.g., `docs(pages): add index.html`)
- Acceptance:
  - Preconditions
  - Steps
  - Expected outputs/URLs
  - Validator runs (if applicable)
- Branch: `docs/<topic>` or `chore/<topic>`

---

Working Branches Log (local coordination)
- Note: set “owner” to the GitHub account the agent is acting on behalf of (the human maintainer/user), not the agent name.
- [ ] branch: `docs/pages-landing` → PR #___ (open) — owner: @james-c — Task: A1
- [x] branch: `chore/ci-validators` → PR #9 (merged) — owner: @james-c — Task: B3
- [x] branch: `chore/labels` → PR #10 (merged) — owner: @james-c — Task: B6
- [x] branch: `chore/branch-protection-workflow` → PR #12 (merged) — owner: @james-c — Task: B2
- [x] branch: `feature/odim-branding-phase-b` → PR #___ (merged) — owner: @james-c — Task: branding Option B (remote/local deleted)
