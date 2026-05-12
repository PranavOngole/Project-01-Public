# CR-01 External Code Review

**Date:** 2026-05-12
**Reference:** CR-01
**Reviewer:** External
**Audience:** Management / Product / Engineering Leads
**Verdict at time of review:** BLOCK until remediation complete
**Status as of publication:** **All findings remediated.** See release notes [`RELEASES/v0.1.2.md`](../RELEASES/v0.1.2.md).

---

## About this document

This is the report of an external code review of Project-01 conducted on 2026-05-12 under the reference CR-01. The review was commissioned by the platform team as part of the standing audit cadence.

The report is preserved here in its original analytical structure (verdict, findings, severity ratings, remediation plan) with implementation-specific details that are not load-bearing for the public record replaced by descriptive labels. The findings, methodology, and verdict are unchanged.

Every finding listed below has been remediated in production. The release that closes them is [v0.1.2](../RELEASES/v0.1.2.md).

---

## 1. Executive Summary

The shipped batch contained useful defensive work, but it should not be treated as production-safe yet.

The two most important issues are:

1. The public web app is pinned to an outdated framework version with known security advisories.
2. The research pipeline prompt says it produces current, source-grounded research, but the runtime still asks the model to use training knowledge.

The second issue is the larger business risk for an investment research platform. It means stale or fabricated market facts can enter the workflow while appearing to satisfy the new safety prompt.

Good work observed:

- Broker integration is pinned to paper trading rather than live trading.
- Warehouse write diagnostics are much clearer than before.
- The bot now attempts to label fallback research as low-confidence instead of silently leaving gaps.
- Several stale-data gates were added to catch known earnings, EPS, gross-margin, and one-off-event failure modes.

However, these controls are incomplete, the release is too large to review safely as one unit, and there are no visible project tests for the highest-risk paths.

## 2. Manager-Level Risk Rating

| Risk Area | Rating | Why It Matters |
|---|---:|---|
| Security | High | The web framework version fails dependency audit with critical advisories. |
| Investment data integrity | High | The research stage can still rely on training knowledge despite prompt language requiring sourced current facts. |
| Operational dashboard accuracy | Medium | The operations cockpit can show "ACTIVE" / "ALL SYSTEMS NOMINAL" while a data feed is unavailable. |
| Release process | High | The shipped batch mixes web, bot, prompts, data pipelines, dependencies, and docs in one large diff. |
| Test confidence | Low | No committed tests were found for the new live-data, warehouse, shell-gate, or prompt-contract paths. |

## 3. Verification Performed

Before finalizing this report, each finding was re-verified against actual files and command output:

- Re-ran the production dependency audit.
- Re-read the research-stage runtime around the API call and user message construction.
- Re-read the research-stage system prompt around fiscal-period, numerical-bounds, and anti-fabrication requirements.
- Re-read the conviction-stage runtime around model output handling and warehouse-write JSON parsing.
- Re-read the broker adapter and warehouse adapter error-handling paths.
- Re-read cockpit status rendering and positions-error rendering.
- Confirmed no project test files existed in either the web app or the bot codebase outside vendor directories.
- Confirmed the production build succeeded but with a short-revalidation entry on the cockpit page.

No findings were retracted. One finding was clarified: the framework dependency issue is a confirmed dependency-audit failure. Some individual advisories may have platform-specific mitigation at the hosting layer, but the dependency gate still fails and should be fixed.

## 4. Limitations of This Review

The following review inputs were unavailable at the time of audit:

- Pull request descriptions and linked tickets.
- Continuous integration status.
- Coverage report.
- Prior review state and prior reviewer comments.
- External audit logging.

This report is therefore based on local git history, local source files, and local verification commands. Recommendations were calibrated against this scope.

## 5. Confirmed Findings

### Finding 1: Outdated Web Framework Dependency With Security Advisories

**Severity:** BLOCKER
**Area:** Security / Dependency management
**Scope:** Web app dependency manifest and lockfile

**Evidence:**

- The dependency manifest pins the web framework to a version below the audited patched range.
- Production dependency audit reports:
  - 1 critical vulnerability group on the framework
  - 1 moderate vulnerability on a transitive package
  - Audit fix available at the next patch release

**Why this matters:**

The web app is public-facing. Known framework vulnerabilities can create security, denial-of-service, or platform compliance risks. Even where the hosting platform may partially mitigate a specific advisory, dependency scanning will continue to flag this release as unsafe.

**Recommendation:** Upgrade the framework to at least the audited patched version, regenerate the lockfile, rerun the dependency audit, and make audit pass in CI before deploy.

### Finding 2: Research-Stage Prompt and Runtime Contradict Each Other

