> ⚠️ **Early Access**: Behavior documentation is in early access. Please review critically.

# Business Logic

## Power Factor Correction Calculations

### Register Reading and Scaling
Every register value read from the DCRG8 is scaled by a predefined divisor to convert raw integer register values to engineering units:

| Register Group | Scale Factor | Unit |
|---------------|-------------|------|
| Power Factor | ÷1000 | dimensionless (0–1) |
| Voltages | ÷10 | Volts |
| Currents | ÷1000 | Amps |
| Active/Reactive Power | ÷10 | W / VAr |
| THD values | ÷100 | % |
| Energy counters | ÷10 | kWh / kVArh / kVAh |
| Frequency | ÷100 | Hz |
| kVAr step values | ÷100 | kVAr |

### Power Factor Calculation Logic
**Location**: `lambda/rpe-dcrg8-platform_v1.py`, lines ~200–240

1. **Uncorrected PF**: Estimates what PF would be without capacitor banks
   - `Q_cap_total` = sum of all kVAr steps for phases where `cap_{phase} == 0`
   - `Q_uncorrected = Q_measured + Q_cap_total`
   - `PF_uncorrected = P / sqrt(P² + Q_uncorrected²)`

2. **Corrected PF**: The measured PF after capacitor bank correction
   - `PF_corrected = P / sqrt(P² + Q_measured²)`

3. **PF Improvement**: `PF_corrected - PF_uncorrected`

4. **Delta to Target**: `PF_corrected - TARGET_PF` (where TARGET_PF = 0.95)

5. **Guard condition**: Calculations only execute when `P > 100` (active power above 100W threshold)

### Financial Savings Calculation
**Location**: `lambda/rpe-dcrg8-platform_v1.py`, lines ~242–260

When `pf_improvement > 0` and `P > 0`:
- `pf_cost_avoided_monthly = (Q_cap_total / (|Q_measured| + 1e-6)) × P × ENERGY_COST_PER_KWH`
- `pf_annualized_savings = pf_cost_avoided_monthly × 12`

When conditions not met: both values default to `0.0`.

### Modbus Address Translation
- **Rule**: `query_addr = (logical_addr - 1) % 65536`
- Converts 1-based Lovato documentation addresses to 0-based Modbus wire protocol addresses

### Data Record Time Bucketing
Each telemetry record includes pre-computed time aggregation keys:
- `timestamp`: Full second precision (`%Y-%m-%d %H:%M:%S`)
- `hour_bucket`: Rounded to hour
- `day_bucket`: Date only
- `week_bucket`: ISO year-week
- `month_bucket`: Year-month

## Cross-References
- [Behavior: Decision Logic](decision-logic.md)
- [Reference: Data Models](../reference/data-models.md)
- [Architecture: Components](../architecture/components.md)
