"""Phase 109A — Release package validator.

校验 checksums_v5_0.sha256 清单中列出的每个文件存在且哈希一致。
仅本地只读校验：零网络、不修改任何文件、不执行被校验文件。
"""
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def compute_sha256(filepath):
    hash_sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


def load_checksum_entries(checksums_path):
    entries = []
    with open(checksums_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = re.split(r"\s+", line, maxsplit=1)
            if len(parts) != 2:
                continue
            expected_hash, rel_path = parts[0], parts[1]
            entries.append((expected_hash, rel_path))
    return entries


def main() -> int:
    checksums_path = ROOT / "checksums_v5_0.sha256"
    if not checksums_path.exists():
        print("[FAIL] checksums_v5_0.sha256 not found", file=sys.stderr)
        return 1

    entries = load_checksum_entries(checksums_path)
    if len(entries) < 10:
        print(f"[FAIL] checksum entries too few: {len(entries)}", file=sys.stderr)
        return 1

    failures = []
    for expected_hash, rel_path in entries:
        target = ROOT / rel_path
        if not target.exists():
            failures.append(f"missing file: {rel_path}")
            continue
        actual = compute_sha256(target)
        if actual != expected_hash:
            failures.append(f"hash mismatch: {rel_path}")

    if failures:
        for msg in failures:
            print(f"[FAIL] {msg}", file=sys.stderr)
        print(f"Validator Summary: {len(entries) - len(failures)}/{len(entries)} checks passed")
        return 1

    print(f"Validator Summary: {len(entries)}/{len(entries)} checks passed")
    print("release package integrity: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
