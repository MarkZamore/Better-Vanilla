"""Stage and verify the locked Better Vanilla delivery."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import zipfile

import multiplayer_warning_policy
import network_logging_policy

SOURCE = Path(__file__).resolve().parents[1]


def fingerprint(path: Path) -> dict:
    with path.open("rb") as stream:
        return {"sizeBytes": path.stat().st_size,
                "sha256": hashlib.file_digest(stream, "sha256").hexdigest()}


def read_json(path: Path) -> dict:
    return json.loads(path.read_bytes())


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def payload_files(pack: Path) -> dict:
    inputs = read_json(SOURCE / "upstream-lock.json")
    support = read_json(SOURCE / "tools/distribution-support-lock.json")
    require(json.loads((pack / "portable-pack.json").read_bytes()) ==
            read_json(SOURCE / "portable-pack.json"), "Unexpected runtime descriptor")
    rows = [row for row in inputs["inputFiles"] if row["path"].startswith("mods/")]
    rows += inputs["requestedShaders"] + support["files"]
    files = {row["path"]: {key: row[key] for key in ("sizeBytes", "sha256")} for row in rows}
    for path, expected in files.items():
        require(fingerprint(pack / path) == expected, f"Changed input: {path}")
    for directory in ("mods", "shaderpacks", "config", "launcher"):
        expected = {path for path in files if path.startswith(directory + "/")}
        actual = {path.relative_to(pack).as_posix() for path in (pack / directory).rglob("*") if path.is_file()}
        require(actual == expected, f"Unexpected files in {directory}")
    return dict(sorted(files.items()))


def verify(pack: Path, output: Path, manifest: dict, library) -> None:
    expected = payload_files(pack)
    require({row["path"]: {k: row[k] for k in ("sizeBytes", "sha256")}
             for row in manifest["files"]} == expected, "Manifest files differ from the locks")
    seen = set()
    for asset in manifest["assets"]:
        path = output / "assets" / asset["name"]
        require(fingerprint(path) == {k: asset[k] for k in ("sizeBytes", "sha256")}, f"Changed asset: {path.name}")
        members = asset["covers"]
        require(not (seen & set(members)), f"Duplicate asset members: {path.name}")
        seen.update(members)
        if asset["kind"] == "zipRoot":
            with zipfile.ZipFile(path) as archive:
                require(archive.namelist() == members, f"Unexpected ZIP members: {path.name}")
                for entry in archive.infolist():
                    require(entry.file_size == expected[entry.filename]["sizeBytes"] and
                            hashlib.sha256(archive.read(entry)).hexdigest() == expected[entry.filename]["sha256"],
                            f"Changed ZIP member: {entry.filename}")
        else:
            require(len(members) == 1 and fingerprint(path) == expected[members[0]], "Unexpected root file")
    require(seen == set(expected), "Incomplete manifest coverage")
    library.verify_library(output, manifest["library"])
    launcher_asset = next(a for a in manifest["assets"] if "launcher/options-default.txt" in a["covers"])
    with zipfile.ZipFile(output / "assets" / launcher_asset["name"]) as archive:
        multiplayer_warning_policy.verify_contents(archive.read("launcher/options-default.txt"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--launcher", required=True, type=Path)
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    pack, output, launcher = (p.resolve() for p in (args.pack, args.out, args.launcher))
    sys.path.insert(0, str(launcher / "tools"))
    sys.path.insert(0, str(launcher / "tools/PackData/CurseForge"))
    import pack_library
    from stage_release import build_assets

    network_logging_policy.verify(SOURCE)
    multiplayer_warning_policy.verify(pack)
    if args.verify_only:
        manifest = read_json(output / "pack-manifest.json")
    else:
        files = payload_files(pack)
        output.mkdir()
        assets = output / "assets"
        assets.mkdir()
        revision = subprocess.check_output(["git", "-C", str(SOURCE), "rev-parse", "HEAD"], text=True).strip()
        require(re.fullmatch("[0-9a-f]{40}", revision) is not None, "Invalid source revision")
        tracked = subprocess.check_output(
            ["git", "-C", str(SOURCE), "status", "--porcelain", "--untracked-files=no"], text=True)
        require(not tracked, "Commit source changes before staging")
        runtime = read_json(pack / "portable-pack.json")
        library = pack_library.stage_library(pack, output, revision, metadata_root=SOURCE, shipped=files)
        with zipfile.ZipFile(assets / library["name"]) as archive:
            card = json.loads(archive.read("library.json"))
        manifest = {
            "schemaVersion": 2, "packId": card["id"], "revision": revision,
            "generatedAtUtc": subprocess.check_output(
                ["git", "-C", str(SOURCE), "show", "-s", "--format=%cI", revision], text=True).strip(),
            "minecraftVersion": runtime["minecraftVersion"], "loader": runtime["loader"],
            "modCount": sum(mod["isLoadedMod"] for mod in card["mods"]),
            "files": [{"path": path, **pin} for path, pin in files.items()],
            "assets": build_assets(pack, assets, files), "library": library,
        }
        (output / "pack-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                                                  encoding="utf-8", newline="\n")
    verify(pack, output, manifest, pack_library)
    print(f"{manifest['revision']}: {len(manifest['files'])} verified files, "
          f"{len(manifest['assets'])} game assets, {manifest['modCount']} loaded mods")


if __name__ == "__main__":
    main()
