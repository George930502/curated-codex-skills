# Release procedure

The project uses Semantic Versioning. Before `v1.0.0`, minor versions may
change skill behavior or repository contracts; patch versions contain
compatible fixes and documentation corrections. Every release has an annotated
Git tag and GitHub release notes.

## Checklist

1. Confirm `VERSION` and `CHANGELOG.md` describe the intended version.
2. Run every command in `AGENTS.md` from a clean checkout.
3. Verify installer smoke tests use isolated destinations.
4. Push the candidate and require green Linux, macOS, and Windows CI.
5. Run fresh Standards and Spec reviews from the chosen fixed baseline; resolve
   every valid finding and repeat until both report `No findings.`
6. Confirm source locks, licenses, local links, repository identity, and remote
   settings.
7. Create an annotated `vX.Y.Z` tag at the verified `main` commit, push it, and
   create the GitHub release. Mark unstable releases as prereleases.
8. Verify the remote tag, release URL, default branch, visibility, and that the
   local HEAD equals `origin/main`.

Never move or replace a published tag. Correct a bad release with a new version.
