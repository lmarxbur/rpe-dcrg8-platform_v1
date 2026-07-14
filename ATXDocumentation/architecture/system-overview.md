# System Overview

## Architecture Style
Serverless event-driven architecture on AWS.

## Deployment Model
- **Compute**: AWS Lambda (Python runtime)
- **Trigger**: Amazon EventBridge (scheduled rule)
- **Storage**: Amazon S3 (raw JSON telemetry)
- **Analytics**: AWS Glue (ETL) → Amazon Athena (SQL queries) → Amazon QuickSight (dashboards)
- **Auth**: Amazon Cognito (user access to dashboards)

## Technology Stack
- **Language**: Python 3.x
- **AWS SDK**: boto3 (S3 client)
- **Modbus Client**: pymodbus (ModbusTcpClient)
- **Standard Library**: json, struct, math, time, datetime, os

## Key Architectural Decisions
1. **Single Lambda function**: All device polling logic consolidated in one function for simplicity
2. **JSON-per-record storage**: Each poll produces one JSON file in S3, partitioned by device/timestamp for efficient querying
3. **Synchronous polling**: Devices are polled sequentially within a single Lambda invocation
4. **Environment-based configuration**: S3 bucket and energy cost are configurable via environment variables
5. **Retry-at-register level**: Individual Modbus register reads are retried independently

## Data Flow
```
EventBridge (Schedule) → Lambda → Modbus/TCP → DCRG8 Devices
                           ↓
                        S3 (JSON)
                           ↓
                      Glue (ETL) → Athena → QuickSight
```

## Cross-References
- [Components](components.md)
- [Dependencies](dependencies.md)
- [Behavior: Workflows](../behavior/workflows.md)
