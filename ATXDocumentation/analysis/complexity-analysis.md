# Complexity Analysis

## Hotspot: `poll_device()` Function

**Cyclomatic Complexity**: 12 (High for a single function)
**Lines**: ~152
**Nested Depth**: Up to 4 levels (for loop → if → try/except → if)

### Complexity Drivers
1. **Multiple register group iterations** with different configurations
2. **Three-level retry logic** (register retry + connection retry + safe_read)
3. **Conditional calculations** based on power thresholds
4. **Nested loops** for 3 phases × 32 steps of kVAr readings

### Recommended Decomposition
The function could be split into:
- `read_electrical_params(client)` — Input register reading
- `read_energy_counters(client)` — Holding register reading
- `read_capacitor_status(client)` — Cap flags and kVAr steps
- `calculate_power_factor(data)` — PF computation
- `calculate_savings(data)` — Financial calculations

## Other Functions
All other functions have complexity ≤ 3, which is well within acceptable limits.

## Overall Assessment
The codebase is simple overall with one concentrated complexity hotspot. The monolithic `poll_device()` function handles too many responsibilities but is still readable due to clear section comments.

## Cross-References
- [Analysis: Code Metrics](code-metrics.md)
- [Architecture: Patterns](../architecture/patterns.md)
