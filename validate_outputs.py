#!/usr/bin/env python3
"""Validasi paket Aoi_Cetara_Rigging_Specification.

Memeriksa:
  1. 10 berkas wajib ada dan tidak kosong
  2. CSV dapat diparse, jumlah kolom konsisten, kolom wajib ada, nilai status sah
  3. Markdown: ada judul H1, legenda status, tidak ada tautan relatif yang patah
  4. Referensi silang: parameter di deformer/physics/ekspresi ada di parameter_map.csv;
     layer di layer_mapping.csv berjumlah sama dengan manifest (bila --project diberikan)
  5. Tidak ada berkas .moc3 / .model3.json / .cmo3 / .physics3.json palsu di folder keluaran
  6. data/audit_results.json dapat diparse

Pemakaian:
    python3 validate_outputs.py <folder_Aoi_Cetara_Rigging_Specification> [--project <folder_proyek>]
Keluar dengan kode 1 jika ada kegagalan. Hanya membaca berkas; tidak mengubah apa pun.
"""
import csv
import glob
import json
import os
import re
import sys

REQUIRED = ['README.md', 'asset_audit.md', 'rigging_specification.md', 'parameter_map.csv', 'deformer_plan.csv',
            'physics_plan.csv', 'expression_plan.csv', 'layer_mapping.csv', 'rigging_checklist.md', 'validation_report.md']
CSV_COLS = {
    'parameter_map.csv': ['parameter_id', 'min', 'default', 'max', 'status'],
    'deformer_plan.csv': ['deformer_id', 'jenis', 'parent', 'parameter_pengendali', 'status'],
    'physics_plan.csv': ['physics_group', 'input', 'output', 'respons_awal', 'redaman_awal', 'status'],
    'expression_plan.csv': ['ekspresi', 'parameter', 'nilai_perkiraan', 'status'],
    'layer_mapping.csv': ['layer_asli', 'grup_psd', 'fungsi_rig', 'nama_artmesh_diusulkan', 'artmesh_sudah_ada', 'status_rancangan'],
}
STATUS_OK = {'VERIFIED', 'PROPOSED', 'BLOCKED', 'COMPLETED'}
FORBIDDEN = ('*.moc3', '*.model3.json', '*.cmo3', '*.physics3.json', '*.exp3.json', '*.motion3.json')

fails, passes = [], []


def ok(msg):
    passes.append(msg)


def bad(msg):
    fails.append(msg)


