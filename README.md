# RPE DCRG8 Telemetry Platform

AWS telemetry pipeline for Lovato DCRG8 power factor controllers.

## Purpose

Collect Modbus/TCP telemetry from DCRG8 devices,
store raw telemetry in S3,
transform/query through AWS analytics services,
and visualize through QuickSight.

## Components

- AWS Lambda
- EventBridge
- S3
- Glue
- Athena
- QuickSight
- Cognito