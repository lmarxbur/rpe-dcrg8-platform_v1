> ⚠️ **Early Access**: Behavior documentation is in early access. Please review critically.

# Workflows

## Workflow: Telemetry Collection Pipeline

**Entry Point**: `lambda_handler(event, context)`

### Flow
```
1. Receive EventBridge event with device list
2. Validate device list (error if empty)
3. For each device in list:
   a. Log polling start
   b. Call poll_device(device)
      i.   Open Modbus/TCP connection (retry up to 3 times)
      ii.  Read input registers (electrical parameters)
      iii. Read holding registers (energy counters)
      iv.  Read frequency register
      v.   Read capacitor bank flags (3 phases)
      vi.  Read kVAr step values (32 steps × 3 phases = 96 reads)
      vii. Calculate power factor metrics
      viii. Calculate financial savings
      ix.  Close connection, return data dict
   c. If poll successful: ingest_to_s3(device, data)
      i.   Generate timestamp and time buckets
      ii.  Build record with device name + timestamps + telemetry
      iii. Compute S3 key with partitioned path
      iv.  PUT object to S3
   d. Record result (success/failed)
4. Return results array
```

### Timing Characteristics
- 50ms delay between individual register reads
- 100ms delay between phase groups for kVAr steps
- 200ms delay after client creation before first read
- 1s delay between connection retry attempts
- 30s Modbus TCP timeout

## Cross-References
- [Behavior: Business Logic](business-logic.md)
- [Behavior: Error Handling](error-handling.md)
- [Diagrams: Behavioral](../diagrams/behavioral/sequence-diagrams.md)
