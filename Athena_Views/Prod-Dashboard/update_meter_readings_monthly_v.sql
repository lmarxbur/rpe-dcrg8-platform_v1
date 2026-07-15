CREATE OR REPLACE VIEW "update_meter_readings_monthly_v" AS 
SELECT
  device_name
, month
, month_label
, MIN(active_energy_import_kwh) start_kwh
, MAX(active_energy_import_kwh) end_kwh
, (MAX(active_energy_import_kwh) - MIN(active_energy_import_kwh)) usage_kwh
, AVG(active_power_total) kw_avg
, MAX(active_power_total) kw_peak
, AVG(pf_measured) pf_measured_avg
, AVG(pf_uncorrected_calc) pf_uncorrected_avg
, AVG((active_power_total / NULLIF(pf_measured, 0))) kva_measured_rowavg
, AVG((active_power_total / NULLIF(pf_uncorrected_calc, 0))) kva_baseline_rowavg
, (SUM(active_power_total) / NULLIF(SUM((active_power_total / NULLIF(pf_measured, 0))), 0)) pf_measured_weighted
, (SUM(active_power_total) / NULLIF(SUM((active_power_total / NULLIF(pf_uncorrected_calc, 0))), 0)) pf_uncorrected_weighted
, (SUM((active_power_total / NULLIF(pf_uncorrected_calc, 0))) - SUM((active_power_total / NULLIF(pf_measured, 0)))) delta_kva_weighted
, (CASE WHEN (AVG(pf_measured) > 9.8E-1) THEN 'excellent' WHEN (AVG(pf_measured) > 9E-1) THEN 'good' WHEN (AVG(pf_measured) > 7.5E-1) THEN 'poor' ELSE 'critical' END) pf_health_band
FROM
  update_meter_readings_clean_v
GROUP BY 1, 2, 3
