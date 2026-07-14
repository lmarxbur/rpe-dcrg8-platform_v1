# IoT Telemetry Patterns

## Modbus/TCP Communication

### Protocol Details
- **Standard**: Modbus TCP/IP (MBAP header)
- **Default Port**: 502
- **Client Library**: pymodbus `ModbusTcpClient`
- **Connection**: TCP socket, one connection per device per poll cycle

### Register Types Used
| Type | Modbus Function Code | Purpose |
|------|---------------------|---------|
| Input Registers | FC 04 | Real-time electrical measurements (read-only) |
| Holding Registers | FC 03 | Energy counters, capacitor bank configuration |

### Address Translation
The DCRG8 uses 1-based logical addresses in documentation. The code translates to 0-based wire addresses:
```
wire_address = (logical_address - 1) % 65536
```

### Throttling Strategy
To avoid overwhelming the Modbus slave:
- 50ms between individual register reads
- 100ms between phase groups
- 200ms initial delay after connection
- 30s TCP timeout per connection

## Device: Lovato DCRG8

### Overview
The Lovato DCRG8 is a three-phase automatic power factor controller that:
- Monitors voltage, current, power, and power factor per phase
- Controls capacitor bank switching steps
- Tracks energy consumption counters
- Measures Total Harmonic Distortion (THD)

### Register Map Summary
- **Registers 0–78**: Electrical parameters (PF, V, I, P, Q)
- **Registers 38**: Frequency
- **Registers 64–78**: Per-phase voltage and current
- **Registers 4864–5055**: kVAr step values (3 phases × 32 steps)
- **Registers 8194–8196**: Capacitor bank flags
- **Registers 11296–11536**: THD measurements
- **Registers 22–30**: Energy counters

### Data Encoding
- All multi-register values are big-endian (high word first)
- 32-bit values span 2 consecutive 16-bit registers
- Signed values use two's complement encoding

## S3 Storage Pattern

### Partitioning
```
s3://{bucket}/stryker/devices/{device_name}/{YYYY}/{MM}/{DD}/{HH}/{MM}/{SS}.json
```

### Benefits
- Enables Athena partition pruning for time-range queries
- Supports Glue crawler auto-discovery
- Natural backup/lifecycle management by date prefix

### Record Enrichment
Each raw telemetry poll is enriched with pre-computed time aggregation keys:
- `hour_bucket`, `day_bucket`, `week_bucket`, `month_bucket`
- Enables efficient GROUP BY queries in Athena without date functions

## Cross-References
- [Architecture: System Overview](../architecture/system-overview.md)
- [Reference: Data Models](../reference/data-models.md)
- [Behavior: Business Logic](../behavior/business-logic.md)
