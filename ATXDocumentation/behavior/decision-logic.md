> ⚠️ **Early Access**: Behavior documentation is in early access. Please review critically.

# Decision Logic

## Decision Points

### 1. Device List Validation
**Location**: `lambda_handler()`, line ~292
- **Condition**: `event.get("devices", [])` is empty
- **True path**: Return error response `{"status": "error", "message": "No devices specified"}`
- **False path**: Proceed with polling

### 2. Connection Retry Decision
**Location**: `poll_device()`, line ~113
- **Condition**: `client.connect()` returns False
- **True path**: Raise `ConnectionError`, caught by outer try/except, retry (up to 3 attempts)
- **False path**: Proceed with register reading

### 3. Register Read Validity
**Location**: `read_input_32()`, `read_holding_32()`, `read_holding_16()`
- **Condition**: Response is not None, not error, has registers
- **True path**: Parse and return value
- **False path**: Return None

### 4. Safe Read Retry
**Location**: `safe_read()`, line ~40
- **Condition**: Read function returns None
- **True path**: Sleep 100ms, retry (up to `MAX_REGISTER_RETRIES` times)
- **False path**: Return value immediately

### 5. Power Factor Calculation Guard
**Location**: `poll_device()`, line ~217
- **Condition**: `P > 100` (active power above 100W)
- **True path**: Calculate `pf_uncorrected_calc` and `pf_corrected_calc`
- **False path**: Set both to `None`

### 6. Capacitor Bank Contribution
**Location**: `poll_device()`, line ~205
- **Condition**: `data.get(f"cap_{phase}", 0) == 0` for each phase
- **True path**: Include that phase's kVAr steps in `Q_cap_total`
- **False path**: Exclude (capacitor bank not active on that phase)

### 7. Financial Savings Calculation Guard
**Location**: `poll_device()`, line ~243
- **Condition**: `pf_improvement > 0` AND `P > 0`
- **True path**: Calculate monthly cost avoided and annualized savings
- **False path**: Set savings to 0.0

### 8. Poll Result Handling
**Location**: `lambda_handler()`, line ~304
- **Condition**: `poll_device()` returns data (not None)
- **True path**: Call `ingest_to_s3()`, record success
- **False path**: Record failure

## Cross-References
- [Behavior: Business Logic](business-logic.md)
- [Behavior: Error Handling](error-handling.md)
