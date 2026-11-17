"""Materialize clean Better Vanilla payload files from the original pinned ZIP."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import zipfile

SOURCE = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    lock = json.loads((SOURCE / "upstream-lock.json").read_bytes())
    support = json.loads((SOURCE / "tools/distribution-support-lock.json").read_bytes())
    with args.original.open("rb") as stream:
        if hashlib.file_digest(stream, "sha256").hexdigest() != lock["inputArchive"]["sha256"]:
            raise ValueError("The original archive SHA-256 differs from the source lock")
    rows = [row for row in lock["inputFiles"] if row["path"].startswith("mods/")]
    with zipfile.ZipFile(args.original) as archive:
        payload = {row["path"]: archive.read("Better Vanilla/" + row["path"]) for row in rows}
    source_rows = lock["requestedShaders"] + support["files"]
    for row in source_rows:
        payload[row["path"]] = (SOURCE / row["path"]).read_bytes()
    for row in rows + source_rows:
        path = Path(row["path"])
        data = payload[row["path"]]
        if (path.is_absolute() or ".." in path.parts or len(data) != row["sizeBytes"] or
                hashlib.sha256(data).hexdigest() != row["sha256"]):
            raise ValueError(f"Changed delivery input: {path}")
    args.out.mkdir()
    for name, data in payload.items():
        file = args.out / name
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(data)


if __name__ == "__main__":
    main()
