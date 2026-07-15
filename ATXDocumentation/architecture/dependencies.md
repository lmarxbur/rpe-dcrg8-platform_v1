# Dependencies

## External Libraries

| Library | Purpose | Version Specified |
|---------|---------|-------------------|
| `pymodbus` | Modbus/TCP communication with DCRG8 devices | No (not pinned) |
| `boto3` | AWS SDK for S3 operations | No (provided by Lambda runtime) |

## Standard Library Usage

| Module | Purpose |
|--------|---------|
| `time` | Delays between Modbus reads |
| `json` | JSON serialization for S3 records |
| `struct` | Binary data unpacking (32-bit signed integers) |
| `math` | Square root for power factor calculation |
| `datetime` | Timestamp generation |
| `os` | Environment variable access |

## AWS Service Dependencies

| Service | Role | Integration |
|---------|------|-------------|
| Lambda | Compute | Hosts the function |
| EventBridge | Trigger | Scheduled invocation |
| S3 | Storage | `put_object` for telemetry JSON |
| Glue | ETL | Downstream processing (not directly referenced in code) |
| Athena | Query | Downstream analytics (not directly referenced in code) |
| QuickSight | Visualization | Dashboards (not directly referenced in code) |
| Cognito | Authentication | User access control (not directly referenced in code) |

## Hardware Dependencies

| Device | Protocol | Purpose |
|--------|----------|---------|
| Lovato DCRG8 | Modbus/TCP | Power factor controller providing telemetry data |

## Dependency Graph
```
Lambda Handler
├── boto3.client("s3")        → Amazon S3
├── pymodbus.ModbusTcpClient  → DCRG8 Device (Modbus/TCP)
├── pymodbus.ModbusException  → Error handling
└── Standard Library
    ├── json     → Record serialization
    ├── struct   → Binary parsing
    ├── math     → PF calculations
    ├── time     → Polling delays
    ├── datetime → Timestamps
    └── os       → Configuration
```

## Cross-References
- [Analysis: Dependency Analysis](../analysis/dependency-analysis.md)
- [Technical Debt: Outdated Components](../technical-debt/outdated-components.md)
