"""Record Fabric's actual resolved mod IDs against the exact archive inputs."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
PLATFORM_IDS = {"fabricloader", "minecraft", "java", "mixinextras"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", required=True, type=Path)
    parser.add_argument("--pack", required=True, type=Path)
    parser.add_argument("--launcher", required=True, type=Path)
    args = parser.parse_args()
    sys.path.insert(0, str(args.launcher.resolve() / "tools"))
    from pack_library import read_mods

    descriptor = json.loads((ROOT / "portable-pack.json").read_bytes())
    rows = json.loads((ROOT / "upstream-lock.json").read_bytes())["inputFiles"]
    by_id, digests = {}, {}
    for row in (r for r in rows if r["path"].startswith("mods/")):
        source = args.pack / row["path"]
        blob = source.read_bytes()
        digest = hashlib.sha256(blob).hexdigest()
        if digest != row["sha256"]:
            raise ValueError(f"Source differs from lock: {source.name}")
        digests[row["path"]] = digest
        for mod in read_mods(blob, source.name, loader="fabric"):
            if mod["isLoadedMod"]:
                by_id.setdefault(mod["id"], mod)
    lines = args.log.read_text(encoding="utf-8", errors="replace").splitlines()
    header = next(i for i, line in enumerate(lines) if re.search(r"Loading \d+ mods:", line))
    expected = int(re.search(r"Loading (\d+) mods:", lines[header])[1])
    observed_versions, loaded = {}, {}
    for line in lines[header + 1:]:
        match = re.match(r"^[\s|]*(?:\|--|\\--|-)\s+([a-z0-9_.-]+)\s+(\S.*)$", line)
        if not match:
            break
        identifier, version = match.groups()
        if observed_versions.setdefault(identifier, version) != version:
            raise ValueError(f"Conflicting Fabric versions for {identifier}")
        if identifier not in by_id and identifier in PLATFORM_IDS:
            continue
        current = by_id.get(identifier)
        if current is None:
            raise ValueError(f"Unbound runtime mod: {identifier}")
        loaded[identifier] = {"id": identifier, "name": current["name"], "version": version}
    if len(observed_versions) != expected:
        raise ValueError(f"Incomplete Fabric inventory: {len(observed_versions)}/{expected}")
    snapshot = {
        "schemaVersion": 1, "minecraftVersion": descriptor["minecraftVersion"],
        "loader": descriptor["loader"], "sourceJars": digests,
        "mods": sorted(loaded.values(), key=lambda item: item["id"]),
    }
    (ROOT / "library/loaded-mods.json").write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"{len(loaded)} loaded pack mods from {len(digests)} exact source JARs")


if __name__ == "__main__":
    main()
