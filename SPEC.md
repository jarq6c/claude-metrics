# SPEC.md

**Status:** template

<!--
How to fill in this file

SPEC.md defines what this project builds. STYLE.md defines how code is
written, and CLAUDE.md defines how Claude Code works. Keep those topics out
of this file.

1. Replace every placeholder marked TODO (in capitals, followed by a colon)
   with real content. Claude treats this file as unfilled while any
   placeholder remains outside this comment, or while Status is template,
   and then works only from the user's explicit instructions.
2. Change the Status line above as the spec matures:
   - template: not filled in yet
   - draft: filled in, still under discussion
   - approved: agreed; changes go through a reviewed PR
3. Give each requirement an ID of the form REQ-###-TAG: the next unused
   three-digit number, then a short uppercase tag naming the subject, such
   as REQ-001-NSE. Tags use letters, digits, and hyphens. Once assigned,
   the full ID never changes, and the number is never reused. Always cite
   the full ID, not just the number. To drop a requirement, add
   "(withdrawn)" to its heading and say why, so references in PRs and
   commits stay valid.
   Track progress on requirements in HANDOFF.md, not in this file.
4. Write acceptance criteria that a test or a reviewer can check: a specific
   input, action, or condition and the expected result.
5. Move each open question into a requirement, constraint, or non-goal once
   it is answered.

Example requirement:

### REQ-001-NSE: Compute the Nash-Sutcliffe efficiency

- **Description:** Provide a function that scores simulated streamflow
  against observed streamflow using the Nash-Sutcliffe efficiency.
- **Acceptance criteria:**
  - A perfect simulation returns 1.0.
  - A simulation equal to the observed mean returns 0.0.
  - Constant observations raise ValueError.
-->

## Purpose

TODO: In two to four sentences, describe the problem this project solves and
who will use it.

## Scope

### In scope

- TODO: List the capabilities this project will provide.

### Non-goals

- TODO: List related capabilities this project will deliberately not provide.

## Requirements

Each requirement has an ID, a short title, a description, and acceptance criteria.

### REQ-001-TAG: TODO: Replace TAG with a short tag, and this text with a short title

- **Description:** TODO: What the project must do, in one or two sentences.
- **Acceptance criteria:**
  - TODO: A checkable condition and its expected result.

## Constraints

- TODO: List limits the design must respect, such as supported platforms,
  performance targets, data formats, licenses, or required dependencies.

## Open design questions

- TODO: List decisions that are still open. For each, note the options being
  considered and who decides.
