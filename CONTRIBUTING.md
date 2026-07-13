# Contributing

Thank you for improving Curated Codex Skills. By participating, you agree to
the [Code of Conduct](CODE_OF_CONDUCT.md).

## Before opening a change

Use a GitHub issue for a defect, workflow proposal, or new skill. A new skill
must solve a repeatable Codex workflow, have a clear trigger and completion
criterion, fit the repository's licensing model, and be supportable with
deterministic checks. A large catalog is not a goal by itself.

For adapted work, pin the upstream repository and commit in `SOURCES.md`, retain
the applicable notice, and include a reproducible patch or equivalent audit
record. Never copy work whose license is unclear.

## Development flow

1. Branch from `main` and keep the change focused.
2. Update documentation, provenance, tests, and `CHANGELOG.md` with behavior.
3. Run:

   ```bash
   python3 scripts/validate.py --skills-dir skills
   python3 scripts/check_repository.py
   python3 -m unittest discover -s tests -v
   ```

4. Smoke-test `scripts/install.sh` or `scripts/install.ps1` with a temporary
   destination. Never point a test at your real `$HOME/.agents/skills`.
5. Open a pull request using the template and wait for required checks.

No live Codex credentials are needed for repository validation. Changes to
native-interaction workflows should also include a documented manual scenario;
CI cannot prove that a particular Codex client exposes a native tool.

## Pull requests

Explain the problem, observable behavior, validation evidence, compatibility
impact, and provenance impact. Maintainers may ask for a smaller patch when the
review surface is unnecessarily broad. Use squash merge unless preserving
separate commits has clear audit value.
