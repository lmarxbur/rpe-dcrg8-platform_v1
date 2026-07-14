# Code Metrics

## Overview
| Metric | Value |
|--------|-------|
| Total Source Files | 1 |
| Total Lines of Code | 299 |
| Language | Python |
| Functions | 10 |
| Classes | 0 |
| External Dependencies | 2 (pymodbus, boto3) |

## Function-Level Metrics

| Function | LOC | Cyclomatic Complexity | Parameters |
|----------|-----|----------------------|------------|
| `get_query_addr` | 2 | 1 | 1 |
| `parse_32bit_unsigned` | 2 | 1 | 1 |
| `parse_32bit_signed` | 3 | 1 | 1 |
| `safe_read` | 10 | 2 | 1 |
| `read_input_32` | 15 | 3 | 3 |
| `read_holding_32` | 19 | 3 | 3 |
| `read_holding_16` | 11 | 3 | 2 |
| `poll_device` | 152 | 12 | 1 |
| `ingest_to_s3` | 23 | 1 | 2 |
| `lambda_handler` | 26 | 3 | 2 |

## Quality Indicators
- **Test coverage**: None (no test files present)
- **Documentation**: Inline section comments, one docstring (`safe_read`)
- **Type annotations**: None
- **Linting configuration**: None present

## Cross-References
- [Analysis: Complexity Analysis](complexity-analysis.md)
- [Architecture: Components](../architecture/components.md)
