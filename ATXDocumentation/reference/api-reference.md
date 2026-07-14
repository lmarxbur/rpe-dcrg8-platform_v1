# API Reference

## Lambda Function Entry Point

### `lambda_handler(event, context)`
**Invocation**: AWS Lambda (triggered by EventBridge)

**Request (event)**:
```json
{
  "devices": [
    {"name": "device-01", "ip": "192.168.1.100", "port": 502}
  ]
}
```

**Response (success)**:
```json
{
  "results": [
    {"device": "device-01", "status": "success"},
    {"device": "device-02", "status": "failed"}
  ]
}
```

**Response (error — no devices)**:
```json
{
  "status": "error",
  "message": "No devices specified"
}
```

## S3 Data API

### Write Path
- **Bucket**: `rpe-dcrg8-data` (configurable via `S3_BUCKET`)
- **Key**: `stryker/devices/{device_name}/{YYYY}/{MM}/{DD}/{HH}/{MM}/{SS}.json`
- **Content-Type**: application/json (implicit)
- **Operation**: `s3:PutObject`

## Modbus/TCP Interface

### Connection Parameters
| Parameter | Value |
|-----------|-------|
| Protocol | Modbus/TCP |
| Default Port | 502 (configurable per device) |
| Timeout | 30 seconds |

### Register Map
See [Data Models](data-models.md) for complete register address mapping.

## Cross-References
- [Reference: Interfaces](interfaces.md)
- [Reference: Data Models](data-models.md)
