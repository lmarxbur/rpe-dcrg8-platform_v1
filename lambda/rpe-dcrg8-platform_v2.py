import json
import time
import json
import struct
import math
from datetime import datetime

from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

import boto3
import os

# ================= CONFIG =================

S3_BUCKET = os.getenv("S3_BUCKET", "rpe-dcrg8-data")

MAX_REGISTER_RETRIES = 2
DEVICE_POLL_GAP_SEC = float(os.getenv("DEVICE_POLL_GAP_SEC", "0.35"))

s3_client = boto3.client("s3")


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

        # ---------------- INPUT REGISTERS ----------------

        input_regs = {
            "pf_measured": (0, True, 1000),
            "eq_voltage": (6, True, 10),
            "eq_current": (8, True, 1000),
            "active_power_total": (10, True, 10),
            "reactive_power_total": (78, True, 10),

            "voltage_l1": (64, True, 10),
            "voltage_l2": (66, True, 10),
            "voltage_l3": (68, True, 10),

            "current_l1": (70, True, 1000),
            "current_l2": (72, True, 1000),
            "current_l3": (74, True, 1000),
        }

        for k, (addr, signed, scale) in input_regs.items():
            val = safe_read(lambda: read_input_32(client, addr, signed))
            if val is not None:
                data[k] = val / scale

        # ---------------- ENERGY REGISTERS ----------------

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

        # ---------------- FREQUENCY ----------------

        freq = safe_read(lambda: read_input_32(client, 38, signed=False))
        if freq is not None:
            data["frequency_hz"] = freq / 100.0

        # ---------------- CAP FLAGS ----------------

        for i, phase in enumerate(["l1", "l2", "l3"]):
            val = safe_read(lambda i=i: read_holding_16(client, 8194 + i))
            data[f"cap_{phase}"] = val if val is not None else 0

        # ---------------- KVAR STEPS ----------------

        for phase_index, phase in enumerate(["l1", "l2", "l3"]):
            for step in range(32):
                addr = 4864 + (phase_index * 64) + (2 * step)

                val = safe_read(lambda addr=addr: read_holding_32(client, addr))
                data[f"{phase}_kvar_step_{step+1}"] = (val or 0) / 100.0

            time.sleep(0.05)

        # ---------------- DERIVED VALUES ----------------

        P = data.get("active_power_total", 0.0)
        Q = data.get("reactive_power_total", 0.0)

        Q_cap_total = sum(
            sum(data.get(f"{phase}_kvar_step_{step+1}", 0.0) for step in range(32))
            for phase in ["l1", "l2", "l3"]
            if data.get(f"cap_{phase}", 0) == 0
        )

        Q_uncorrected = Q + Q_cap_total

        if P > 100:
            pf_uncorrected = P / math.sqrt(P**2 + Q_uncorrected**2)
            pf_corrected = P / math.sqrt(P**2 + Q**2)

            data["pf_uncorrected_calc"] = round(pf_uncorrected, 3)
            data["pf_corrected_calc"] = round(pf_corrected, 3)
            data["pf_improvement"] = round(pf_corrected - pf_uncorrected, 3)
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


# ================= S3 INGEST =================

def ingest_to_s3(device, data):

    ts = datetime.utcnow().replace(microsecond=0)

    record = {
        "device": device["name"],
        "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),

        "hour_bucket": ts.strftime("%Y-%m-%d %H:00:00"),
        "day_bucket": ts.strftime("%Y-%m-%d"),
        "week_bucket": ts.strftime("%Y-%W"),
        "month_bucket": ts.strftime("%Y-%m"),

        **data
    }

    key = (
        f"stryker/devices/"
        f"{device['name']}/"
        f"{ts.strftime('%Y/%m/%d/%H/%M/%S')}.json"
    )

    s3_client.put_object(
        Bucket=S3_BUCKET,
        Key=key,
        Body=json.dumps(record)
    )

    print(f"[{device['name']}] S3 OK")


# ================= LAMBDA HANDLER =================

def lambda_handler(event, context):

    devices = event.get("devices", [])

    if not devices:
        return {"status": "error", "message": "No devices provided"}

    results = []

    for device in devices:

        print(f"[INFO] Polling {device['name']}")

        data = poll_device(device)

        if data:
            ingest_to_s3(device, data)
            results.append({"device": device["name"], "status": "success"})
        else:
            results.append({"device": device["name"], "status": "failed"})

        # 🔥 CRITICAL: pacing between devices
        time.sleep(DEVICE_POLL_GAP_SEC)

    return {"results": results}