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
for name, initial in [('new', None), ('existing', {
        'ModSettings': {'first_run': False},
        'AutoRefillSettings': {'enable_auto_refill': True,
            'auto_refill_enable_indicator_icons': True,
            'auto_refill_enable_horbar_indicator_icons': {'value': True, 'keybind': 'custom-key'}},
        'unknown': ['keep', 12]})]:
    case = args.out / name
    (case / 'config/inventoryprofilesnext').mkdir(parents=True)
    config = case / 'config/inventoryprofilesnext/inventoryprofiles.json'
    if initial is not None:
        config.write_text(json.dumps(initial), encoding='utf-8')
    subprocess.run(command, cwd=case, capture_output=True, text=True, check=True)
    expected = json.loads(json.dumps(initial or {}))
    expected.setdefault('AutoRefillSettings', {})['auto_refill_enable_indicator_icons'] = False
    hotbar = expected['AutoRefillSettings'].get('auto_refill_enable_horbar_indicator_icons')
    if isinstance(hotbar, dict):
        hotbar['value'] = False
    else:
        expected['AutoRefillSettings']['auto_refill_enable_horbar_indicator_icons'] = False
    assert json.loads(config.read_bytes()) == expected
    checks.append(name + ': only arrow visibility changed, keybinds and other settings retained')
    before = config.read_bytes(), config.stat().st_mtime_ns
    subprocess.run(command, cwd=case, capture_output=True, text=True, check=True)
    assert (config.read_bytes(), config.stat().st_mtime_ns) == before
    checks.append(name + ': idempotent startup')
    expected['AutoRefillSettings']['auto_refill_enable_indicator_icons'] = True
    config.write_text(json.dumps(expected), encoding='utf-8')
    before = config.read_bytes()
    subprocess.run(command, cwd=case, capture_output=True, text=True, check=True)
    assert config.read_bytes() == before
    checks.append(name + ': later player choice retained')
case = args.out / 'malformed'
(case / 'config/inventoryprofilesnext').mkdir(parents=True)
config = case / 'config/inventoryprofilesnext/inventoryprofiles.json'
config.write_text('{invalid player file', encoding='utf-8')
before = config.read_bytes()
result = subprocess.run(command, cwd=case, capture_output=True, text=True, check=True)
assert config.read_bytes() == before and 'Could not apply IPN' in result.stderr
assert not (case / 'config/better-vanilla/ipn-arrow-defaults-v1.applied').exists()
checks.append('malformed settings preserved without migration marker')
case = args.out / 'nea-existing'
(case / 'config').mkdir(parents=True)
config = case / 'config/notenoughanimations.json'
initial = {'configVersion': 12, 'enableAnimationSmoothing': True, 'disableLegSmoothing': False,
           'enableLadderAnimation': True, 'bowAnimation': 'CUSTOM',
           'holdingItems': ['custom:torch'], 'unknownPlayerOption': {'keep': 42}}
config.write_text(json.dumps(initial), encoding='utf-8')
required = {'enableAnimationSmoothing': False, 'disableLegSmoothing': True,
            'enableLadderAnimation': False, 'bowAnimation': 'VANILLA'}
subprocess.run(command, cwd=case, capture_output=True, text=True, check=True)
assert json.loads(config.read_bytes()) == {**initial, **required}
checks.append('NEA four required compatibility values preserve all unrelated settings')
before = config.read_bytes(), config.stat().st_mtime_ns
subprocess.run(command, cwd=case, capture_output=True, text=True, check=True)
assert (config.read_bytes(), config.stat().st_mtime_ns) == before
checks.append('NEA compatibility settings are idempotent')
config.write_text('{invalid existing NEA file', encoding='utf-8')
before = config.read_bytes()
result = subprocess.run(command, cwd=case, capture_output=True, text=True, check=True)
assert config.read_bytes() == before and 'Could not apply NEA' in result.stderr
checks.append('NEA malformed settings preserved with diagnostic')
report = {'status': 'PASS', 'checks': checks, 'count': len(checks), 'minecraftStarted': False}
(args.out / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print('PASS:', len(checks), 'checks without Minecraft')
