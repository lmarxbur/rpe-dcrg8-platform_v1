# Outdated Components

## Runtime Version
| Component | Current | Status | Severity |
|-----------|---------|--------|----------|
| Python | Not specified in repo | Unknown — no `runtime` config or `.python-version` file | Medium |

**Note**: Without a `requirements.txt`, `pyproject.toml`, SAM template, or similar, the target Python runtime version cannot be determined from source alone. If deployed on Python 3.8 or 3.9 (both EOL for Lambda), this would be a **High** severity issue.

## Library Dependencies

| Library | Version in Use | Latest Stable | Status | Severity |
|---------|---------------|---------------|--------|----------|
| `pymodbus` | Not pinned | 3.7.x | Unknown — could be any version | Medium |
| `boto3` | Lambda-provided | Current | Managed by AWS | Low |

## Deprecated API Usage

| API | Location | Deprecation | Severity |
|-----|----------|-------------|----------|
| `datetime.utcnow()` | `ingest_to_s3()` | Deprecated in Python 3.12 (PEP 587) | Low |

**Recommended replacement**: `datetime.now(datetime.UTC)` (Python 3.11+) or `datetime.now(timezone.utc)` (Python 3.2+)

## Build Tools
No build tool or packaging configuration detected. Deployment mechanism is unknown.

## Cross-References
- [Analysis: Dependency Analysis](../analysis/dependency-analysis.md)
- [Technical Debt: Remediation Plan](remediation-plan.md)
