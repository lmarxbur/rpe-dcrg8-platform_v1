import json
import time
import struct
import math
from datetime import datetime
import os
import sys

from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

import boto3

# ================= CONFIG =================

S3_BUCKET = os.getenv("S3_BUCKET", "rpe-dcrg8-data-v2-firehose-ec2")
MAX_REGISTER_RETRIES = 2
DEVICE_POLL_GAP_SEC = float(os.getenv("DEVICE_POLL_GAP_SEC", "0.35"))
POLL_INTERVAL_SEC = float(os.getenv("POLL_INTERVAL_SEC", "60.0"))  # Time between full polling cycles on EC2

s3_client = boto3.client("s3")
firehose_client = boto3.client("firehose", region_name="us-east-1")
FIREHOSE_STREAM_NAME = "PUT-S3-EC2"


# ================= HELPERS =================

def get_query_addr(logical_addr):
    return (logical_addr - 1) % 65536


def parse_32bit_unsigned(regs):
    return (regs[0] << 16) | regs[1]


def parse_32bit_signed(regs):
    raw = parse_32bit_unsigned(regs)
    return struct.unpack(">i", struct.pack(">I", raw))[0]


# ================= SAFE READ (RETRY ONLY READS) =================

def safe_read(fn):
    for _ in range(MAX_REGISTER_RETRIES + 1):
        try:
            val = fn()
            if val is not None:
                return val
        except Exception:
            pass
        time.sleep(0.05)

    return None


# ================= MODBUS READERS =================

def read_input_32(client, addr, signed=True):
    rr = client.read_input_registers(get_query_addr(addr), count=2)
    if rr and not rr.isError() and rr.registers:
        return parse_32bit_signed(rr.registers) if signed else parse_32bit_unsigned(rr.registers)
    return None


def read_holding_32(client, addr, signed=False):
    rr = client.read_holding_registers(get_query_addr(addr), count=2)
    if rr and not rr.isError() and rr.registers:
        raw = parse_32bit_unsigned(rr.registers)
        return struct.unpack(">i", struct.pack(">I", raw))[0] if signed else raw
    return None


def read_holding_16(client, addr):
    rr = client.read_holding_registers(get_query_addr(addr), count=1)
    if rr and not rr.isError() and rr.registers:
        return rr.registers[0]
    return None


# ================= DEVICE PREFLIGHT =================

def preflight_device(device):
    client = ModbusTcpClient(
        host=device["ip"],
        port=device["port"],
        timeout=5
    )

    try:
        if not client.connect():
            print(f"[PREFLIGHT] {device['name']} UNREACHABLE - connect failed")
            return False

        val = safe_read(lambda: read_input_32(client, 0, signed=True))
        if val is None:
            print(f"[PREFLIGHT] {device['name']} UNREACHABLE - no PF response")
            return False

        print(f"[PREFLIGHT] {device['name']} REACHABLE (pf_measured={val / 1000.0})")
        return True

    except Exception as e:
        print(f"[PREFLIGHT] {device['name']} UNREACHABLE - {e}")
        return False

    finally:
        client.close()


# ================= DEVICE POLL =================

