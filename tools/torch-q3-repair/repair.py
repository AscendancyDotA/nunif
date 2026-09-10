"""Opt-in repair for the exact tested Windows Torch build; stdlib only."""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import tempfile

SPEC = json.loads(Path(__file__).with_name('patch.json').read_text(encoding='utf-8'))


def digest(data):
    return hashlib.sha256(data.replace(b'\r\n', b'\n')).hexdigest()


def candidate(data):
    text = data.decode('utf-8').replace('\r\n', '\n')
    for edit in SPEC['edits']:
        if text.count(edit['before']) != 1:
            raise ValueError('Patch context mismatch; refusing to patch')
        text = text.replace(edit['before'], edit['after'], 1)
    result = text.encode('utf-8')
    if digest(result) != SPEC['patched_sha256']:
        raise ValueError('Patched checksum mismatch')
    compile(text, 'symbolic_shapes.py', 'exec')
    return result.replace(b'\n', b'\r\n') if b'\r\n' in data else result


def repair(installation, action='check'):
    if action not in ('check', 'apply', 'restore'):
        raise ValueError('Unknown action')
    torch = Path(installation) / 'python/Lib/site-packages/torch'
    version_tree = ast.parse((torch / 'version.py').read_text(encoding='utf-8'))
    versions = []
    for node in version_tree.body:
        targets = node.targets if isinstance(node, ast.Assign) else [node.target] if isinstance(node, ast.AnnAssign) else []
        if any(isinstance(t, ast.Name) and t.id == '__version__' for t in targets):
            versions.append(ast.literal_eval(node.value))
    if versions != [SPEC['torch_version']]:
        raise ValueError('Unknown Torch version; refusing to modify it')
    target = torch / 'fx/experimental/symbolic_shapes.py'
    backup = target.with_name(target.name + '.iw3-q3-original')
    original = target.read_bytes()
    checksum = digest(original)
    if checksum == SPEC['original_sha256']:
        state = 'original'
    elif checksum == SPEC['patched_sha256']:
        state = 'patched'
    else:
        raise ValueError('Unknown source checksum; refusing to modify it')
    if action == 'check' or (action == 'apply' and state == 'patched') or (action == 'restore' and state == 'original'):
        return state
    if action == 'apply':
        replacement = candidate(original)
        if backup.exists():
            if backup.read_bytes() != original:
                raise ValueError('Existing backup differs; refusing to overwrite it')
        else:
            with backup.open('xb') as f:
                f.write(original)
        if backup.read_bytes() != original:
            raise ValueError('Backup verification failed')
    else:
        replacement = backup.read_bytes()
        if digest(replacement) != SPEC['original_sha256']:
            raise ValueError('Backup checksum mismatch; refusing to restore it')
    if target.read_bytes() != original:
        raise ValueError('Target changed during operation; refusing to overwrite it')
    staged = None
    try:
        with tempfile.NamedTemporaryFile(dir=target.parent, prefix='.iw3-q3-', delete=False) as f:
            staged = Path(f.name)
            f.write(replacement)
        os.replace(staged, target)
        if target.read_bytes() != replacement:
            raise OSError('Target readback failed; backup retained')
    finally:
        if staged is not None:
            staged.unlink(missing_ok=True)
    return 'patched' if action == 'apply' else 'original'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('installation', type=Path, help='Windows iw3 folder containing python/ (not the nunif subfolder)')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--apply', action='store_true')
    group.add_argument('--restore', action='store_true')
    args = parser.parse_args()
    try:
        print(repair(args.installation, 'apply' if args.apply else 'restore' if args.restore else 'check'))
    except (OSError, ValueError, SyntaxError) as error:
        parser.exit(1, f'Refused/failed: {error}\n')
