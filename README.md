# claude-metrics

A template for Python projects developed with [Claude Code](https://code.claude.com/docs).
It sets up a review-gated workflow: Claude proposes each change, the developer
reviews it on GitHub, and nothing moves forward without approval.

> **Status:** work in progress. An example package (`pyproject.toml`, pixi
> environment, source module, and tests) is still to come. Once it is in place,
> this repository will be marked as a GitHub template, and this README will be
> updated with setup and usage commands.

## What's included

| File | Purpose |
|---|---|
| `CLAUDE.md` | How Claude works: the general development workflow, review gates, Git branching, pull request contents, and what needs approval. Claude Code loads it in every session. |
| `STYLE.md` | Style, standards, and coding conventions for Python code, tests, tooling, and documentation. |
| `SPEC.md` | A template for the project's requirements, with IDs such as `REQ-001-NSE` and checkable acceptance criteria. |
| `.claude/settings.json` | Claude Code permission rules, and a hook that loads `HANDOFF.md` at the start of each session. |
| `.gitignore` | Standard Python ignores, plus the local `HANDOFF.md`. |

## How the workflow works

1. **Specify.** Fill in `SPEC.md`. Until its placeholders are replaced, Claude
   works only from your explicit instructions.
2. **Design.** Claude proposes each change as a GitHub issue or draft pull
   request, then stops for your approval.
3. **Implement.** Claude makes only the approved change, on a new branch named
   `claude/<short-description>`.
4. **Review.** Claude opens one small pull request at a time, lists the
   decisions you need to review, and reports every check as passed, failed,
   skipped, not available, or not run. You resolve review threads; Claude
   replies with the commit that addressed each one.

Between sessions, Claude keeps notes in `HANDOFF.md`, a local file that is
never committed. It records the current state, the next action, blockers, and
open questions.

## Permissions

`.claude/settings.json` lets Claude run read-only Git commands, commit, run
pixi tasks, and delete individual files or empty folders without prompting.
Claude asks before pushing or adding dependencies. Force pushes, recursive
deletes, `pip`, `uv`, and reading `.env` files are blocked. The rules match
command text, so they reduce mistakes rather than guarantee against them.

## Using this template

Until the example package is added, copy these files into a new repository by
hand:

1. Copy `CLAUDE.md`, `STYLE.md`, `SPEC.md`, `.claude/settings.json`, and
   `.gitignore`.
2. Fill in `SPEC.md` for your project and set its `Status` line to `draft`.
3. Adjust `STYLE.md` if your project uses different conventions.
4. Start a Claude Code session in the repository and describe the first change.

## License

Apache License 2.0. See `LICENSE`.
