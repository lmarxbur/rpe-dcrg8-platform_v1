import json
import time
import struct
import math
from datetime import datetime
import socket

from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

import boto3
import os

# ================= CONFIG =================

S3_BUCKET = os.getenv("S3_BUCKET", "rpe-dcrg8-data-v2")

MAX_REGISTER_RETRIES = 2
DEVICE_POLL_GAP_SEC = float(os.getenv("DEVICE_POLL_GAP_SEC", "0.35"))
CONNECT_TIMEOUT = float(os.getenv("CONNECT_TIMEOUT", "5.0"))

s3_client = boto3.client("s3")
firehose_client = boto3.client("firehose", region_name="us-east-1")
FIREHOSE_STREAM_NAME = "PUT-S3-DCRG8-Data"


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


# ================= DEVICE HEALTH CHECK (TCP + MODBUS) =================

def check_device_health(device):
    ip = device["ip"]
    port = device["port"]
    name = device["name"]

    health_status = {
        "device": name,
        "ip": ip,
        "port": port,
        "tcp_passed": False,
        "modbus_passed": False,
        "failure_state": "unknown",
        "connect_time_sec": None
    }

    # ---------------- 1. RAW TCP SOCKET CHECK ----------------
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(CONNECT_TIMEOUT)

    try:
        t0 = time.time()
        sock.connect((ip, port))
        elapsed = round(time.time() - t0, 3)
        
        health_status["tcp_passed"] = True
        health_status["connect_time_sec"] = elapsed
    except Exception as e:
        health_status["tcp_passed"] = False
        health_status["failure_state"] = "tcp_failed"
        print(f"[ERROR] {name} TCP connection failed: {e}")
        return health_status
    finally:
        sock.close()

    # ---------------- 2. MODBUS APPLICATION CHECK ----------------
    client = ModbusTcpClient(
        host=ip,
        port=port,
        timeout=5
    )

    try:
        if not client.connect():
            health_status["modbus_passed"] = False
            health_status["failure_state"] = "modbus_connect_failed"
            print(f"[ERROR] {name} TCP passed, but Modbus client connect failed")
            return health_status

        # Read known-good register (e.g., PF measured at addr 0)
        val = safe_read(lambda: read_input_32(client, 0, signed=True))

        if val is None:
            health_status["modbus_passed"] = False
            health_status["failure_state"] = "modbus_read_failed"
            print(f"[ERROR] {name} TCP passed, but Modbus register read returned None")
            return health_status

        # If both succeeded
        health_status["modbus_passed"] = True
        health_status["failure_state"] = "healthy"
        print(f"[SUCCESS] {name} TCP + Modbus passed (pf_measured={val / 1000.0})")
        return health_status

    except Exception as e:
        health_status["modbus_passed"] = False
        health_status["failure_state"] = "modbus_exception"
        print(f"[ERROR] {name} Modbus check threw exception: {e}")
        return health_status

    finally:
        client.close()


# ================= LAMBDA HANDLER =================

def lambda_handler(event, context):
    devices = event.get("devices", [])

    if not devices:
        return {"status": "error", "message": "No devices provided"}

    print("[INFO] Starting device diagnostic health checks...")

    diagnostic_results = []
    healthy_count = 0

    for device in devices:
        result = check_device_health(device)
        diagnostic_results.append(result)
        
        if result["failure_state"] == "healthy":
            healthy_count += 1

    # Structured summary for CloudWatch log ingestion / metric extraction
    summary = {
        "timestamp": datetime.utcnow().isoformat(),
        "total_devices": len(devices),
        "healthy_count": healthy_count,
        "results": diagnostic_results
    }

    print(json.dumps(summary))

    return {
        "status": "success",
        "summary": summary
    }