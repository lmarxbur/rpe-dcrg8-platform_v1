from pathlib import Path
import json
from collections import Counter, defaultdict

root = Path("E:/json-save")

schemas = Counter()
examples = {}

for file in root.rglob("*.json"):
    try:
        with file.open("r", encoding="utf-8") as f:
            data = json.load(f)

        # Key names define the schema signature
        signature = tuple(sorted(data.keys()))

        schemas[signature] += 1

        if signature not in examples:
            examples[signature] = file

    except Exception as e:
        print(f"ERROR: {file}: {e}")

print(f"\nUnique JSON schemas: {len(schemas)}")

for i, (signature, count) in enumerate(
    schemas.most_common(), start=1
):
    print(f"\nSCHEMA {i}")
    print(f"Files:   {count}")
    print(f"Example: {examples[signature]}")
    print(f"Columns: {len(signature)}")