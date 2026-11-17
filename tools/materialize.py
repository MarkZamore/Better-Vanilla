"""Materialize clean Better Vanilla payload files from the original pinned ZIP."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen
import zipfile

SOURCE = Path(__file__).resolve().parents[1]


def mod_inputs() -> tuple[list[dict], list[dict]]:
    upstream = json.loads((SOURCE / "upstream-lock.json").read_bytes())
    overlay = json.loads((SOURCE / "tools/mod-overlay-lock.json").read_bytes())
    originals = {row["path"]: row for row in upstream["inputFiles"] if row["path"].startswith("mods/")}
    for row in overlay["remove"]:
        path = row["path"]
        if path not in originals or originals[path]["sha256"] != row["sha256"]:
            raise ValueError(f"Excluded author JAR changed: {path}")
        del originals[path]
    added = overlay["add"]
    seen = set(originals)
    for row in added:
        path = Path(row["path"])
        if path.parent != Path("mods") or path.suffix != ".jar" or row["path"] in seen:
            raise ValueError(f"Invalid added JAR path: {path}")
        seen.add(row["path"])
    return list(originals.values()), added


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
    rows, added = mod_inputs()
    with zipfile.ZipFile(args.original) as archive:
        payload = {row["path"]: archive.read("Better Vanilla/" + row["path"]) for row in rows}
    source_rows = lock["requestedShaders"] + support["files"]
    for row in source_rows:
        payload[row["path"]] = (SOURCE / row["path"]).read_bytes()
    for row in added:
        request = Request(row["downloadUrl"], headers={"User-Agent": "Better-Vanilla/1.0 (MarkZamore)"})
        with urlopen(request, timeout=60) as response:
            data = response.read(row.get("upstreamSizeBytes", row["sizeBytes"]) + 1)
            if patch := row.get("patch"):
                if patch != "restore-mojang-logo-v1":
                    raise ValueError(f"Unknown pack patch: {patch}")
                import intro_logo_patch
                data = intro_logo_patch.apply(data)
            payload[row["path"]] = data
    for row in rows + source_rows + added:
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
