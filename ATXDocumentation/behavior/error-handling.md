> ⚠️ **Early Access**: Behavior documentation is in early access. Please review critically.

# Error Handling

## Exception Handling Patterns

### 1. Modbus Register Read Errors
**Location**: `read_input_32()`, `read_holding_32()`, `read_holding_16()`
- **Exception**: `ModbusException`
- **Handling**: Caught silently, returns `None`
- **Impact**: Caller receives None, triggering retry via `safe_read()`

### 2. Connection and Polling Errors
**Location**: `poll_device()`, outer try/except
- **Exception**: Any `Exception`
- **Handling**: Logs error with device name, attempt number, and exception message; sleeps 1s; retries up to 3 times
- **Impact**: If all retries fail, returns `None` to caller

### 3. Connection Failure
**Location**: `poll_device()`, line ~118
- **Exception**: Raises `ConnectionError("connect failed")`
- **Handling**: Caught by the outer try/except, triggering retry logic

### 4. Safe Read Exhaustion
**Location**: `safe_read()`, line ~45
- **Handling**: After `MAX_REGISTER_RETRIES + 1` attempts all returning None, prints `[WARN] Persistent Modbus failure` and returns None
- **Impact**: The specific register value is missing from the data dictionary

## Error Recovery Strategy
```
Level 1: Register Read  → Returns None on ModbusException
Level 2: Safe Read      → Retries register read up to 2 times
Level 3: Device Poll    → Retries entire connection up to 3 times
Level 4: Lambda Handler → Records device as "failed", continues to next device
```

## Gaps in Error Handling
- No structured logging (uses `print()` statements)
- No CloudWatch metrics emitted on failures
- No dead-letter queue for failed device polls
- S3 `put_object` has no error handling (will propagate to Lambda runtime)
- Division by zero protection only via `1e-6` epsilon in savings calculation

## Cross-References
- [Behavior: Decision Logic](decision-logic.md)
- [Architecture: Patterns](../architecture/patterns.md)
- [Technical Debt: Maintenance Burden](../technical-debt/maintenance-burden.md)
