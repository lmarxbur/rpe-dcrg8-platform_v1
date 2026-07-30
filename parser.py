import re

# Match a 4-digit hexadecimal register anywhere in a line.
REGISTER_RE = re.compile(r'([0-9A-F]{4}H)')

INPUT_FILE = "rawtext.txt"
OUTPUT_FILE = "out_file.txt"

# Read and strip blank lines.
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    lines = [line.strip() for line in f if line.strip()]

records = []

i = 0

while i < len(lines):

    match = REGISTER_RE.search(lines[i])

    if not match:
        i += 1
        continue

    address = match.group(1)

    # Grab the next six lines if available.
    block = lines[i:i + 7]

    if len(block) < 7:
        print(f"Incomplete block at {address}")
        break

    record = {
        "address": address,
        "words": block[1],
        "desc_it": block[2],
        "desc_en": block[3],
        "scale": block[4],
        "format": block[5],
        "bytes": block[6],
    }

    records.append(record)

    i += 7

print(f"\nParsed {len(records)} registers.\n")

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:

    for record in records:

        print(record)
        f.write(str(record) + "\n")