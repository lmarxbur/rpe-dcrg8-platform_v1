# Data Models

## Input Event Schema
```json
{
  "devices": [
    {
      "name": "string",
      "ip": "string",
      "port": "integer"
    }
  ]
}
```

## Telemetry Data Dictionary
The `poll_device()` function produces a dictionary with these fields:

### Electrical Parameters (from Input Registers)
| Field | Unit | Scale | Register |
|-------|------|-------|----------|
| `pf_measured` | — | ÷1000 | 0 |
| `eq_voltage` | V | ÷10 | 6 |
| `eq_current` | A | ÷1000 | 8 |
| `active_power_total` | W | ÷10 | 10 |
| `reactive_power_total` | VAr | ÷10 | 78 |
| `voltage_l1` | V | ÷10 | 64 |
| `voltage_l2` | V | ÷10 | 66 |
| `voltage_l3` | V | ÷10 | 68 |
| `current_l1` | A | ÷1000 | 70 |
| `current_l2` | A | ÷1000 | 72 |
| `current_l3` | A | ÷1000 | 74 |
| `voltage_thd_l1` | % | ÷100 | 11296 |
| `voltage_thd_l2` | % | ÷100 | 11344 |
| `voltage_thd_l3` | % | ÷100 | 11392 |
| `current_thd_l1` | % | ÷100 | 11440 |
| `current_thd_l2` | % | ÷100 | 11456 |
| `current_thd_l3` | % | ÷100 | 11536 |
| `frequency_hz` | Hz | ÷100 | 38 |

### Energy Counters (from Holding Registers)
| Field | Unit | Scale | Register |
|-------|------|-------|----------|
| `active_energy_import_kwh` | kWh | ÷10 | 22 |
| `reactive_energy_import_kvarh` | kVArh | ÷10 | 24 |
| `apparent_energy_kvah` | kVAh | ÷10 | 26 |
| `active_energy_export_kwh` | kWh | ÷10 | 28 |
| `reactive_energy_export_kvarh` | kVArh | ÷10 | 30 |

### Capacitor Bank Status
| Field | Type | Register |
|-------|------|----------|
| `cap_l1` | int (bitmask) | 8194 |
| `cap_l2` | int (bitmask) | 8195 |
| `cap_l3` | int (bitmask) | 8196 |

### kVAr Step Values
| Field Pattern | Count | Unit | Register Base |
|---------------|-------|------|--------------|
| `l1_kvar_step_{1-32}` | 32 | kVAr | 4864 |
| `l2_kvar_step_{1-32}` | 32 | kVAr | 4928 |
| `l3_kvar_step_{1-32}` | 32 | kVAr | 4992 |

### Computed Fields
| Field | Unit | Formula |
|-------|------|---------|
| `pf_uncorrected_calc` | — | `P / sqrt(P² + Q_uncorrected²)` |
| `pf_corrected_calc` | — | `P / sqrt(P² + Q_measured²)` |
| `pf_improvement` | — | `pf_corrected - pf_uncorrected` |
| `pf_delta_to_target` | — | `pf_corrected - 0.95` |
| `pf_cost_avoided_monthly` | $ | `(Q_cap / |Q_measured|) × P × cost/kWh` |
| `pf_annualized_savings` | $ | `monthly × 12` |

## S3 Record Schema
The final record stored in S3 adds:
| Field | Format |
|-------|--------|
| `device` | Device name string |
| `timestamp` | `YYYY-MM-DD HH:MM:SS` |
| `hour_bucket` | `YYYY-MM-DD HH:00:00` |
| `day_bucket` | `YYYY-MM-DD` |
| `week_bucket` | `YYYY-WW` |
| `month_bucket` | `YYYY-MM` |

## Cross-References
- [Behavior: Business Logic](../behavior/business-logic.md)
- [Reference: Interfaces](interfaces.md)
