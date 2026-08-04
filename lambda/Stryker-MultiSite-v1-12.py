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

S3_BUCKET = os.getenv("S3_BUCKET", "rpe-dcrg8-data-v1.12")

TARGET_PF = 0.95

MAX_REGISTER_RETRIES = 2

s3_client = boto3.client("s3")


# ================= HELPERS =================

def get_query_addr(logical_addr):
    return (logical_addr - 1) % 65536


def parse_32bit_unsigned(regs):
    return (regs[0] << 16) | regs[1]


def parse_32bit_signed(regs):
    raw = parse_32bit_unsigned(regs)
    return struct.unpack(">i", struct.pack(">I", raw))[0]


def safe_read(read_func):
    """
    Retry a zero-arg function up to MAX_REGISTER_RETRIES
    """

    for _ in range(MAX_REGISTER_RETRIES + 1):
        val = read_func()

        if val is not None:
            return val

        time.sleep(0.1)

    print("[WARN] Persistent Modbus failure")
    return None


# ================= MODBUS READ FUNCTIONS =================

def read_input_32(client, addr, signed=True):

    try:
        rr = client.read_input_registers(
            get_query_addr(addr),
            count=2
        )

        if rr and not rr.isError() and rr.registers:

            if signed:
                return parse_32bit_signed(rr.registers)

            return parse_32bit_unsigned(rr.registers)

    except ModbusException:
        return None

    return None



def read_input_16(client, addr, signed=False):

    try:
        rr = client.read_input_registers(
            get_query_addr(addr),
            count=1
        )

        if rr and not rr.isError() and rr.registers:

            val = rr.registers[0]

            if signed and val >= 32768:
                val -= 65536

            return val

    except ModbusException:
        return None

    return None


def read_holding_32(client, addr, signed=False):

    try:
        rr = client.read_holding_registers(
            get_query_addr(addr),
            count=2
        )

        if rr and not rr.isError() and rr.registers:

            raw = parse_32bit_unsigned(rr.registers)

            if signed:
                return struct.unpack(">i", struct.pack(">I", raw))[0]

            return raw

    except ModbusException:
        return None

    return None


def read_holding_16(client, addr):

    try:
        rr = client.read_holding_registers(
            get_query_addr(addr),
            count=1
        )

        if rr and not rr.isError() and rr.registers:
            return rr.registers[0]

    except ModbusException:
        return None

    return None


# ================= POLLING =================

