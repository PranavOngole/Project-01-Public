# Changelog

Versioned record of platform releases.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Detailed release notes for each version live under [`RELEASES/`](./RELEASES/).

---

## [v0.1.4] - 2026-05-14

### Highlights

Earnings-quality letter-grade band shipped. Cross-name calibration evidence broadened from one to five tickers. Eight-name historical-fraud forensic fixture cleared its gate eight of eight. Source-of-truth moved from local artifacts to the warehouse with a full bi-temporal contract.

Full notes: [`RELEASES/v0.1.4.md`](./RELEASES/v0.1.4.md).

### Added

- Composite earnings-quality letter-grade band in the UI, with click-to-expand per-component drill-down.
- Eight-name historical-fixture test for the earnings-quality composite. Five fraud-archetype filings classified as quality-stressed, three established-conservative filings classified as clean.
- Five-ticker calibration cohort for the distributional intrinsic-value band.
- Warehouse-first storage for backtest probe results and historical filing fixtures with a full bi-temporal contract.
- Named failure-reason diagnostic on calibration-gate failures.

### Changed

- Backtest probe results now persist to the warehouse rather than local JSON artifacts. Local artifacts remain as release records only.

---

## [v0.1.3] - 2026-05-14

### Highlights

Distributional intrinsic-value band shipped. Single-point estimate replaced with a quantile band that exposes uncertainty rather than papering over it. Conviction sizing now follows a four-tier ladder. Capital-exposure discipline operates in two independent layers (recommendation and trade-execution).

Full notes: [`RELEASES/v0.1.3.md`](./RELEASES/v0.1.3.md).

### Added

- P5-P95 intrinsic-value band in the UI, with labelled dominant-uncertainty driver.
- Trade-execution-layer margin-of-safety gate at fifteen percent below the band median, independent of the recommendation-layer threshold.
- Four-tier conviction ladder for position sizing (zero size above the band median, one-third in the upper tail, two-thirds in the lower tail, full size below the lower extreme).
- Empirical spread-calibration gate for the band methodology.

### Changed

- Release gate for the intrinsic-value band redefined after the originally specified gate proved structurally unreachable for names trading materially away from DCF fair value. The replacement measures band-width calibration against the asset's empirical short-horizon return spread.

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
[v0.1.3]: https://github.com/PranavOngole/Project-01-Public/releases/tag/v0.1.3
[v0.1.4]: https://github.com/PranavOngole/Project-01-Public/releases/tag/v0.1.4
