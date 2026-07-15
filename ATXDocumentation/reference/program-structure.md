# Program Structure

## Module: `lambda/rpe-dcrg8-platform_v1.py`

### Imports
```python
import time
import json
import struct
import math
from datetime import datetime
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException
import boto3
import os
```

### Module-Level Constants and Globals
| Name | Type | Value/Source |
|------|------|-------------|
| `S3_BUCKET` | str | `os.getenv("S3_BUCKET", "rpe-dcrg8-data")` |
| `ENERGY_COST_PER_KWH` | float | `os.getenv("ENERGY_COST_PER_KWH", "0.13")` |
| `TARGET_PF` | float | `0.95` |
| `MAX_REGISTER_RETRIES` | int | `2` |
| `s3_client` | boto3.S3.Client | `boto3.client("s3")` |

### Functions

| Function | Parameters | Returns | Lines |
|----------|-----------|---------|-------|
| `get_query_addr` | `logical_addr: int` | `int` | 25–26 |
| `parse_32bit_unsigned` | `regs: list[int]` | `int` | 29–30 |
| `parse_32bit_signed` | `regs: list[int]` | `int` | 33–35 |
| `safe_read` | `read_func: Callable` | `Optional[int]` | 38–48 |
| `read_input_32` | `client, addr, signed=True` | `Optional[int]` | 53–68 |
| `read_holding_32` | `client, addr, signed=False` | `Optional[int]` | 71–90 |
| `read_holding_16` | `client, addr` | `Optional[int]` | 93–103 |
| `poll_device` | `device: dict` | `Optional[dict]` | 108–260 |
| `ingest_to_s3` | `device: dict, data: dict` | `None` | 265–288 |
| `lambda_handler` | `event: dict, context` | `dict` | 293–316 |

## Cross-References
- [Architecture: Components](../architecture/components.md)
- [Reference: Interfaces](interfaces.md)
