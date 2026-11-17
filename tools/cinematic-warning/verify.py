"""Exercise the real premain in disposable JVMs without starting Minecraft."""
import argparse
import json
import os
from pathlib import Path
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--jdk', required=True, type=Path)
parser.add_argument('--gson', required=True, type=Path)
parser.add_argument('--agent', required=True, type=Path)
parser.add_argument('--out', required=True, type=Path)
args = parser.parse_args()
args.out.mkdir()
probe = args.out / 'PolicyProbe.java'
probe.write_text('public class PolicyProbe { public static void main(String[] args) {} }\n', encoding='utf-8')
subprocess.run([str(args.jdk / 'bin/javac.exe'), '--release', '25', '-d', str(args.out), str(probe)], check=True)
command = [str(args.jdk / 'bin/java.exe'), '-javaagent:' + str(args.agent.resolve()),
           '-cp', os.pathsep.join([str(args.gson.resolve()), str(args.out.resolve())]), 'PolicyProbe']

checks = []
for name, initial in [('new', None), ('existing', {'camera.approachSpeed': 67,
        'multiplayer.clientOnlyMode': False, 'multiplayer.serverHintSeen': False,
        'custom.playerOption': {'nested': [1, True, 'Тест']}}),
        ('already-set', {'multiplayer.serverHintSeen': True, 'camera.armStyle': 2})]:
    case = args.out / name
    (case / 'config').mkdir(parents=True)
    config = case / 'config/cinematic-client.json'
    if initial is not None:
        config.write_text(json.dumps(initial, ensure_ascii=False), encoding='utf-8')
    subprocess.run(command, cwd=case, capture_output=True, text=True, check=True)
    expected = {**(initial or {}), 'multiplayer.serverHintSeen': True}
    assert json.loads(config.read_bytes()) == expected, name
    before = config.read_bytes(), config.stat().st_mtime_ns
    subprocess.run(command, cwd=case, capture_output=True, text=True, check=True)
    assert (config.read_bytes(), config.stat().st_mtime_ns) == before, name + ' idempotence'
    assert not list((case / 'config').glob('*.tmp'))
    checks.extend([name + ' acknowledgement and settings preservation', name + ' idempotence'])
case = args.out / 'malformed'
(case / 'config').mkdir(parents=True)
config = case / 'config/cinematic-client.json'
config.write_text('{invalid player file', encoding='utf-8')
before = config.read_bytes()
result = subprocess.run(command, cwd=case, capture_output=True, text=True, check=True)
assert config.read_bytes() == before and 'Could not acknowledge' in result.stderr
checks.append('malformed settings preserved with diagnostic')
report = {'status': 'PASS', 'checks': checks, 'count': len(checks), 'minecraftStarted': False}
(args.out / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print('PASS:', len(checks), 'checks without Minecraft')
