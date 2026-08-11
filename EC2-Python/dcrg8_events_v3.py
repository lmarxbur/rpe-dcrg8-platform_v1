#dcrg8_events_v3.py EC2 events ingester
import os
import json
import time
import argparse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException
import boto3
import struct
import pyarrow as pa
import pyarrow.parquet as pq

# ================= CONFIG =================
S3_BUCKET = os.getenv("S3_BUCKET", "rpe-dcrg8-data-v2")
MAX_REGISTER_RETRIES = int(os.getenv("MAX_REGISTER_RETRIES", "2"))
MAX_THREADS = int(os.getenv("MAX_THREADS", "5"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "25"))
EVENT_SLOT_COUNT = int(os.getenv("EVENT_SLOT_COUNT", "250"))
EVENT_SELECT_DELAY = float(os.getenv("EVENT_SELECT_DELAY", "0.05"))
EVENT_SLOT_START = int(os.getenv("EVENT_SLOT_START", "0"))

s3 = boto3.client("s3")

# ================= LOAD DEVICES =================
DEVICES_FILE = os.getenv("DEVICES_FILE", "/home/ec2-user/modbus.json")


def load_devices(device_filter=None):
    with open(DEVICES_FILE) as f:
        devices = json.load(f)["devices"]
    if device_filter:
        devices = [d for d in devices if d["name"] == device_filter]
    return devices


# ================= HELPER FUNCTIONS =================
def log(level, msg, **kwargs):
    print(json.dumps({"level": level, "msg": msg, "time": datetime.utcnow().isoformat(), **kwargs}))


def get_query_addr(logical_addr):
    return (logical_addr - 1) % 65536


def safe_read(func):
    for _ in range(MAX_REGISTER_RETRIES + 1):
        val = func()
        if val is not None:
            return val
        time.sleep(0.1)
    return None


# ================= MODBUS FUNCTIONS =================
def read_input_16(client, addr):
    try:
        rr = client.read_input_registers(get_query_addr(addr), count=1)
        if rr and rr.registers:
            return rr.registers[0]
    except ModbusException:
        return None
    return None


def write_register_16(client, addr, value):
    try:
        rr = client.write_register(get_query_addr(addr), value)
        if rr and not rr.isError():
            return True
    except ModbusException:
        return False
    return False


def read_event_text(client, addr=0x5032):
    try:
        rr = client.read_input_registers(get_query_addr(addr), count=43)
        if rr and rr.registers:
            return rr.registers
    except ModbusException:
        return None
    return None


def decode_event(registers):
    raw = bytearray()
    for r in registers:
        raw.append((r >> 8) & 0xFF)
        raw.append(r & 0xFF)

    text = raw.decode("ascii", errors="ignore").strip()
    text = text.rstrip("\x00").strip()
    parts = text.split(";")

    if len(parts) >= 3:
        event_text = parts[2].strip()
        if "," in event_text:
            code, description = event_text.split(",", 1)
        else:
            code = None
            description = event_text

        return {
            "event_date": parts[0].strip(),
            "event_time": parts[1].strip(),
            "event_code": code.strip() if code else None,
            "event_text": description.strip(),
            "event_valid": True,
        }

    return {
        "event_text_raw": text,
        "event_valid": False,
    }


def read_all_events(client, event_counter=None, max_slots=None, include_empty=False):
    """Select each event slot via 0x5030, then read text from 0x5032."""
    slot_count = max_slots if max_slots is not None else EVENT_SLOT_COUNT
    events = []

    for slot in range(EVENT_SLOT_START, EVENT_SLOT_START + slot_count):
        select_value = slot
        if event_counter is not None:
            select_value = ((event_counter & 0xFF) << 8) | (slot & 0xFF)

        ok = write_register_16(client, 0x5030, select_value)
        if not ok:
            log("WARN", "event_select_failed", slot=slot)
            continue

        time.sleep(EVENT_SELECT_DELAY)

        regs = read_event_text(client)
        if not regs:
            continue

        event = decode_event(regs)
        event["event_slot"] = slot

        if not include_empty:
            if not event.get("event_valid"):
                continue
            if not event.get("event_date") and not event.get("event_text"):
                continue

        events.append(event)

    return events


