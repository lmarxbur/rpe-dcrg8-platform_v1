# Architectural Patterns

## Patterns Identified

### 1. Serverless Function Pattern
The entire application is a single AWS Lambda function invoked by EventBridge. No persistent compute infrastructure is maintained.

### 2. Event-Driven Ingestion
- Trigger: EventBridge scheduled event containing device list
- Processing: Sequential device polling
- Output: JSON record per device per invocation to S3

### 3. Retry/Resilience Pattern
- **Register-level retries**: `safe_read()` wraps individual Modbus reads with configurable retries (`MAX_REGISTER_RETRIES = 2`)
- **Connection-level retries**: `poll_device()` retries the entire device connection up to 3 times
- **Graceful degradation**: Failed registers return `None`; partial data is still stored

### 4. Configuration via Environment
- `S3_BUCKET` and `ENERGY_COST_PER_KWH` are externalized via environment variables with defaults
- `TARGET_PF` is a module-level constant

### 5. Partitioned Storage Pattern
S3 keys follow a hierarchical partitioning scheme:
```
stryker/devices/{device_name}/{YYYY}/{MM}/{DD}/{HH}/{MM}/{SS}.json
```
This enables efficient time-range queries via Athena/Glue.

### 6. Polling with Throttling
Deliberate `time.sleep()` calls between register reads prevent overwhelming the Modbus slave device.

## Anti-Patterns Identified

### 1. Monolithic Lambda
All logic (connection, reading, calculation, storage) is in a single function. For the current scope this is acceptable, but it limits testability and reuse.

### 2. No Dependency Injection
The S3 client is a module-level global. This makes unit testing difficult without mocking at the module level.

### 3. Synchronous Sequential Polling
Devices are polled one at a time. For large device fleets this could exceed Lambda timeout.

## Cross-References
- [Architecture: System Overview](system-overview.md)
- [Analysis: Complexity Analysis](../analysis/complexity-analysis.md)
