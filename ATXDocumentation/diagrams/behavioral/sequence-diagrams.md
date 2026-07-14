# Behavioral Diagrams

## Sequence Diagram: Telemetry Collection

```
EventBridge          Lambda           ModbusTcpClient       DCRG8 Device         S3
    │                   │                   │                    │                 │
    │── schedule ──────►│                   │                    │                 │
    │                   │                   │                    │                 │
    │                   │── create() ──────►│                    │                 │
    │                   │                   │                    │                 │
    │                   │── connect() ─────►│── TCP connect ────►│                 │
    │                   │                   │◄── connected ──────│                 │
    │                   │◄── True ──────────│                    │                 │
    │                   │                   │                    │                 │
    │                   │  ┌─── loop: input registers ───┐      │                 │
    │                   │  │                              │      │                 │
    │                   │──┤ read_input_registers() ─────►│─────►│                 │
    │                   │  │                       ◄──────│◄─────│                 │
    │                   │  │ sleep(50ms)                   │      │                 │
    │                   │  └──────────────────────────────┘      │                 │
    │                   │                   │                    │                 │
    │                   │  ┌─── loop: holding registers ──┐      │                 │
    │                   │  │                              │      │                 │
    │                   │──┤ read_holding_registers() ───►│─────►│                 │
    │                   │  │                       ◄──────│◄─────│                 │
    │                   │  │ sleep(50ms)                   │      │                 │
    │                   │  └──────────────────────────────┘      │                 │
    │                   │                   │                    │                 │
    │                   │── close() ───────►│── TCP close ──────►│                 │
    │                   │                   │                    │                 │
    │                   │── calculate PF ──►│ (internal)         │                 │
    │                   │                   │                    │                 │
    │                   │── put_object() ──────────────────────────────────────────►│
    │                   │◄─────────────────────────────────────────────────── 200 ──│
    │                   │                   │                    │                 │
    │◄── results ───────│                   │                    │                 │
```

## Activity Diagram: Power Factor Calculation

```
┌─────────────────┐
│ Get P, Q_meas   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Sum Q_cap for   │
│ active phases   │
│ (cap_phase == 0)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Q_uncorr =      │
│ Q_meas + Q_cap  │
└────────┬────────┘
         │
         ▼
    ┌────┴────┐
    │ P > 100?│
    └────┬────┘
    Yes/ │ \No
       │    │
       ▼    ▼
┌──────────┐ ┌──────────┐
│ PF_uncorr│ │ Set both │
│ = P/√(P²+│ │ to None  │
│ Q_un²)   │ └──────────┘
│          │
│ PF_corr  │
│ = P/√(P²+│
│ Q_m²)    │
└────┬─────┘
     │
     ▼
┌──────────────┐
│ improvement  │
│ = corr - un  │
│ delta = corr │
│   - 0.95     │
└──────────────┘
```

## Cross-References
- [Behavior: Workflows](../../behavior/workflows.md)
- [Diagrams: Architecture](../architecture/system-context.md)
