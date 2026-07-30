CREATE OR REPLACE VIEW "update_meter_readings_clean_v" AS 
SELECT
  replace(device, 'Unit-', 'MCC-') device_name
, date_trunc('month', date_parse(timestamp, '%Y-%m-%d %H:%i:%s')) month
, date_format(date_trunc('month', date_parse(timestamp, '%Y-%m-%d %H:%i:%s')), '%Y-%m') month_label
, active_power_total
, reactive_power_total
, active_energy_import_kwh
, reactive_energy_import_kvarh
, pf_measured
, pf_uncorrected_calc
FROM
  stryker_meter_data_devices