def poll_device(device):

    client = ModbusTcpClient(
        host=device["ip"],
        port=device["port"],
        timeout=30
    )

    time.sleep(0.2)

    max_retries = 3

    for attempt in range(max_retries):

        try:

            if not client.connect():
                raise ConnectionError("connect failed")

            data = {}

            # ---------- INPUT REGISTERS ----------

            input_regs = {
                "pf_measured": (0, True, 1000),

                "eq_voltage": (6, True, 10),
                "eq_current": (8, True, 1000),

                #"active_power_total": (10, True, 10), 
                #"reactive_power_total": (78, True, 10),
                #updated 2026/07/25:
                #Updated to lovato documented registers after lab validation
                "active_power_total": (5376, True, 1),
                "reactive_power_total": (10, True, 1),
                #Undocumented Register "apparent_power_total": (5384, False, 1),


                "voltage_l1": (64, True, 10),
                "voltage_l2": (66, True, 10),
                "voltage_l3": (68, True, 10),

                "current_l1": (70, True, 1000),
                "current_l2": (72, True, 1000),
                "current_l3": (74, True, 1000),


            }

            for k, (addr, signed, scale) in input_regs.items():

                val = safe_read(
                    lambda addr=addr, signed=signed:
                    read_input_32(client, addr, signed)
                )

                if val is not None:
                    data[k] = val / scale

                time.sleep(0.05)

            # ---------- THD REGISTERS ----------

            thd_regs = {
                "voltage_thd_l1": (11296, False, 10),
                "voltage_thd_l2": (11344, False, 10),
                "voltage_thd_l3": (11392, False, 10),

                "current_thd_l1": (11440, False, 10),
                "current_thd_l2": (11488, False, 10),
                "current_thd_l3": (11536, False, 10),
            }

            for k, (addr, signed, scale) in thd_regs.items():

                val = safe_read(
                    lambda addr=addr, signed=signed:
                    read_input_16(client, addr, signed)
                )

                if val is not None:
                    data[k] = val / scale

                time.sleep(0.05)

            # ---------- HOLDING REGISTERS ----------

            energy_regs = {
                "active_energy_import_kwh": 22,
                "reactive_energy_import_kvarh": 24,
                "apparent_energy_kvah": 26,
                "active_energy_export_kwh": 28,
                "reactive_energy_export_kvarh": 30,
            }

            for k, addr in energy_regs.items():

                val = safe_read(
                    lambda addr=addr:
                    read_holding_32(client, addr)
                )

                if val is not None:
                    data[k] = val / 10.0

                time.sleep(0.05)

            # ---------- FREQUENCY ----------

            freq = safe_read(
                lambda: read_input_32(
                    client,
                    38,
                    signed=False
                )
            )

            if freq is not None:
                data["frequency_hz"] = freq / 100.0

            time.sleep(0.05)

            # ---------- CAP FLAGS ----------

            for i, phase in enumerate(["l1", "l2", "l3"]):

                val = safe_read(
                    lambda i=i:
                    read_holding_16(client, 8194 + i)
                )

                data[f"cap_{phase}"] = val if val is not None else 0

                time.sleep(0.05)

            # ---------- KVAR STEPS ----------

            for phase_index, phase in enumerate(["l1", "l2", "l3"]):

                for step in range(32):

                    addr = 4864 + (phase_index * 64) + (2 * step)

                    val = safe_read(
                        lambda addr=addr:
                        read_holding_32(client, addr)
                    )

                    data[f"{phase}_kvar_step_{step+1}"] = (
                        (val or 0) / 100.0
                    )

                    time.sleep(0.05)

                time.sleep(0.1)

            # ---------- PF CALCULATIONS ----------

            P = data.get("active_power_total", 0.0)

            Q_measured = data.get(
                "reactive_power_total",
                0.0
            )

            data["apparent_power_total"] = round(
                math.sqrt(
                    (P ** 2) + (Q_measured ** 2)
                ),
                3
            )

            data["apparent_power_total"] = round(
                math.sqrt(
                    (P ** 2) + (Q_measured ** 2)
                ),
                3
            )

            Q_cap_total = sum(
                sum(
                    data.get(
                        f"{phase}_kvar_step_{step+1}",
                        0.0
                    )
                    for step in range(32)
                )
                for phase in ["l1", "l2", "l3"]
                if data.get(f"cap_{phase}", 0) == 0
            )

            Q_uncorrected = Q_measured + Q_cap_total

            if P > 100:

                data["pf_uncorrected_calc"] = round(
                    P / math.sqrt(
                        (P ** 2) + (Q_uncorrected ** 2)
                    ),
                    3
                )

                data["pf_corrected_calc"] = round(
                    P / math.sqrt(
                        (P ** 2) + (Q_measured ** 2)
                    ),
                    3
                )

            else:

                data["pf_uncorrected_calc"] = None
                data["pf_corrected_calc"] = None

            data["pf_improvement"] = round(
                data["pf_corrected_calc"]
                - data["pf_uncorrected_calc"],
                3
            )

            data["pf_delta_to_target"] = round(
                data["pf_corrected_calc"]
                - TARGET_PF,
                3
            )



            client.close()

            return data

        except Exception as e:

            print(
                f"[ERROR] "
                f"{device['name']} "
                f"poll failed "
                f"(attempt {attempt+1}/{max_retries}): "
                f"{e}"
            )

            time.sleep(1)

    client.close()

    return None


# ================= S3 INGEST =================

def ingest_to_s3(device, data):
    print("THD DEBUG:")
    for k, v in data.items():
        if "thd" in k.lower():
            print(k, v)
    ts = datetime.utcnow().replace(microsecond=0)
     # Optional metadata for future multi-site support
    if device.get("site_name"):
        data["site_name"] = device["site_name"]


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

    print(
        f"[{device['name']}] "
        f"S3 OK "
        f"({len(data)} fields)"
    )


# ================= LAMBDA HANDLER =================

def lambda_handler(event, context):

    devices = event.get("devices", [])

    if not devices:

        print("[ERROR] No devices specified in event")

        return {
            "status": "error",
            "message": "No devices specified"
        }

    results = []

    for device in devices:

        print(
            f"[INFO] Polling "
            f"{device['name']} "
            f"({device['ip']}:{device['port']})"
        )

        data = poll_device(device)

        if data:

            ingest_to_s3(device, data)

            results.append({
                "device": device["name"],
                "status": "success"
            })

        else:

            results.append({
                "device": device["name"],
                "status": "failed"
            })

    return {
        "results": results
    }
