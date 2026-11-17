"""Download every referenced public asset and verify the exact staged release."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import subprocess
import time
from urllib.request import urlopen

SOURCE = Path(__file__).resolve().parents[1]
BASE = 'https://github.com/MarkZamore/Better-Vanilla/releases/download/pack-latest/'


def download(row, target):
    path = target / row['name']
    for attempt in range(2):
        try:
            digest = hashlib.sha256()
            size = 0
            with urlopen(BASE + row['name'] + '?verify=' + str(time.time_ns()), timeout=90) as response:
                with path.open('wb') as output:
                    while block := response.read(1024 * 1024):
                        size += len(block)
                        if size > row['sizeBytes']:
                            raise ValueError('Asset exceeds declared size: ' + row['name'])
                        digest.update(block)
                        output.write(block)
            if size != row['sizeBytes'] or digest.hexdigest() != row['sha256']:
                raise ValueError('Public asset differs from lock: ' + row['name'])
            return size
        except Exception:
            if attempt:
                raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--staged', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    args.out.mkdir()
    assets = args.out / 'assets'
    assets.mkdir()
    staged = args.staged.read_bytes()
    manifest = json.loads(staged)
    with urlopen(BASE + 'pack-manifest.json?verify=' + str(time.time_ns()), timeout=60) as response:
        public = response.read(8 * 1024 * 1024)
    if public != staged:
        raise ValueError('Public manifest differs from the verified staged manifest')
    (args.out / 'pack-manifest.json').write_bytes(public)
    rows = manifest['assets'] + [manifest['library']]
    overlay = json.loads((SOURCE / 'tools/mod-overlay-lock.json').read_bytes())
    for row in overlay['add']:
        if source := row.get('correspondingSource'):
            rows.append({'name': source['releaseAsset'], 'sizeBytes': source['sizeBytes'],
                         'sha256': source['sha256']})
    release = json.loads(subprocess.check_output(
        ['gh', 'release', 'view', 'pack-latest', '-R', 'MarkZamore/Better-Vanilla', '--json', 'assets']))
    notices = [r for r in release['assets'] if r['name'].startswith('mod-licenses-')]
    if len(notices) != 1:
        raise ValueError('Expected one current license archive')
    notice = notices[0]
    rows.append({'name': notice['name'], 'sizeBytes': notice['size'],
                 'sha256': notice['name'].removeprefix('mod-licenses-').removesuffix('.zip')})
    with ThreadPoolExecutor(max_workers=4) as pool:
        sizes = list(pool.map(lambda row: download(row, assets), rows))
    result = {'status': 'PASS', 'revision': manifest['revision'],
              'manifestSha256': hashlib.sha256(public).hexdigest(),
              'fullBodyDownloads': len(rows), 'downloadedBytes': sum(sizes),
              'assets': [{'name': row['name'], 'sha256': row['sha256'],
                          'sizeBytes': row['sizeBytes']} for row in rows]}
    (args.out / 'public-verification.json').write_text(json.dumps(result, indent=2) + '\n',
                                                       encoding='utf-8', newline='\n')
    print(f"PASS: {len(rows)} complete public asset downloads, {sum(sizes)} bytes verified")


if __name__ == '__main__':
    main()