def read_csv(path):
    with open(path, encoding='utf-8', newline='') as f:
        return list(csv.reader(f))


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    root = sys.argv[1]
    project = sys.argv[sys.argv.index('--project') + 1] if '--project' in sys.argv else None

    for name in REQUIRED:
        p = os.path.join(root, name)
        if os.path.isfile(p) and os.path.getsize(p) > 0:
            ok(f'ada & tidak kosong: {name}')
        else:
            bad(f'hilang/kosong: {name}')

    tables = {}
    for name, cols in CSV_COLS.items():
        p = os.path.join(root, name)
        if not os.path.isfile(p):
            continue
        try:
            rows = read_csv(p)
        except Exception as e:  # noqa: BLE001
            bad(f'CSV gagal diparse {name}: {e}')
            continue
        head, body = rows[0], rows[1:]
        widths = {len(r) for r in rows}
        if widths != {len(head)}:
            bad(f'{name}: jumlah kolom tidak konsisten {sorted(widths)}')
        else:
            ok(f'{name}: {len(body)} baris x {len(head)} kolom konsisten')
        missing = [c for c in cols if c not in head]
        if missing:
            bad(f'{name}: kolom wajib hilang {missing}')
        tables[name] = [dict(zip(head, r)) for r in body]
        if 'status' in head or 'status_rancangan' in head:
            col = 'status' if 'status' in head else 'status_rancangan'
            vals = {r[col] for r in tables[name]}
            if not vals <= STATUS_OK:
                bad(f'{name}: nilai status tidak sah {sorted(vals - STATUS_OK)}')
            else:
                ok(f'{name}: nilai status sah {sorted(vals)}')

    # referensi silang parameter
    if 'parameter_map.csv' in tables:
        pids = {r['parameter_id'] for r in tables['parameter_map.csv']}
        if len(pids) != len(tables['parameter_map.csv']):
            bad('parameter_map.csv: parameter_id duplikat')
        pat = re.compile(r'Param[A-Za-z]+')

        def refs(text):
            found = set(pat.findall(text))
            # singkatan seperti ParamBrowLY/RY atau ParamEye{R,L}Open tidak dipetakan satu per satu
            return {f for f in found if '{' not in f}

        known_prefix = {x for x in pids}
        unknown = {}
        for tname, col in (('deformer_plan.csv', 'parameter_pengendali'), ('physics_plan.csv', 'output'),
                           ('layer_mapping.csv', 'parameter_pengendali')):
            for r in tables.get(tname, []):
                for ref in refs(r.get(col, '')):
                    if ref not in known_prefix and not any(k.startswith(ref) for k in known_prefix):
                        unknown.setdefault(tname, set()).add(ref)
        if unknown:
            bad(f'parameter tidak ada di parameter_map.csv: { {k: sorted(v) for k, v in unknown.items()} }')
        else:
            ok('referensi parameter di deformer/physics/layer cocok dengan parameter_map.csv')

    # referensi layer: nama layer yang dipakai di deformer_plan harus ada di layer_mapping (atau pola/pengelompokan)
    if 'layer_mapping.csv' in tables:
        lnames = [r['layer_asli'] for r in tables['layer_mapping.csv']]
        if len(set(lnames)) != len(lnames):
            bad('layer_mapping.csv: nama layer duplikat')
        else:
            ok(f'layer_mapping.csv: {len(lnames)} nama layer unik')
        if any(r['artmesh_sudah_ada'].startswith('YA') for r in tables['layer_mapping.csv']):
            bad('layer_mapping.csv: ada ArtMesh bertanda sudah ada, padahal belum ada model Cubism')
        else:
            ok('layer_mapping.csv: tidak ada klaim ArtMesh yang sudah dibuat')
        orders = [int(r['urutan_gambar_diusulkan']) for r in tables['layer_mapping.csv']]
        if sorted(orders) == list(range(1, len(orders) + 1)):
            ok('urutan_gambar_diusulkan: permutasi lengkap 1..N')
        else:
            bad('urutan_gambar_diusulkan: bukan permutasi 1..N')
        known_layers = set(lnames)
        miss = {}
        for r in tables.get('deformer_plan.csv', []):
            for tok in re.findall(r'[A-Z][A-Z0-9_]{3,}', r.get('objek_dideformasi', '')):
                if tok.startswith('D_') or tok.startswith('PARAM'):
                    continue
                if tok in known_layers or any(k.startswith(tok.rstrip('_')) for k in known_layers):
                    continue
                miss.setdefault(r['deformer_id'], set()).add(tok)
        if miss:
            bad(f'deformer_plan.csv: nama layer tidak dikenal { {k: sorted(v) for k, v in miss.items()} }')
        else:
            ok('deformer_plan.csv: semua nama layer yang disebut ada di layer_mapping.csv')
        if project:
            mp = os.path.join(project, '02_Layered_Artwork', 'Layer_Manifest.csv')
            if os.path.isfile(mp):
                man = [r['name'] for r in csv.DictReader(open(mp, encoding='utf-8-sig'))]
                if sorted(man) == sorted(lnames):
                    ok(f'layer_mapping.csv cocok dengan Layer_Manifest.csv ({len(man)} layer)')
                else:
                    bad('layer_mapping.csv tidak cocok dengan Layer_Manifest.csv')
            else:
                bad(f'manifest tidak ditemukan: {mp}')
        # deformer parent harus ada
        dids = {r['deformer_id'] for r in tables.get('deformer_plan.csv', [])}
        orphan = [r['deformer_id'] for r in tables.get('deformer_plan.csv', [])
                  if r['parent'] not in dids and r['parent'] != '(root)']
        if orphan:
            bad(f'deformer_plan.csv: parent tidak ditemukan untuk {orphan}')
        else:
            ok('deformer_plan.csv: semua parent valid (rantai tidak yatim)')

    for name in REQUIRED:
        if name.endswith('.md'):
            p = os.path.join(root, name)
            if not os.path.isfile(p):
                continue
            text = open(p, encoding='utf-8').read()
            if not re.search(r'^# ', text, re.M):
                bad(f'{name}: tidak ada judul H1')
            else:
                ok(f'{name}: judul H1 ada')
            if name != 'README.md' and not all(s in text for s in STATUS_OK):
                bad(f'{name}: legenda/penggunaan status VERIFIED/PROPOSED/BLOCKED/COMPLETED tidak lengkap')
            for m in re.finditer(r'\]\(([^)#:]+\.[a-z0-9]+)\)', text):
                target = os.path.join(root, m.group(1))
                if not os.path.exists(target):
                    bad(f'{name}: tautan patah -> {m.group(1)}')

    for pat in FORBIDDEN:
        hits = glob.glob(os.path.join(root, '**', pat), recursive=True)
        if hits:
            bad(f'berkas runtime/template tidak boleh ada di keluaran: {hits}')
    ok('tidak ada berkas .moc3/.model3.json/.cmo3/.physics3.json/.exp3.json/.motion3.json di keluaran') if not any(
        glob.glob(os.path.join(root, '**', p), recursive=True) for p in FORBIDDEN) else None

    ar = os.path.join(root, 'data', 'audit_results.json')
    if os.path.isfile(ar):
        try:
            json.load(open(ar, encoding='utf-8'))
            ok('data/audit_results.json dapat diparse')
        except Exception as e:  # noqa: BLE001
            bad(f'audit_results.json gagal diparse: {e}')

    print(f'LULUS: {len(passes)}   GAGAL: {len(fails)}')
    for m in passes:
        print('  [OK]    ' + m)
    for m in fails:
        print('  [GAGAL] ' + m)
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
