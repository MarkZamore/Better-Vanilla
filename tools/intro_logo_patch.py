"""Reproducible CC0 intro variant: retain the vanilla Mojang loading logo."""
import argparse
import copy
import hashlib
import io
from pathlib import Path
import zipfile
import json

ORIGINAL_SHA256 = "30cd1c2332a77052c0a7ffecc8c060d436923b97d16ce2ebeb9e725ae03e3826"
CONFIG = "reimagined-intro.mixins.json"
HIDDEN_LOGO_CLASS = "noobtrieu/reimaginedintro/client/mixin/LoadingOverlayMixin.class"
HIDDEN_LOGO_CLASS_SHA256 = "a7147d1f2ceb084d7cc865390b8f51659e9a443b5b7db72ed1682c1ba1778d83"
ORIGINAL_MIXINS = ["TitleScreenMixin", "ScreenMixin", "PanoramaMixin", "LoadingOverlayMixin"]

def apply(original: bytes) -> bytes:
    if hashlib.sha256(original).hexdigest() != ORIGINAL_SHA256:
        raise ValueError("Reimagined Intro upstream JAR changed; review the patch")
    with zipfile.ZipFile(io.BytesIO(original)) as source:
        if hashlib.sha256(source.read(HIDDEN_LOGO_CLASS)).hexdigest() != HIDDEN_LOGO_CLASS_SHA256:
            raise ValueError("Logo hiding implementation changed")
        settings = json.loads(source.read(CONFIG))
        if settings["client"] != ORIGINAL_MIXINS:
            raise ValueError("Unexpected mixin list")
        settings["client"].remove("LoadingOverlayMixin")
        output = io.BytesIO()
        with zipfile.ZipFile(output, "w") as target:
            target.comment = source.comment
            for entry in source.infolist():
                data = ((json.dumps(settings, indent=2) + "\n").encode("utf-8")
                        if entry.filename == CONFIG else source.read(entry))
                target.writestr(copy.copy(entry), data)
    return output.getvalue()

def verify(original: bytes, patched: bytes) -> dict:
    if apply(original) != patched:
        raise ValueError("Variant is not the reproducible patch")
    with zipfile.ZipFile(io.BytesIO(original)) as old, zipfile.ZipFile(io.BytesIO(patched)) as new:
        if old.namelist() != new.namelist():
            raise ValueError("Archive members changed")
        changed = [name for name in old.namelist() if old.read(name) != new.read(name)]
        if changed != [CONFIG]:
            raise ValueError("Unexpected changed archive members")
        before, after = json.loads(old.read(CONFIG)), json.loads(new.read(CONFIG))
        before["client"].remove("LoadingOverlayMixin")
        if before != after:
            raise ValueError("Unrelated mixin settings changed")
        return {"status": "PASS", "changedMembers": changed,
                "unchangedMembers": len(old.namelist()) - 1,
                "disabledMixin": "LoadingOverlayMixin",
                "retainedMixins": after["client"],
                "classVideoLicenseBytesUnchanged": True,
                "originalSha256": hashlib.sha256(original).hexdigest(),
                "patchedSha256": hashlib.sha256(patched).hexdigest()}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    original = args.original.read_bytes()
    patched = apply(original)
    result = verify(original, patched)
    args.out.write_bytes(patched)
    print(json.dumps(result, indent=2))
