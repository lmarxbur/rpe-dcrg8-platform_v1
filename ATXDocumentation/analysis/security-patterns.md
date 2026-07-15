# Security Patterns

## Authentication and Authorization
- **Lambda execution role**: IAM-based (not defined in code, managed externally)
- **S3 access**: Via Lambda execution role, no explicit credential handling in code
- **Modbus/TCP**: No authentication (protocol does not support it natively)

## Data Protection
- **S3 encryption**: Relies on bucket-level default encryption (not explicitly set in `put_object`)
- **Data in transit to S3**: Encrypted via HTTPS (boto3 default)
- **Modbus communication**: Unencrypted (inherent protocol limitation)

## Input Validation
- **Device list**: Only checks for non-empty array; no validation of IP format, port range, or device name
- **Register responses**: Validates `not rr.isError()` and `rr.registers` presence
- **No injection risk**: No user-supplied strings are used in queries or commands

## Secrets Management
- **No hardcoded secrets**: Configuration uses environment variables
- **No API keys or tokens in source**

## Security Concerns

| Finding | Severity | Detail |
|---------|----------|--------|
| No Modbus authentication | Medium | Protocol limitation; devices should be on isolated network |
| No input validation on device IP/port | Low | Event source is controlled (EventBridge) |
| No S3 encryption explicitly set | Low | Should rely on bucket policy, but not enforced in code |
| Unencrypted Modbus/TCP traffic | Medium | Industrial protocol constraint; mitigate with network segmentation |

## Cross-References
- [Architecture: Patterns](../architecture/patterns.md)
- [Technical Debt: Maintenance Burden](../technical-debt/maintenance-burden.md)
