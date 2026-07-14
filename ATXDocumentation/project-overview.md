# Project Overview

## System Name
RPE DCRG8 Telemetry Platform

## Purpose
AWS serverless telemetry pipeline that collects power quality and energy data from Lovato DCRG8 power factor controllers via Modbus/TCP, performs power factor correction calculations, and stores structured telemetry in Amazon S3 for downstream analytics.

## Technology Stack
| Layer | Technology |
|-------|-----------|
| Language | Python (Lambda runtime) |
| Cloud Platform | AWS (Lambda, S3, EventBridge, Glue, Athena, QuickSight, Cognito) |
| Protocol | Modbus/TCP |
| Hardware | Lovato DCRG8 power factor controllers |
| Libraries | pymodbus, boto3 |

## Architecture Summary
The system is a single AWS Lambda function triggered by EventBridge on a schedule. It connects to one or more DCRG8 devices, reads Modbus registers (input and holding), computes power factor metrics and cost savings, then writes timestamped JSON records to S3. Downstream services (Glue, Athena, QuickSight) provide ETL, querying, and visualization.

## Project Structure
```
rpe-dcrg8-platform_v1/
├── lambda/
│   └── rpe-dcrg8-platform_v1.py   # Main Lambda function (299 LOC)
└── README.md                        # Project documentation
```

## Key Characteristics
- **Single-function architecture**: One Lambda function handles all telemetry collection
- **Event-driven**: Triggered by EventBridge scheduler
- **Industrial IoT**: Communicates with physical power factor controllers
- **Financial analytics**: Calculates power factor cost savings and annualized savings
- **Multi-device**: Supports polling multiple DCRG8 devices per invocation

## Cross-References
- [Architecture: System Overview](architecture/system-overview.md)
- [Behavior: Business Logic](behavior/business-logic.md)
- [Technical Debt Report](technical-debt-report.md)
