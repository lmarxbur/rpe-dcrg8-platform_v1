from pathlib import Path
import json

source = Path("E:/json-edit/Unit-5a")
save_root = Path("E:/json-save/MCC-5a")
v2_ref_file = Path("E:/json-edit/v2_ref.json")

# Load canonical V2 schema
with v2_ref_file.open("r", encoding="utf-8") as f:
    v2_ref = json.load(f)

v2_keys = list(v2_ref.keys())

print(f"V2 reference columns: {len(v2_keys)}")

count = 0

for file in source.rglob("*.json"):

    # Preserve existing YYYY/MM/DD/HH/MM/SS.json structure
    relative_path = file.relative_to(source)
    output_file = save_root / relative_path

    # Read V1 JSON
    with file.open("r", encoding="utf-8") as f:
        old_data = json.load(f)

    # Build a NEW record containing EXACTLY the V2 fields.
    # Existing V1 values are retained where the field exists.
    # V2 fields absent from V1 become null.
    data = {
        key: old_data.get(key)
        for key in v2_keys
    }

    # V1 -> V2 identity changes
    data["device"] = "MCC-5a"
    data["site_name"] = "Stryker_Mahwah_NJ"

    # Create matching output directories
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Write normalized V2 JSON
    with output_file.open("w", encoding="utf-8") as f:
        json.dump(data, f)

    count += 1

print(f"Converted JSON files: {count}")