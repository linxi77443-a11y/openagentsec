#!/usr/bin/env python3
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKSUM_FILE = ROOT / "checksums_v5_2.sha256"

def regen():
    if not CHECKSUM_FILE.exists():
        print(f"File not found: {CHECKSUM_FILE}")
        return

    lines = CHECKSUM_FILE.read_text().splitlines()
    new_lines = []
    count = 0
    for line in lines:
        if not line.strip():
            continue
        parts = line.split("  ", 1)
        if len(parts) == 2:
            old_hash, rel_path = parts
            file_path = ROOT / rel_path
            if file_path.exists():
                hasher = hashlib.sha256()
                with open(file_path, 'rb') as f:
                    while chunk := f.read(8192):
                        hasher.update(chunk)
                new_hash = hasher.hexdigest()
                new_lines.append(f"{new_hash}  {rel_path}")
                count += 1
            else:
                print(f"Warning: File missing: {rel_path}, keeping old hash")
                new_lines.append(line)
        else:
            new_lines.append(line)
            
    CHECKSUM_FILE.write_text("\n".join(new_lines) + "\n")
    print(f"Regenerated checksums for {count} entries.")

if __name__ == "__main__":
    regen()
