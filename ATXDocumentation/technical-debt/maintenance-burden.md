# Maintenance Burden

## High-Maintenance Areas

### 1. Monolithic `poll_device()` Function
- **152 lines** with cyclomatic complexity of 12
- Combines connection management, register reading, calculations, and retry logic
- Any change to one concern risks affecting others
- Difficult to unit test individual calculation logic

### 2. Register Address Management
- Modbus register addresses are hardcoded as magic numbers throughout `poll_device()`
- Adding/removing registers requires modifying the function body
- No validation that addresses match DCRG8 documentation

### 3. No Automated Testing
- Zero test files in the repository
- Changes cannot be validated without manual testing against physical hardware
- Regression detection is entirely manual

### 4. No Infrastructure Definition
- No SAM template, CDK, CloudFormation, or Terraform
- Lambda configuration (timeout, memory, IAM role, environment variables) is not version-controlled
- EventBridge rule configuration is not in code

### 5. Logging via `print()`
- No structured logging
- No log levels (cannot filter warnings from errors)
- Difficult to set up CloudWatch Logs Insights queries
- No request correlation (Lambda request ID not included)

## Operational Risks

| Risk | Impact | Likelihood |
|------|--------|-----------|
| pymodbus breaking change on deploy | Lambda fails silently | Medium |
| Lambda timeout with many devices | Partial data collection | Medium |
| No alerting on poll failures | Undetected data gaps | High |

## Cross-References
- [Analysis: Complexity Analysis](../analysis/complexity-analysis.md)
- [Behavior: Error Handling](../behavior/error-handling.md)
- [Technical Debt: Remediation Plan](remediation-plan.md)
