# Remediation Plan

## Priority 1: Medium Severity (Address First)

### 1.1 Add Dependency Management
- Create `requirements.txt` with pinned versions:
  ```
  pymodbus>=3.5,<4.0
  boto3>=1.28.0
  ```
- Consider adding `pyproject.toml` for modern Python packaging

### 1.2 Add Infrastructure-as-Code
- Create SAM template (`template.yaml`) or CDK stack defining:
  - Lambda function (runtime, handler, memory, timeout)
  - EventBridge rule (schedule expression)
  - S3 bucket
  - IAM execution role with least-privilege policy
  - Environment variables

### 1.3 Specify Python Runtime Version
- Pin runtime in SAM/CDK template (recommend Python 3.12+)
- Add `.python-version` file for local development

## Priority 2: Low Severity (Address When Convenient)

### 2.1 Replace `datetime.utcnow()`
- Replace with `datetime.now(timezone.utc)` for Python 3.12+ compatibility
- Import: `from datetime import timezone`

### 2.2 Refactor `poll_device()`
- Extract register reading into separate functions by group
- Extract PF calculation logic into a pure function
- Extract savings calculation into a pure function
- This enables unit testing of business logic without Modbus hardware

### 2.3 Add Structured Logging
- Replace `print()` with Python `logging` module
- Use JSON formatter for CloudWatch Logs Insights compatibility
- Include Lambda request ID via `context.aws_request_id`

### 2.4 Add Unit Tests
- Test PF calculation logic with known input/output pairs
- Test address translation (`get_query_addr`)
- Test 32-bit parsing functions
- Mock `ModbusTcpClient` for integration-style tests

### 2.5 Externalize Configuration
- Move S3 key prefix to environment variable
- Consider making register map configurable for different device models

### 2.6 Add CloudWatch Metrics
- Emit custom metrics for: devices polled, success/failure count, poll duration
- Set up CloudWatch Alarms for failure thresholds

## Cross-References
- [Technical Debt: Outdated Components](outdated-components.md)
- [Technical Debt: Maintenance Burden](maintenance-burden.md)
- [Migration: Validation Criteria](../migration/validation-criteria.md)
