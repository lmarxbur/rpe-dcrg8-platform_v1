# Validation Criteria

## Functional Validation

| # | Criterion | Validation Method |
|---|-----------|------------------|
| 1 | Lambda handler accepts event with device list and returns results | Unit test with mock devices |
| 2 | Modbus register values are correctly scaled to engineering units | Unit test with known register values |
| 3 | Power factor calculations match expected formulas | Unit test with reference data |
| 4 | S3 records contain all required time buckets | Integration test with mocked S3 |
| 5 | S3 key follows partitioned path format | Integration test assertion |
| 6 | Retry logic handles transient Modbus failures | Unit test with controlled failure injection |
| 7 | Empty device list returns error response | Unit test |

## Non-Functional Validation

| # | Criterion | Validation Method |
|---|-----------|------------------|
| 1 | Lambda completes within configured timeout for expected device count | Load test with target device count |
| 2 | No hardcoded credentials in source | Static analysis / code review |
| 3 | Dependencies pinned to specific version ranges | Verify `requirements.txt` exists with version constraints |
| 4 | Infrastructure defined as code | Verify SAM/CDK template exists and is deployable |

## Migration Success Criteria

| # | Criterion | Evidence |
|---|-----------|----------|
| 1 | All existing telemetry fields preserved | Compare output schema before/after |
| 2 | S3 path structure unchanged | Verify key format matches `stryker/devices/{name}/{YYYY}/{MM}/{DD}/{HH}/{MM}/{SS}.json` |
| 3 | No data loss during migration | Compare record counts pre/post migration window |
| 4 | PF calculation results unchanged | Run both versions against same register data, diff outputs |

## Cross-References
- [Migration: Test Specifications](test-specifications.md)
- [Migration: Component Order](component-order.md)
