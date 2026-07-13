# Security policy

## Supported versions

Security fixes are provided for the latest tagged release and current `main`.
Preview releases may receive breaking fixes when preserving behavior would keep
an unsafe workflow.

## Reporting

Do not open a public issue for a vulnerability. Use the repository's
[private vulnerability report](https://github.com/George930502/curated-codex-skills/security/advisories/new)
with reproduction steps, affected files or skills, impact, and any suggested
mitigation. The maintainer will acknowledge a report as capacity allows,
coordinate disclosure, and credit reporters who want attribution.

## Security boundaries

The repository distributes instructions and local installers; it does not hold
credentials or operate a service. Relevant reports include prompt-driven
unauthorized actions, approval or destination-verification bypasses, installer
path traversal, secret exposure, and malicious provenance. General Codex
product vulnerabilities should be reported to OpenAI through its official
security channel.
