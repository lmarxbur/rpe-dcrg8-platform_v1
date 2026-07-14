# Structural Diagrams

## Component Diagram
```
┌─────────────────────────────────────────────────────────┐
│                    AWS Lambda Function                    │
│              rpe-dcrg8-platform_v1.py                    │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Config     │  │   Helpers    │  │ Modbus Read  │  │
│  │              │  │              │  │              │  │
│  │ S3_BUCKET    │  │ get_query_   │  │ read_input   │  │
│  │ ENERGY_COST  │  │   addr()    │  │   _32()      │  │
│  │ TARGET_PF    │  │ parse_32bit  │  │ read_holding │  │
│  │              │  │ safe_read()  │  │   _32()/_16()│  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │              poll_device()                         │   │
│  │  - Connect to DCRG8 via Modbus/TCP               │   │
│  │  - Read electrical parameters                     │   │
│  │  - Read energy counters                           │   │
│  │  - Read capacitor bank status                     │   │
│  │  - Calculate PF metrics                           │   │
│  │  - Calculate financial savings                    │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────────┐  ┌──────────────────────────────┐    │
│  │ ingest_to_s3 │  │     lambda_handler()         │    │
│  │              │  │  - Iterate devices            │    │
│  │ Format record│  │  - Poll each                  │    │
│  │ Write to S3  │  │  - Ingest results             │    │
│  └──────────────┘  └──────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

## Module Dependency Graph
```
lambda_handler
    │
    ├──► poll_device
    │       │
    │       ├──► safe_read ──► read_input_32 ──► get_query_addr
    │       │                                  ──► parse_32bit_signed
    │       │                                  ──► parse_32bit_unsigned
    │       │
    │       ├──► safe_read ──► read_holding_32 ──► get_query_addr
    │       │                                   ──► parse_32bit_unsigned
    │       │
    │       └──► safe_read ──► read_holding_16 ──► get_query_addr
    │
    └──► ingest_to_s3
             │
             └──► s3_client.put_object (boto3)
```

## Cross-References
- [Architecture: Components](../../architecture/components.md)
- [Reference: Modules](../../reference/modules.md)
