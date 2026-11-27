# SPEC.md

**Status:** alpha

<!--
How to fill in this file

SPEC.md defines what this project builds. STYLE.md defines how code is
written, and CLAUDE.md defines how Claude Code works. Keep those topics out
of this file.

This file ships with an example: the requirements for example_package. A new
project replaces the sections below with its own content.

1. Mark anything not yet written with a placeholder: TODO in capitals,
   followed by a colon. Claude treats this file as unfilled while any
   placeholder remains outside this comment, and then works only from the
   user's explicit instructions.
2. Change the Status line above as the spec matures:
   - alpha (default): requirements are being drafted and may change freely.
   - beta: all planned requirements are written; they may still change
     after review.
   - candidate: requirements are frozen pending final review; only
     corrections.
   - release: requirements are agreed; changes go through a reviewed PR.
   The status describes how settled the spec is. Implementation may start
   at any status once its design is approved.
3. Give each requirement an ID of the form REQ-###-TAG: the next unused
   three-digit number, then a short uppercase tag naming the subject, such
   as REQ-001-NSE. Tags use letters, digits, and hyphens. Once assigned,
   the full ID never changes, and the number is never reused. Always cite
   the full ID, not just the number. To drop a requirement, add
   "(withdrawn)" to its heading and say why, so references in PRs and
   commits stay valid.
   Track progress on requirements in HANDOFF.md, not in this file.
4. When a requirement adds or changes a public function or class, record its
   interface: module, signature, inputs with units, return value, and errors.
5. Write acceptance criteria that a test or a reviewer can check: a specific
   input, action, or condition and the expected result.
6. Move each open question into a requirement, constraint, or non-goal once
   it is answered.
-->

## Purpose

`example_package` demonstrates the workflow this template sets up, from a
written requirement to tested code. It provides one small function that
scores simulated streamflow against observed streamflow. Its audience is
developers adopting the template, who can use it as a reference for how a
requirement, its code, and its tests fit together.

## Scope

### In scope

- Computing the Nash-Sutcliffe efficiency for one simulated series and one
  observed series.
- Validating inputs and reporting invalid ones with clear errors.

### Non-goals

- Other evaluation metrics, such as the Kling-Gupta efficiency.
- Batched or multi-dimensional inputs, such as many series at once.
- Handling missing values. Inputs with `nan` are rejected, not skipped.
- Reading or writing data files.

## Requirements

Each requirement has an ID, a short title, a description, an interface when it
adds public code, and acceptance criteria.

### REQ-001-NSE: Compute the Nash-Sutcliffe efficiency

- **Description:** Provide a function that scores simulated streamflow
  against observed streamflow using the Nash-Sutcliffe efficiency (NSE).
- **Interface:**
  - Module: `example_package.metrics`
  - Signature:
    `nash_sutcliffe_efficiency(simulated: ArrayLike, observed: ArrayLike) -> float`
  - Inputs: `simulated` and `observed`, array-like series of streamflow in
    the same unit, of any flow unit.
  - Returns: the NSE, a dimensionless float from negative infinity to 1.
  - Raises `ValueError` if either input is not one-dimensional, the lengths
    differ, the inputs are empty, any value is not finite, or the
    observations are constant.
- **Acceptance criteria:**
  - A perfect simulation returns 1.0.
  - A simulation equal to the observed mean returns 0.0.
  - Constant observations raise `ValueError`.
  - Each invalid input listed under Raises produces `ValueError`.

## Constraints

- Python 3.13 or newer.
- NumPy is the only runtime dependency.
- Development environments are supported on `linux-64` only, for now.
- Licensed under the Apache License 2.0.

## Open design questions

- None at this time.
