# Issue tracker: GitHub

Issues and planned work live in
[GitHub Issues](https://github.com/George930502/curated-codex-skills/issues).
Use the `gh` CLI for automation and infer the repository from `origin`.

- Create: `gh issue create`
- Read: `gh issue view <number> --comments`
- List: `gh issue list --state open`
- Comment: `gh issue comment <number> --body "..."`
- Label: `gh issue edit <number> --add-label "..."`
- Close: `gh issue close <number> --comment "..."`

## Pull requests as a triage surface

**PRs as a request surface: no.** External pull requests are contributions, not
feature requests. A bare `#42` can identify either an issue or pull request;
resolve it with `gh pr view 42` and then `gh issue view 42`.

When a skill says to publish to the issue tracker, create a GitHub issue. When
it says to fetch a ticket, read the issue and its comments.
