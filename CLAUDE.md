# CLAUDE.md

How Claude Code works in this repository. Keep this file short: code
conventions belong in `STYLE.md`, and requirements belong in `SPEC.md`.

## Sources of authority

- `SPEC.md` defines what to build: scope, requirements (IDs such as
  `REQ-001-NSE`), and acceptance criteria.
- `STYLE.md` defines how code, tests, configuration, and documentation are written.
- This file defines how work is planned, reviewed, verified, and handed off.
- The user's current instructions take precedence over all three.
- When sources conflict or a requirement is ambiguous, stop and ask. Never
  resolve a conflict silently.
- Never invent requirements. If `SPEC.md` is missing or does not cover the
  task, work only from explicit user instructions and say so.

## Starting a session

1. Read `HANDOFF.md` if it exists, and check it against the current code. It may be stale.
2. Run `git status` and `git log --oneline -10`. Preserve uncommitted work you did not make.
3. Read the parts of `SPEC.md` that apply to the task.
4. Read `STYLE.md` in full before writing or changing code, tests, or configuration.

## Review gates

The user reviews all work on GitHub. Each gate ends with a stop.

1. **Design.** Propose the change as a GitHub issue or draft PR: affected files,
   public interfaces, planned tests, requirement IDs, and open decisions. Write
   no implementation code. Stop and wait for approval.
2. **Implement.** After approval, make only the approved change, on a new branch
   (see Branches).
3. **Review.** Open one small PR, about 100 to 300 reviewable lines, not counting
   lock files. Stop and wait for review.

Keep only one PR open at a time. Do not start the next piece of work until the
current PR is merged, unless the user says otherwise.

## Branches

- Start each PR on a new branch created from the latest `main`. Never commit
  directly to `main`.
- Name the branch `claude/` followed by a short, lowercase, hyphenated
  description of the change, for example `claude/add-style-guide`.
- After the PR merges, update local `main` and delete the local branch. Never
  reuse a merged branch.

## Pull requests

Every PR description includes:

- **Summary:** what changed and why.
- **Requirements:** the full requirement IDs covered, or "none" with a reason.
- **Decisions needing review:** every choice not dictated by `SPEC.md` or `STYLE.md`.
- **Verification:** each check, its command, and its status.

## Reporting verification

Give every check exactly one status: passed, failed, skipped, not available, or
not run. Never report a result for a check that was not run, and never call work
done or working without evidence.

## Handling review comments

- Make each requested change, then reply on its thread with the commit hash.
- Leave threads for the reviewer to resolve. Do not resolve them yourself.
- For a large request, such as a redesign or a public interface change, reply
  with a proposal and wait.
- If you disagree with a request, explain why on the thread and let the user decide.

## Commits

- Keep each commit to one logical change.
- Write messages a person can understand without reading the diff: a summary
  line of 72 characters or fewer in the imperative mood, a blank line, then a
  body explaining why the change was made and what a reviewer should know.
- Run the project's checks (see `STYLE.md`) before committing. All must pass.

## Ask first

Get the user's approval before you:

- add, remove, or upgrade a dependency;
- change tooling, CI, or `.claude/settings.json`;
- change the cloud environment or its network access;
- take any action outside the repository that the current task does not already call for.

## HANDOFF.md

`HANDOFF.md` is a local, untracked file (ignored in `.gitignore`) that records
where work stands relative to the plan. Update it at the end of every work
session. Never commit it. Use these headings:

```markdown
# Handoff

## Objective
## Current state
## Next action
## Blockers
## Open questions
```

Write it for a reader with no chat history: name files, branches, PRs, and
issues explicitly. Never include secrets or personal data.
