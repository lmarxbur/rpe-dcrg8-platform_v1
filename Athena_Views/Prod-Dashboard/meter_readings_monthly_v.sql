CREATE OR REPLACE VIEW "meter_readings_monthly_v" AS 
SELECT
  replace(device, 'Unit-', 'MCC-') device_name
, CAST(date_trunc('month', date_parse(timestamp, '%Y-%m-%d %H:%i:%s')) AS DATE) month
, date_format(date_trunc('month', date_parse(timestamp, '%Y-%m-%d %H:%i:%s')), '%Y-%m') month_label
, MIN(active_energy_import_kwh) start_kwh
, MAX(active_energy_import_kwh) end_kwh
, (MAX(active_energy_import_kwh) - MIN(active_energy_import_kwh)) usage_kwh
, AVG(active_power_total) kw_avg
, MAX(active_power_total) kw_peak
, AVG(pf_measured) pf_measured_avg
, AVG(pf_uncorrected_calc) pf_uncorrected_avg
FROM
  stryker_meter_data_devices
GROUP BY replace(device, 'Unit-', 'MCC-'), date_trunc('month', date_parse(timestamp, '%Y-%m-%d %H:%i:%s'))
