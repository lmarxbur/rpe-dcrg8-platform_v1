from pathlib import Path

root = Path("E:/json-edit")

bad = []

for file in root.rglob("*.json"):
    rel = file.relative_to(root)
    parts = rel.parts

    # Unit-X / YYYY / MM / DD / HH / MM / SS.json
    if len(parts) != 7:
        bad.append((file, f"depth={len(parts)}"))
        continue

    try:
        year   = int(parts[1])
        month  = int(parts[2])
        day    = int(parts[3])
        hour   = int(parts[4])
        minute = int(parts[5])

        if not (1 <= month <= 12):
            bad.append((file, f"bad month={month}"))
        elif not (1 <= day <= 31):
            bad.append((file, f"bad day={day}"))
        elif not (0 <= hour <= 23):
            bad.append((file, f"bad hour={hour}"))
        elif not (0 <= minute <= 59):
            bad.append((file, f"bad minute={minute}"))

    except ValueError:
        bad.append((file, "non-numeric date/time path"))

print(f"Bad paths: {len(bad)}")

for file, reason in bad[:100]:
    print(reason, file)