# ================= POLLING =================
def poll_device(device, max_slots=None, include_empty=False):
    client = ModbusTcpClient(host=device["ip"], port=device["port"], timeout=10)

    try:
        if not client.connect():
            raise ConnectionError("connect failed")

        data = {}

        # 5030H Event Pointer / Event Counter (Function 04)
        # MSB = event counter, LSB = pointer to last stored event
        event_reg = safe_read(lambda: read_input_16(client, 0x5030))

        if event_reg is not None:
            data["event_raw"] = event_reg
            data["event_counter"] = (event_reg >> 8) & 0xFF
            data["event_pointer"] = event_reg & 0xFF

            events = read_all_events(
                client,
                event_counter=data["event_counter"],
                max_slots=max_slots,
                include_empty=include_empty,
            )
            data["events"] = events
            data["event_count_read"] = len(events)

        return data

    except Exception as e:
        log("ERROR", "event_poll_failed", device=device["name"], err=str(e))
        return None

    finally:
        client.close()


# ================= S3 INGEST =================
def write_s3(records):
    if not records:
        return

    ts = datetime.utcnow()
    by_device = {}
    for r in records:
        by_device.setdefault(r["device"], []).append(r)

    for device, dev_records in by_device.items():
        partition = (
            f"year={ts.year}/month={ts.month:02d}/day={ts.day:02d}/hour={ts.hour:02d}/"
        )
        table = pa.Table.from_pylist(dev_records)
        buf = pa.BufferOutputStream()
        pq.write_table(table, buf, compression="snappy")

        key = f"dcrg8-events/{partition}{int(time.time() * 1000)}.parquet"

        s3.put_object(
            Bucket=S3_BUCKET,
            Key=key,
            Body=buf.getvalue().to_pybytes(),
        )

        log("INFO", "batch_written", device=device, records=len(dev_records), key=key)


# ================= MAIN =================
def main():
    parser = argparse.ArgumentParser(description="Poll DCR-G8 event log slots via Modbus")
    parser.add_argument(
        "--device",
        help="Poll only this device name (must match modbus.json)",
    )
    parser.add_argument(
        "--max-slots",
        type=int,
        help=f"Limit slots read per device (default: all {EVENT_SLOT_COUNT})",
    )
    parser.add_argument(
        "--include-empty",
        action="store_true",
        help="Include invalid/empty slots in output",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Poll and print summary without writing to S3",
    )
    args = parser.parse_args()

    devices = load_devices(device_filter=args.device)
    if not devices:
        log("ERROR", "no_devices_found", filter=args.device)
        return

    log(
        "INFO",
        "poll_start",
        devices=len(devices),
        max_slots=args.max_slots or EVENT_SLOT_COUNT,
        dry_run=args.dry_run,
    )

    results = []
    batch = []

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as exe:
        futures = {
            exe.submit(
                poll_device,
                d,
                max_slots=args.max_slots,
                include_empty=args.include_empty,
            ): d
            for d in devices
        }

        for f in as_completed(futures):
            device = futures[f]
            data = f.result()

            if not data:
                results.append({"device": device["name"], "status": "failed"})
                continue

            ts = datetime.utcnow()
            base = {
                "device": device["name"],
                "timestamp": ts.isoformat(),
                "epoch": int(ts.timestamp()),
                "event_counter": data.get("event_counter"),
                "event_pointer": data.get("event_pointer"),
            }

            events = data.get("events", [])
            if not events:
                results.append({"device": device["name"], "status": "ok", "events": 0})
                continue

            for ev in events:
                batch.append({**base, **ev})

            results.append({
                "device": device["name"],
                "status": "ok",
                "events": len(events),
                "event_counter": data.get("event_counter"),
                "event_pointer": data.get("event_pointer"),
            })

            if not args.dry_run and len(batch) >= BATCH_SIZE:
                write_s3(batch)
                batch = []

    if not args.dry_run and batch:
        write_s3(batch)

    print(json.dumps({"results": results}, indent=2))


if __name__ == "__main__":
    main()
