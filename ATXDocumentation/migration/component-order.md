# Component Migration Order

## Overview
This document defines the recommended order for migrating or modernizing the RPE DCRG8 Platform components, based on dependency relationships.

## Migration Phases

### Phase 1: Foundation (No dependencies on other phases)
1. **Add dependency management** (`requirements.txt` / `pyproject.toml`)
2. **Add infrastructure-as-code** (SAM template or CDK)
3. **Pin Python runtime version** (3.12+)

### Phase 2: Code Quality (Depends on Phase 1)
4. **Extract pure calculation functions** from `poll_device()`
   - `calculate_power_factor(P, Q_measured, Q_cap_total)`
   - `calculate_savings(pf_improvement, P, Q_cap_total, Q_measured, cost_per_kwh)`
5. **Replace `datetime.utcnow()`** with timezone-aware alternative
6. **Replace `print()` with `logging` module**

### Phase 3: Testing (Depends on Phase 2)
7. **Add unit tests** for extracted calculation functions
8. **Add integration tests** with mocked Modbus client
9. **Add S3 integration tests** with mocked boto3

### Phase 4: Observability (Depends on Phase 1)
10. **Add CloudWatch custom metrics**
11. **Add structured JSON logging**
12. **Set up CloudWatch Alarms**

## Dependency Graph
```
Phase 1: [Requirements] [IaC] [Runtime Pin]
              │            │
              ▼            ▼
Phase 2: [Extract Fns] [Fix deprecations] [Logging]
              │
              ▼
Phase 3: [Unit Tests] [Integration Tests]
              
Phase 4: [Metrics] [Alarms] (parallel with Phase 2/3)
```

## Cross-References
- [Technical Debt: Remediation Plan](../technical-debt/remediation-plan.md)
- [Migration: Validation Criteria](validation-criteria.md)