def poll_device(device):
    client = ModbusTcpClient(
        host=device["ip"],
        port=device["port"],
        timeout=10
    )

    data = {}

    try:
        if not client.connect():
            print(f"[ERROR] {device['name']} connect failed")
            return None

        input_regs = {
            "pf_measured": (0, True, 1000),
            "eq_voltage": (6, True, 10),
            "eq_current": (8, True, 1000),
            "active_power_total": (5376, True, 1),
            "reactive_power_total": (10, True, 1),
            "current_l1": (70, True, 1000),
            "current_l2": (72, True, 1000),
            "current_l3": (74, True, 1000),
        }

        for k, (addr, signed, scale) in input_regs.items():
            val = safe_read(lambda: read_input_32(client, addr, signed))
            if val is not None:
                data[k] = val / scale

        energy_regs = {
            "active_energy_import_kwh": 22,
            "reactive_energy_import_kvarh": 24,
            "apparent_energy_kvah": 26,
            "active_energy_export_kwh": 28,
            "reactive_energy_export_kvarh": 30,
        }

        for k, addr in energy_regs.items():
            val = safe_read(lambda: read_holding_32(client, addr))
            if val is not None:
                data[k] = val / 10.0

        for i, phase in enumerate(["l1", "l2", "l3"]):
            val = safe_read(lambda i=i: read_holding_16(client, 8194 + i))
            data[f"cap_{phase}"] = val if val is not None else 0

        for phase_index, phase in enumerate(["l1", "l2", "l3"]):
            for step in range(6):
                addr = 4864 + (phase_index * 64) + (2 * step)
                val = safe_read(lambda addr=addr: read_holding_32(client, addr))
                data[f"{phase}_kvar_step_{step+1}"] = (val or 0) / 100.0

            time.sleep(0.05)

        # DERIVED VALUES
        P = data.get("active_power_total", 0.0)
        Q = data.get("reactive_power_total", 0.0)
        pf_measured = data.get("pf_measured")

        Q_cap_total = sum(
            sum(data.get(f"{phase}_kvar_step_{step+1}", 0.0) for step in range(6))
            for phase in ["l1", "l2", "l3"]
            if data.get(f"cap_{phase}", 0) == 0
        )
        
        Q_uncorrected = Q + Q_cap_total

        if P > 100 and pf_measured is not None:
            pf_uncorrected = P / math.sqrt(P**2 + Q_uncorrected**2)
            pf_corrected = P / math.sqrt(P**2 + Q**2)

            data["pf_uncorrected_calc"] = round(pf_uncorrected, 3)
            data["pf_corrected_calc"] = round(pf_corrected, 3)
            data["pf_improvement"] = round(pf_measured - pf_uncorrected, 3)
        else:
            data["pf_uncorrected_calc"] = None
            data["pf_corrected_calc"] = None
            data["pf_improvement"] = None

        return data

    except Exception as e:
        print(f"[ERROR] {device['name']} poll failed: {e}")
        return None

    finally:
        client.close()


# ================= FIREHOSE INGEST =================

def ingest_to_firehose(device, data):
    ts = datetime.utcnow().replace(microsecond=0)

    record = {
        "device": device["name"],
        "site_name": device.get("site_name"),
        "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
        "hour_bucket": ts.strftime("%Y-%m-%d %H:00:00"),
        "day_bucket": ts.strftime("%Y-%m-%d"),
        "week_bucket": ts.strftime("%Y-%W"),
        "month_bucket": ts.strftime("%Y-%m"),
        **data
    }

    firehose_client.put_record(
        DeliveryStreamName=FIREHOSE_STREAM_NAME,
        Record={
            "Data": (json.dumps(record) + "\n").encode("utf-8")
        }
    )

    print(f"[{device['name']}] FIREHOSE OK")


# ================= EXECUTION RUNLOOP =================

def run_polling_cycle(devices):
    print(f"\n[INFO] Starting polling cycle at {datetime.utcnow().isoformat()}")
    reachable_devices = []

    # PREFLIGHT
    print("[INFO] Starting device preflight")
    MAX_PREFLIGHT_ATTEMPTS = 3
    retry_interval = 10

    for attempt in range(1, MAX_PREFLIGHT_ATTEMPTS + 1):
        all_reachable = True
        for device in devices:
            if not preflight_device(device):
                all_reachable = False

        if all_reachable:
            reachable_devices = list(devices)
            print(f"[INFO] Preflight complete: {len(devices)}/{len(devices)} devices reachable")
            break

        if attempt < MAX_PREFLIGHT_ATTEMPTS:
            time.sleep(retry_interval)
    else:
        print("[ERROR] Preflight failed. Skipping poll cycle.")
        return

    # FULL POLL
    for device in reachable_devices:
        print(f"[INFO] Polling {device['name']}")
        data = poll_device(device)

        if data:
            ingest_to_firehose(device, data)
        
        time.sleep(DEVICE_POLL_GAP_SEC)


if __name__ == "__main__":
    # Define your devices directly here or load them from a local configuration file/env variable
    # Example target configuration for your Modbus TCP devices (MCC-1 through MCC-8 etc.):
    devices_config = [
        {"name": "MCC-1", "ip": "10.41.34.140", "port": 502, "site_name": "Stryker Mahwah"},
        {"name": "MCC-2", "ip": "10.41.34.141", "port": 502, "site_name": "Stryker Mahwah"},
        # Add remaining MCC nodes as needed...
    ]

    # If you want to run it continuously as a daemon service on EC2:
    print("[INFO] Starting Modbus Polling Daemon on EC2...")
    try:
        while True:
            run_polling_cycle(devices_config)
            time.sleep(POLL_INTERVAL_SEC)
    except KeyboardInterrupt:
        print("[INFO] Polling daemon stopped by user.")
        sys.exit(0)