# Test Specifications

## Unit Tests

### Test: Address Translation
| Case | Input | Expected Output |
|------|-------|-----------------|
| Standard address | `get_query_addr(1)` | `0` |
| Higher address | `get_query_addr(100)` | `99` |
| Large address | `get_query_addr(11296)` | `11295` |

### Test: 32-bit Parsing
| Case | Input | Expected Output |
|------|-------|-----------------|
| Unsigned zero | `parse_32bit_unsigned([0, 0])` | `0` |
| Unsigned max | `parse_32bit_unsigned([0xFFFF, 0xFFFF])` | `4294967295` |
| Signed positive | `parse_32bit_signed([0, 1000])` | `1000` |
| Signed negative | `parse_32bit_signed([0xFFFF, 0xFFFF])` | `-1` |

### Test: Power Factor Calculation
| Case | P | Q_measured | Q_cap_total | Expected PF_corr | Expected PF_uncorr |
|------|---|-----------|-------------|------------------|-------------------|
| Normal load | 5000 | 2000 | 1000 | 0.928 | 0.857 |
| Low power (guard) | 50 | 20 | 10 | None | None |
| Unity PF | 5000 | 0 | 0 | 1.000 | 1.000 |

### Test: Financial Savings
| Case | pf_improvement | P | Q_cap | Q_measured | Expected Monthly |
|------|---------------|---|-------|------------|-----------------|
| Active savings | 0.05 | 5000 | 1000 | 2000 | `(1000/2000) × 5000 × 0.13 = 325.0` |
| No improvement | 0.0 | 5000 | 0 | 2000 | 0.0 |
| No power | 0.05 | 0 | 1000 | 2000 | 0.0 |

## Integration Tests

### Test: Modbus Read with Retry
- Mock `ModbusTcpClient` to return error on first call, valid response on second
- Verify `safe_read()` returns value after retry

### Test: S3 Ingestion
- Mock `boto3.client("s3").put_object`
- Verify correct key format and JSON body structure

### Test: Lambda Handler
- Provide event with 2 devices (one reachable, one unreachable via mock)
- Verify response contains both success and failure results

## Cross-References
- [Migration: Validation Criteria](validation-criteria.md)
- [Reference: Interfaces](../reference/interfaces.md)
