# Modules

## Module: `lambda/rpe-dcrg8-platform_v1`

This is the sole module in the project. It is a single-file Python Lambda function with no sub-modules or package structure.

### Internal Organization (by section comments)

| Section | Purpose | Functions |
|---------|---------|-----------|
| CONFIG | Configuration and initialization | — (module-level) |
| HELPERS | Utility functions | `get_query_addr`, `parse_32bit_unsigned`, `parse_32bit_signed`, `safe_read` |
| MODBUS READ FUNCTIONS | Hardware communication | `read_input_32`, `read_holding_32`, `read_holding_16` |
| POLLING | Device data collection | `poll_device` |
| S3 INGEST | Data persistence | `ingest_to_s3` |
| LAMBDA HANDLER | Entry point | `lambda_handler` |

### Dependency Flow (internal)
```
lambda_handler
├── poll_device
│   ├── safe_read
│   │   ├── read_input_32
│   │   │   ├── get_query_addr
│   │   │   ├── parse_32bit_signed
│   │   │   └── parse_32bit_unsigned
│   │   ├── read_holding_32
│   │   │   ├── get_query_addr
│   │   │   └── parse_32bit_unsigned
│   │   └── read_holding_16
│   │       └── get_query_addr
│   └── (inline calculations)
└── ingest_to_s3
    └── s3_client.put_object
```

## Cross-References
- [Reference: Program Structure](program-structure.md)
- [Architecture: Components](../architecture/components.md)
