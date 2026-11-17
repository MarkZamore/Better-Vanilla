"""Resolve the candidate through Fabric, then stop before Minecraft starts."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import zipfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--run', required=True, type=Path)
parser.add_argument('--jdk', required=True, type=Path)
args = parser.parse_args()
root = Path.cwd().resolve()
run = args.run.resolve()
assert run.parent == root / 'artifacts/agent-runs' and (run / 'RUN.json').is_file()
shared = root / 'Minecraft/Launcher/Shared'
libraries = []
for name in ('fabric-loader-0.20.1-26.3', '26.3'):
    document = json.loads((shared / f'versions/{name}/{name}.json').read_bytes())
    for row in document['libraries']:
        if row.get('rules') and not any(r['action'] == 'allow' and r.get('os', {}).get('name', 'windows') == 'windows'
                                       for r in row['rules']):
            continue
        if 'downloads' in row:
            artifact = row['downloads'].get('artifact')
            if not artifact:
                continue
            path = artifact['path']
        else:
            group, artifact, version = row['name'].split(':')
            path = f'{group.replace(".", "/")}/{artifact}/{version}/{artifact}-{version}.jar'
        jar = shared / 'libraries' / path
        assert jar.is_file(), jar
        libraries.append(jar)
libraries.append(shared / 'versions/26.3/26.3.jar')
classpath = os.pathsep.join(map(str, libraries))
classes = run / 'resolution-classes'
classes.mkdir()
agent_source = Path(__file__).with_name('ResolutionOnlyAgent.java').resolve()
subprocess.run([str(args.jdk / 'bin/javac.exe'), '-cp', classpath, '-d', str(classes), str(agent_source)], check=True)
agent = run / 'resolution-only-agent.jar'
with zipfile.ZipFile(agent, 'w') as archive:
    archive.writestr('META-INF/MANIFEST.MF', 'Manifest-Version: 1.0\r\nPremain-Class: ResolutionOnlyAgent\r\n\r\n')
    for file in sorted(classes.glob('*.class')):
        archive.write(file, file.name)
pack = run / 'pack'
java = next(root.glob('Minecraft/Launcher/JavaRuntimes/runtime/windows-x64/*/bin/java.exe'))
command = [str(java), '-Xmx2G', '-Djava.awt.headless=true', '-javaagent:' + str(agent),
           '-cp', classpath, 'net.fabricmc.loader.impl.launch.knot.KnotClient',
           '--gameDir', str(pack), '--version', 'fabric-loader-0.20.1-26.3']
with (run / 'fabric-resolution.log').open('wb') as output:
    result = subprocess.run(command, cwd=pack, stdout=output, stderr=subprocess.STDOUT, timeout=120)
log = (run / 'fabric-resolution.log').read_text(encoding='utf-8', errors='replace')
if result.returncode or 'FABRIC_RESOLUTION_ONLY_PASS' not in log:
    raise RuntimeError('Fabric resolution failed. Inspect ' + str(run / 'fabric-resolution.log'))
proof = {'status': 'PASS', 'minecraftMainExecuted': False, 'computerUse': False,
         'gameJarSha256': hashlib.sha256(libraries[-1].read_bytes()).hexdigest(),
         'logSha256': hashlib.sha256((run / 'fabric-resolution.log').read_bytes()).hexdigest()}
(run / 'fabric-resolution-proof.json').write_text(json.dumps(proof, indent=2) + '\n', encoding='utf-8')
print('PASS: actual Fabric resolution completed and Minecraft main was skipped')
