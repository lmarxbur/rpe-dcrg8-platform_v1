# Interfaces

## Function Contracts

### `lambda_handler(event, context) → dict`
- **Input**: `event` — dict with key `"devices"` containing list of device dicts
- **Device dict schema**: `{"name": str, "ip": str, "port": int}`
- **Output**: `{"results": [{"device": str, "status": "success"|"failed"}]}` or `{"status": "error", "message": str}`

### `poll_device(device) → Optional[dict]`
- **Input**: Device dict `{"name": str, "ip": str, "port": int}`
- **Output**: Dictionary of telemetry fields (see [Data Models](data-models.md)) or `None` on failure

### `ingest_to_s3(device, data) → None`
- **Input**: Device dict + telemetry data dictionary
- **Side effect**: Writes JSON to S3 at `stryker/devices/{name}/{YYYY}/{MM}/{DD}/{HH}/{MM}/{SS}.json`

### `safe_read(read_func) → Optional[int]`
- **Input**: Zero-argument callable returning `Optional[int]`
- **Output**: First non-None result, or None after exhausting retries

### `read_input_32(client, addr, signed=True) → Optional[int]`
- **Input**: ModbusTcpClient, logical register address, sign flag
- **Output**: 32-bit integer or None

### `read_holding_32(client, addr, signed=False) → Optional[int]`
- **Input**: ModbusTcpClient, logical register address, sign flag
- **Output**: 32-bit integer or None

### `read_holding_16(client, addr) → Optional[int]`
- **Input**: ModbusTcpClient, logical register address
- **Output**: 16-bit unsigned integer or None

### `get_query_addr(logical_addr) → int`
- **Input**: 1-based logical Modbus address
- **Output**: 0-based wire protocol address

### `parse_32bit_unsigned(regs) → int`
- **Input**: List of two 16-bit register values [high, low]
- **Output**: Unsigned 32-bit integer

### `parse_32bit_signed(regs) → int`
- **Input**: List of two 16-bit register values [high, low]
- **Output**: Signed 32-bit integer

## External Interfaces

### AWS S3
- **Operation**: `put_object`
- **Bucket**: Configured via `S3_BUCKET` env var
- **Key pattern**: `stryker/devices/{device_name}/{YYYY}/{MM}/{DD}/{HH}/{MM}/{SS}.json`
- **Body**: JSON-encoded telemetry record

### Modbus/TCP
- **Client**: `pymodbus.client.ModbusTcpClient`
- **Operations**: `read_input_registers`, `read_holding_registers`
- **Timeout**: 30 seconds

## Cross-References
- [Reference: Data Models](data-models.md)
- [Reference: API Reference](api-reference.md)
