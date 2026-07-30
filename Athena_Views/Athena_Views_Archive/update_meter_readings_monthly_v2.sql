CREATE OR REPLACE VIEW "update_meter_readings_monthly_v2" AS 
SELECT
  device_name
, month
, month_label
, MIN(active_energy_import_kwh) start_kwh
, MAX(active_energy_import_kwh) end_kwh
, (MAX(active_energy_import_kwh) - MIN(active_energy_import_kwh)) usage_kwh
, AVG(active_power_total) kw_avg
, MAX(active_power_total) kw_peak
, AVG(pf_measured) pf_measured
, AVG(pf_uncorrected_calc) pf_uncorrected
, (AVG(active_power_total) / NULLIF(AVG(pf_measured), 0)) kva_measured
, (AVG(active_power_total) / NULLIF(AVG(pf_uncorrected_calc), 0)) kva_baseline
, ((AVG(active_power_total) / NULLIF(AVG(pf_uncorrected_calc), 0)) - (AVG(active_power_total) / NULLIF(AVG(pf_measured), 0))) delta_kva
FROM
  update_meter_readings_clean_v
GROUP BY 1, 2, 3
