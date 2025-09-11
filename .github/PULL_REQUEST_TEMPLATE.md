Title: type(scope): subject

Summary
- Briefly describe the changes and motivation
- Link the Issue: Closes #____

Checklist
- [ ] Syntax/profile pass (`tooling/run_ontology_tools.sh profile mhm_ontology.owl DL`)
- [ ] Validators pass: `validate-units` / `validate-sosa` / `validate-skos` / `validate-prov`
- [ ] Docs updated (README, `docs/*.md`), examples/queries adjusted if impacted
- [ ] Public plan updated in `plan.md` (if non‑agentic); agent notes updated in `AGENT-PLAN.md`
- [ ] Branch named per convention (`feature/…`, `fix/…`, `docs/…`, `chore/…`)

Post‑merge (maintainer or author)
- [ ] Confirm PR merged
- [ ] Delete remote branch: `git push origin --delete <branch>`
- [ ] Delete local branch: `git branch -d <branch>`

