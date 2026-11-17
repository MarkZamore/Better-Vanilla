"""Build the deterministic pack-owned policy using the target JDK and Gson."""
import argparse
from pathlib import Path
import subprocess
import tempfile
import zipfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--jdk', required=True, type=Path)
parser.add_argument('--gson', required=True, type=Path)
parser.add_argument('--out', required=True, type=Path)
args = parser.parse_args()
source = Path(__file__).with_name('InventoryProfilesDefaults.java')
args.out.parent.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(prefix='inventory-defaults-', dir=args.out.parent) as temp:
    classes = Path(temp)
    subprocess.run([str(args.jdk / 'bin/javac.exe'), '--release', '25', '-encoding', 'UTF-8',
                    '-cp', str(args.gson.resolve()), '-d', str(classes), str(source.resolve())], check=True)
    manifest = b'Manifest-Version: 1.0\r\nPremain-Class: bettervanilla.InventoryProfilesDefaults\r\n\r\n'
    entries = [('META-INF/MANIFEST.MF', manifest)]
    entries += [(p.relative_to(classes).as_posix(), p.read_bytes()) for p in sorted(classes.rglob('*.class'))]
    with zipfile.ZipFile(args.out, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in entries:
            info = zipfile.ZipInfo(name, (2026, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)
print(args.out)