**Severity:** BLOCKER
**Area:** Investment data integrity / Prompt regression
**Scope:** Research-stage runtime and research-stage system prompt

**Evidence:**

The research-stage system prompt now says:

- Do not produce numerical claims without a source checked in the session.
- Emit `null` rather than guessing from training memory.
- Verify current earnings periods and source date anchors.

But the runtime still sends the model this instruction:

> Use your training knowledge.

It also calls a plain completion endpoint without a search or source-grounding tool.

**Why this matters:**

This is the exact failure mode the shipped hardening is meant to prevent. The platform can still generate research packets from stale model memory while the prompt gives management the impression that research is source-grounded.

**Business impact:**

- Wrong earnings numbers can enter the system.
- Old fiscal periods can be mislabeled as current.
- The conviction stage may score an investment thesis based on stale or fabricated context.
- The dashboard may show "live" conviction data built on weak source assumptions.

**Recommendation:** Replace the research-stage runtime with a genuinely source-grounded workflow. If the system cannot access sources, it should emit a `RESEARCH UNAVAILABLE` status rather than a guessed packet.

### Finding 3: Conviction-Stage Output Is Not Strictly Validated Before Success

**Severity:** MAJOR
**Area:** Contracts / Reliability
**Scope:** Conviction-stage runtime

**Evidence:**

The runtime extracts model text and prints it to standard output. Warehouse-write code later attempts to parse the JSON and skips the insert if invalid, but the runtime does not fail the command before printing invalid output.

**Why this matters:**

Downstream scripts treat the conviction stage as a JSON-producing contract. If malformed model output reaches standard output with a successful process exit, trade gating can break unpredictably.

**Recommendation:** Parse the final output as JSON before printing it. If parsing fails, print a clear error to standard error and exit non-zero.

### Finding 4: Public API Routes Can Return Raw Upstream Error Details

**Severity:** MAJOR
**Area:** Security hygiene
**Scope:** Public broker and warehouse adapters

**Evidence:**

The broker and warehouse helpers return raw upstream exception messages through public API responses.

**Why this matters:**

Public unauthenticated endpoints should not reveal internal infrastructure details, cloud resource names, credential configuration states, or upstream exception messages.

**Recommendation:** Keep full errors in server logs. Return generic client-safe error envelopes such as:

- `Market data temporarily unavailable`
- `Account data temporarily unavailable`
- `Conviction data temporarily unavailable`

### Finding 5: Cockpit Can Show Green System Health During Data Outage

**Severity:** MAJOR
**Area:** Operational correctness
**Scope:** Operations cockpit page

**Evidence:**

The positions panel can show "Alpaca unreachable," but the top system status still renders:

- `ACTIVE`
- `ALL SYSTEMS NOMINAL`

**Why this matters:**

The cockpit page is an operations surface. It should not reassure the user when its own broker or data feed is unavailable.

**Recommendation:** Derive the overall status from live data health:

- If account and positions load: `ACTIVE`
- If one feed fails: `DEGRADED`
- If both fail: `DATA UNAVAILABLE`

### Finding 6: No Visible Tests for Critical Paths

**Severity:** MAJOR
**Area:** Test coverage
**Scope:** Web routes, data adapters, bot scripts, prompt output contracts

**Evidence:**

No committed project tests were found across the web app or the bot codebase. The only test files found were inside vendor directories, which do not count as project tests.

**Why this matters:**

The release changes money-adjacent and data-integrity paths:

- Broker account state
- Broker positions
- Market prices
- Conviction-stage rows
- Research-stage rows
- Warehouse writes
- Model output contracts

**Recommendation:** Add a small but focused regression suite before trusting this pipeline. Minimum tests:

- Broker credentials missing.
- Broker upstream unavailable.
- Warehouse credentials missing.
- Warehouse query failure.
- Conviction-stage malformed JSON.
- Research-stage no-source fallback.
- Internal fallback marker blocked by the conviction gate.
- Cockpit degraded status when data fails.

### Finding 7: Release Batch Is Too Large and Mixed

**Severity:** MAJOR
**Area:** Process / Reviewability
**Scope:** 40 files, 3,684 additions, 1,826 deletions, multiple domains

**Why this matters:**

The shipped batch mixes web app live-data routes, broker integration, warehouse writes, shell script changes, prompt hardening, data methodology docs, dependency changes, and large docs movements. This makes it hard for any reviewer to catch defects. Large mixed diffs create review fatigue and hide contract breaks.

**Recommendation:** Split future changes into smaller review units, one domain per batch.

### Finding 8: Standardize Code Style, Comments, and Delivery Methodology

**Severity:** PROCESS RECOMMENDATION
**Area:** Human handoff / maintainability

