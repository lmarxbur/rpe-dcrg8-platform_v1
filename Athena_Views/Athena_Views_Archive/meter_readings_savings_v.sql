CREATE OR REPLACE VIEW "meter_readings_savings_v" AS 
SELECT
  device_name
, month
, month_label
, kw_peak
, kva_baseline
, kva_measured
, delta_kva
, 20 demand_rate_per_kva
, (delta_kva * 20) estimated_demand_savings
FROM
  update_meter_readings_monthly_v2