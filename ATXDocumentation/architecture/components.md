# Components

## Lambda Function: `rpe-dcrg8-platform_v1`
**File**: `lambda/rpe-dcrg8-platform_v1.py` (299 LOC)

### Functional Sections

| Section | Lines | Responsibility |
|---------|-------|---------------|
| Config | 1–22 | Environment variables, constants, S3 client init |
| Helpers | 24–48 | Address translation, 32-bit parsing, retry wrapper |
| Modbus Read | 50–103 | Low-level register read functions |
| Polling | 105–260 | Device polling, data collection, PF calculations |
| S3 Ingest | 262–288 | Record formatting and S3 upload |
| Lambda Handler | 290–299 | Entry point, device iteration, result aggregation |

### Component Responsibilities

#### Configuration Layer
- Reads `S3_BUCKET` and `ENERGY_COST_PER_KWH` from environment
- Defines constants: `TARGET_PF = 0.95`, `MAX_REGISTER_RETRIES = 2`
- Initializes global boto3 S3 client

#### Helper Utilities
- `get_query_addr()`: Converts logical Modbus address to wire address
- `parse_32bit_unsigned()` / `parse_32bit_signed()`: Decode two 16-bit registers into 32-bit values
- `safe_read()`: Generic retry wrapper for any read function

#### Modbus Communication
- `read_input_32()`: Read 32-bit value from input registers
- `read_holding_32()`: Read 32-bit value from holding registers
- `read_holding_16()`: Read single 16-bit holding register

#### Device Polling Engine
- `poll_device()`: Orchestrates complete data collection from one DCRG8 unit
- Reads electrical parameters, energy counters, capacitor bank status, kVAr step values
- Computes power factor metrics and financial savings

#### Data Ingestion
- `ingest_to_s3()`: Formats record with timestamps and time buckets, writes to S3

#### Entry Point
- `lambda_handler()`: Processes device list from event, polls each, returns results

## Cross-References
- [Architecture: System Overview](system-overview.md)
- [Reference: Program Structure](../reference/program-structure.md)
- [Behavior: Business Logic](../behavior/business-logic.md)
