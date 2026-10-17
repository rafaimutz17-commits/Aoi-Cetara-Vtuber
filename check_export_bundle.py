#!/usr/bin/env python3
"""Periksa kelengkapan folder ekspor Live2D (hasil Export For Runtime dari Cubism Editor).

Membaca <nama>.model3.json dan memastikan setiap berkas yang direferensikan ada:
Moc, Textures, Physics, Pose, DisplayInfo, Expressions[].File, Motions[grup][].File.
Juga memastikan setiap ID parameter pada physics3.json / exp3.json / motion3.json
dikenal oleh parameter_map.csv (bila --params diberikan).

CATATAN: skrip hanya memeriksa keberadaan dan konsistensi berkas. Skrip TIDAK membuktikan
model dapat dimuat di Cubism Viewer atau VTube Studio, dan TIDAK memeriksa isi biner .moc3.

Pemakaian:
    python3 check_export_bundle.py <folder_ekspor> [--params parameter_map.csv]
Keluar dengan kode 1 bila ada masalah. Hanya membaca berkas.
"""
import csv
import glob
import json
import os
import sys


def load(path):
    with open(path, encoding='utf-8-sig') as f:
        return json.load(f)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    root = sys.argv[1]
    params = None
    if '--params' in sys.argv:
        pm = sys.argv[sys.argv.index('--params') + 1]
        params = {r['parameter_id'] for r in csv.DictReader(open(pm, encoding='utf-8'))}
    problems, notes = [], []

    indexes = glob.glob(os.path.join(root, '*.model3.json'))
    if len(indexes) != 1:
        problems.append(f'harus ada tepat satu *.model3.json di {root}; ditemukan {len(indexes)}')
        report(problems, notes)
    idx = indexes[0]
    try:
        model = load(idx)
    except Exception as e:  # noqa: BLE001
        problems.append(f'{os.path.basename(idx)} bukan JSON valid: {e}')
        report(problems, notes)
    if model.get('Version') != 3:
        problems.append(f"Version bukan 3: {model.get('Version')}")
    refs = model.get('FileReferences', {})
    wanted = []
    if refs.get('Moc'):
        wanted.append(('Moc', refs['Moc']))
    else:
        problems.append('FileReferences.Moc tidak ada')
    textures = refs.get('Textures') or []
    if not textures:
        problems.append('FileReferences.Textures kosong')
    wanted += [('Texture', t) for t in textures]
    for key in ('Physics', 'Pose', 'DisplayInfo', 'UserData'):
        if refs.get(key):
            wanted.append((key, refs[key]))
    if not refs.get('Physics'):
        notes.append('tidak ada Physics terdaftar: physics harus diekspor bersama model agar terpakai VTube Studio')
    for e in refs.get('Expressions') or []:
        wanted.append(('Expression', e.get('File', '')))
    for group, items in (refs.get('Motions') or {}).items():
        for m in items:
            wanted.append((f'Motion[{group}]', m.get('File', '')))
    for kind, rel in wanted:
        if not rel or not os.path.isfile(os.path.join(root, rel)):
            problems.append(f'{kind}: berkas tidak ada -> {rel!r}')
    seen_moc = glob.glob(os.path.join(root, '*.moc3'))
    for f in seen_moc:
        if os.path.getsize(f) == 0:
            problems.append(f'berkas .moc3 kosong: {os.path.basename(f)}')
    if params is not None:
        for pat in ('*.physics3.json', '**/*.exp3.json', '**/*.motion3.json'):
            for f in glob.glob(os.path.join(root, pat), recursive=True):
                try:
                    d = load(f)
                except Exception as e:  # noqa: BLE001
                    problems.append(f'{os.path.relpath(f, root)} bukan JSON valid: {e}')
                    continue
                ids = set()
                if f.endswith('.physics3.json'):
                    for s in d.get('PhysicsSettings', []):
                        ids |= {i['Source']['Id'] for i in s.get('Input', [])}
                        ids |= {o['Destination']['Id'] for o in s.get('Output', [])}
                elif f.endswith('.exp3.json'):
                    ids = {p['Id'] for p in d.get('Parameters', [])}
                else:
                    ids = {c['Id'] for c in d.get('Curves', []) if c.get('Target') == 'Parameter'}
                unknown = sorted(ids - params)
                if unknown:
                    problems.append(f'{os.path.relpath(f, root)}: ID parameter tidak ada di parameter_map.csv -> {unknown}')
    notes.append(f'{len(wanted)} referensi diperiksa')
    report(problems, notes)


def report(problems, notes):
    for n in notes:
        print('  [catatan] ' + n)
    for p in problems:
        print('  [MASALAH] ' + p)
    print('HASIL: ' + ('GAGAL' if problems else 'LULUS (hanya keberadaan berkas; bukan bukti model dapat dimuat)'))
    sys.exit(1 if problems else 0)


if __name__ == '__main__':
    main()
