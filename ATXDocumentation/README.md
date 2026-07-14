# RPE DCRG8 Telemetry Platform - Documentation

Comprehensive documentation for the RPE DCRG8 Telemetry Platform, an AWS serverless pipeline that collects Modbus/TCP telemetry from Lovato DCRG8 power factor controllers and stores it in S3.

## Navigation

### Root Documents
- [Project Overview](project-overview.md) — High-level summary of the system
- [Technical Debt Report](technical-debt-report.md) — Executive summary of technical debt and AWS transformation recommendations

### Architecture
- [System Overview](architecture/system-overview.md) — Technology stack, deployment model, architectural decisions
- [Components](architecture/components.md) — Major system components and responsibilities
- [Dependencies](architecture/dependencies.md) — Internal and external dependency mapping
- [Patterns](architecture/patterns.md) — Design and architectural patterns

### Behavior
- [Business Logic](behavior/business-logic.md) — Extracted business rules and calculations
- [Workflows](behavior/workflows.md) — Application-level process flows
- [Decision Logic](behavior/decision-logic.md) — Decision trees and branching patterns
- [Error Handling](behavior/error-handling.md) — Exception patterns and recovery

### Reference
- [Program Structure](reference/program-structure.md) — Complete structural hierarchy
- [Interfaces](reference/interfaces.md) — Function signatures and contracts
- [Data Models](reference/data-models.md) — Type definitions and data structures
- [API Reference](reference/api-reference.md) — Callable services and endpoints
- [Modules](reference/modules.md) — Module organization

### Analysis
- [Code Metrics](analysis/code-metrics.md) — Complexity measurements and quality indicators
- [Complexity Analysis](analysis/complexity-analysis.md) — Code complexity hotspots
- [Dependency Analysis](analysis/dependency-analysis.md) — Dependency mapping and health
- [Security Patterns](analysis/security-patterns.md) — Security implementations
- [Tech Debt](analysis/tech-debt.md) — Comprehensive technical debt assessment

### Diagrams
- [Structural](diagrams/structural/) — Component and module diagrams
- [Behavioral](diagrams/behavioral/) — Sequence and activity diagrams
- [Architecture](diagrams/architecture/) — System context and integration patterns

### Technical Debt
- [Summary](technical-debt/summary.md) — Overview of all findings
- [Outdated Components](technical-debt/outdated-components.md) — Obsolete component analysis
- [Maintenance Burden](technical-debt/maintenance-burden.md) — High-maintenance areas
- [Remediation Plan](technical-debt/remediation-plan.md) — Prioritized action items

### Migration
- [Component Order](migration/component-order.md) — Migration dependency ordering
- [Test Specifications](migration/test-specifications.md) — Validation test cases
- [Validation Criteria](migration/validation-criteria.md) — Success criteria

### Specialized
- [IoT Telemetry Patterns](specialized/iot-telemetry-patterns.md) — Modbus/TCP and device communication
