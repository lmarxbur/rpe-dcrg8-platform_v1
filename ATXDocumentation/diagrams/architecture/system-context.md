# Architecture Diagrams

## System Context Diagram

```
                    ┌─────────────────────────────┐
                    │       External Systems       │
                    │                              │
                    │  ┌───────────────────────┐  │
                    │  │  Lovato DCRG8 Devices │  │
                    │  │  (Power Factor Ctrl)  │  │
                    │  └───────────┬───────────┘  │
                    └──────────────┼──────────────┘
                                   │ Modbus/TCP
                                   │ (port 502)
┌──────────────────────────────────┼──────────────────────────────────┐
│                             AWS Cloud                                 │
│                                  │                                    │
│  ┌──────────┐    ┌──────────────▼──────────────┐    ┌──────────┐   │
│  │EventBridge│───►│    Lambda Function          │───►│   S3     │   │
│  │(Schedule) │    │ rpe-dcrg8-platform_v1.py    │    │(Raw JSON)│   │
│  └──────────┘    └─────────────────────────────┘    └────┬─────┘   │
│                                                           │          │
│                                                           ▼          │
│                                                    ┌──────────┐     │
│                                                    │   Glue   │     │
│                                                    │  (ETL)   │     │
│                                                    └────┬─────┘     │
│                                                         │            │
│                                                         ▼            │
│                                                    ┌──────────┐     │
│  ┌──────────┐                                      │  Athena  │     │
│  │ Cognito  │◄─── User Auth ──────────────────────►│ (Query)  │     │
│  └──────────┘                                      └────┬─────┘     │
│                                                         │            │
│                                                         ▼            │
│                                                    ┌──────────┐     │
│                                                    │QuickSight│     │
│                                                    │(Dashboards)    │
│                                                    └──────────┘     │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
┌──────────┐         ┌──────────┐         ┌──────────┐
│  DCRG8   │ Modbus  │  Lambda  │  JSON   │    S3    │
│  Device  │────────►│ Function │────────►│  Bucket  │
└──────────┘ Registers└──────────┘ Records └──────────┘
                          │                      │
                          │ Computed:            │ Partitioned by:
                          │ - PF metrics         │ - device/YYYY/MM/DD/HH
                          │ - Cost savings       │
                          │ - Time buckets       │
                          ▼                      ▼
                    ┌──────────┐         ┌──────────┐
                    │CloudWatch│         │  Athena  │
                    │  Logs    │         │  Tables  │
                    └──────────┘         └──────────┘
```

## Security Boundaries

```
┌─────────────────── VPC / Network Boundary ───────────────────┐
│                                                                │
│  ┌──────────────────┐              ┌──────────────────────┐  │
│  │  OT Network      │              │  AWS VPC             │  │
│  │  (Industrial)    │              │                      │  │
│  │                  │   Modbus/TCP │  ┌──────────────┐   │  │
│  │  ┌──────────┐   │◄────────────►│  │   Lambda     │   │  │
│  │  │  DCRG8   │   │   Port 502   │  │   (ENI)      │   │  │
│  │  └──────────┘   │              │  └──────┬───────┘   │  │
│  │                  │              │         │ IAM Role   │  │
│  └──────────────────┘              │         ▼           │  │
│                                    │  ┌──────────────┐   │  │
│                                    │  │     S3       │   │  │
│                                    │  │ (encrypted)  │   │  │
│                                    │  └──────────────┘   │  │
│                                    └──────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
```

## Cross-References
- [Architecture: System Overview](../../architecture/system-overview.md)
- [Analysis: Security Patterns](../../analysis/security-patterns.md)