**Observation:**

The repo currently mixes styles and levels of explanation. Some code has detailed incident comments. Some code has no tests or no clear handoff notes. Some docs describe intended behavior that the code does not yet implement.

**Why this matters for a non-technical manager:**

When a human engineer needs to pick up the work later, inconsistent style increases ramp time. The manager has to spend more money and time just getting someone oriented.

**Recommendation:** Create and enforce a small "Project-01 Engineering Standard" covering:

1. One task, one purpose.
2. Same file header format for scripts.
3. Same error-handling pattern across routes and scripts.
4. Same logging vocabulary: `OK`, `SKIPPED`, `FAILED`, `BLOCKED`, `DEGRADED`.
5. Same comment style: comments explain why, not what.
6. Same test expectation: every new behavior gets at least one regression test.
7. Same PR handoff block: what changed, why, how to verify, known limitations, rollback plan.
8. Same prompt-change checklist: behavior, schema, affected downstream agents, QA regression status.
9. Same code-review format: blockers, majors, minors, tests run, residual risk.

This recommendation is not cosmetic. It is a cost-control and continuity-control measure.

### Finding 9: Minor Prompt Text Mismatch

**Severity:** MINOR
**Area:** Prompt accuracy
**Scope:** Research-stage system prompt

**Evidence:** The prompt states a per-share value rejection threshold that is broader than the per-ticker rejection thresholds the runtime actually applies.

**Recommendation:** Update the prompt text to match the actual per-ticker gates.

### Finding 10: Trivial Formatting Issue

**Severity:** NIT
**Area:** Formatting
**Scope:** Internal design document

**Evidence:** Trailing whitespace on two lines.

**Recommendation:** Trim trailing whitespace. Not a merge blocker on its own.

## 6. Recommended Remediation Plan

### Immediate: 0-1 day

1. Upgrade the web framework and make the dependency audit pass.
2. Remove the training-knowledge instruction from the research-stage runtime.
3. Decide the real research-stage sourcing path: use a web-grounded API or tool, or return `RESEARCH UNAVAILABLE`.
4. Make the conviction-stage runtime fail on invalid JSON.
5. Remove raw error details from public API responses.

### Short term: 2-5 days

1. Add regression tests for web routes and shell gates.
2. Make the cockpit status reflect actual data health.
3. Add CI checks: dependency audit, type check, build, shell syntax, regression test suite.
4. Add prompt-contract tests for the research and conviction stages.

### Medium term: 1-2 weeks

1. Create the engineering standards document.
2. Create a PR template with the standard handoff block.
3. Split future work into review-sized PRs.
4. Create a dashboard or checklist showing which hard gates are passing.

## 7. Go / No-Go Recommendation

**Recommendation at time of review:** NO-GO for production trust until the two blockers are resolved.

The platform can continue as a prototype or paper-trading sandbox if clearly labeled as such, but at the time of this review the current state should not be represented as production-grade or source-grounded investment intelligence.

**Approval criteria:**

1. Dependency audit passes.
2. The research stage no longer generates current research from training memory.
3. Conviction-stage output is schema-validated before success.
4. Public API errors are sanitized.
5. Cockpit health reflects real feed status.
6. Tests cover the critical regression paths.

## 8. Bottom Line

This is not a failure of direction. The architecture is moving toward the right controls: provenance, fallback labeling, paper-only broker exposure, and stale-data gates.

The gap is execution discipline. The code must match the prompts. The tests must match the risk. The release process must be small enough for humans to review. And the style and methodology must be consistent enough that the next engineer can pick up the system without needing archaeology.

That is fixable. It should be fixed before this release is treated as safe.

---

## Resolution

**All six approval criteria were met within the audit response window.** The remediation work shipped under release [v0.1.2](../RELEASES/v0.1.2.md) on the same date as this review (2026-05-12) under a new team operating standard adopted in response to Finding 8: contracts at the boundary, refuse-to-ship beats fake-confidence, spec equals runtime equals docs, tests as preconditions, small reviewable batches.

| Approval criterion | Status |
|---|---|
| Dependency audit passes | Clean across critical, high, and moderate runtime advisories |
| Research stage no longer uses training memory | Source-grounded runtime with refusal semantics; permanent regression guard test |
| Conviction-stage output schema-validated before success | Boundary validator rejects malformed output; downstream gates fail closed |
| Public API errors sanitized | Single public error envelope with request-correlated identifier; no vendor detail leaked |
| Cockpit health reflects real feed status | Three explicit states derived from live feed health |
| Tests cover critical regression paths | Full regression suite covering every audit-named path; suite gates every change |

The production-trust verdict moved from NO-GO to GO with the release of v0.1.2.
