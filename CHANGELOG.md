# Changelog

Versioned record of platform releases.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Detailed release notes for each version live under [`RELEASES/`](./RELEASES/).

---

## [v0.1.2] - 2026-05-12

### Highlights

External code review (CR-01) response. All review findings closed. Production-trust verdict moved from NO-GO to GO. Dependency security posture clean (zero advisories) for the first time since the review was filed.

Full notes: [`RELEASES/v0.1.2.md`](./RELEASES/v0.1.2.md).

### Security

- Dependency advisories cleared across runtime and transitive packages. Audit at zero critical, zero high, zero moderate.

### Added

- Source-grounded research runtime with refusal semantics when source access is unavailable.
- Boundary validation on every agent output prior to any persisted write.
- Sanitized public API error surface with request-correlated identifiers.
- Real-time feed-health observability with explicit degraded states.
- Regression coverage on every named critical path.
- Repository conventions for machine-readable contracts and human-readable decision records.
- Engineering standards document and auto-applying pull-request template.

### Changed

- Seventeen small single-domain release batches versus prior monolithic pattern.

---

## [v0.1.1] - 2026-04-23

Pre-code self-review pass. Safety controls, kill switch, daily budget cap, drawdown circuit breaker, and real-time grounding for the research stage.

## [v0.1.0] - 2026-04-23

Initial trading platform release. Stateless runs, git-backed memory, hard rules enforced before any action.

[v0.1.2]: https://github.com/PranavOngole/Project-01-Public/releases/tag/v0.1.2
