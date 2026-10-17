#!/usr/bin/env python3
"""Audit aset Aoi Cetara untuk persiapan rigging Live2D.

Memverifikasi LANGSUNG dari berkas (tidak mempercayai klaim README/QA):
  * checksum SHA256 terhadap SHA256SUMS.txt
  * manifest layer vs PNG (ukuran kanvas, kosong, bbox)
  * apakah layer aktif saling tumpang-tindih (partisi) dan pasangan yang bersentuhan (seam)
  * struktur PSD (jumlah layer, grup, mask, visibilitas, ICC) lewat psd_inspect.py
  * konvensi LEFT/RIGHT (anatomi karakter -> LEFT berada di kanan layar)
  * metrik komponen wajah aktif vs komponen pengganti ALT_*
  * referensi parameter pada physics / ekspresi / motion / deformer vs Parameter_Spec.csv
  * keberadaan artefak runtime (.cmo3 / .moc3 / .model3.json)

Pemakaian:
    python3 audit_assets.py <folder_proyek_terekstrak> [--out audit_results.json]

Dependensi: Python 3.9+, numpy, Pillow. Tidak mengubah berkas apa pun di folder proyek.
"""
import csv
import fnmatch
import glob
import hashlib
import json
import os
import sys
import ast

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from psd_inspect import read_psd_layers  # noqa: E402

CANVAS_W, CANVAS_H = 1024, 1536


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def check_checksums(root):
    sums = os.path.join(root, 'SHA256SUMS.txt')
    res = {'listed': 0, 'ok': 0, 'mismatch': [], 'missing': [], 'unlisted': []}
    if not os.path.exists(sums):
        res['note'] = 'SHA256SUMS.txt tidak ditemukan'
        return res
    listed = set()
    for line in open(sums, encoding='utf-8'):
        line = line.strip()
        if not line:
            continue
        digest, name = line.split(None, 1)
        name = name.strip().lstrip('*')
        listed.add(name)
        res['listed'] += 1
        p = os.path.join(root, name)
        if not os.path.exists(p):
            res['missing'].append(name)
        elif sha256(p) == digest.lower():
            res['ok'] += 1
        else:
            res['mismatch'].append(name)
    for p in glob.glob(os.path.join(root, '**', '*'), recursive=True):
        if os.path.isfile(p):
            rel = os.path.relpath(p, root).replace(os.sep, '/')
            if rel not in listed and rel != 'SHA256SUMS.txt':
                res['unlisted'].append(rel)
    return res


def load_manifest(root):
    path = os.path.join(root, '02_Layered_Artwork', 'Layer_Manifest.csv')
    return list(csv.DictReader(open(path, encoding='utf-8-sig')))


def layer_metrics(root, rows):
    out, sizes = {}, set()
    for r in rows:
        im = Image.open(os.path.join(root, r['png'])).convert('RGBA')
        sizes.add(im.size)
        a = np.array(im)[:, :, 3]
        ys, xs = np.where(a > 0)
        if len(xs) == 0:
            out[r['name']] = {'empty': True}
            continue
        bbox = [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]
        out[r['name']] = {
            'empty': False, 'bbox': bbox, 'w': bbox[2] - bbox[0], 'h': bbox[3] - bbox[1],
            'alpha_px': int((a > 0).sum()), 'semi_px': int(((a > 0) & (a < 255)).sum()),
            'cx': (bbox[0] + bbox[2]) // 2, 'cy': (bbox[1] + bbox[3]) // 2,
            'manifest_bbox': ast.literal_eval(r['bbox']),
            'bbox_matches_manifest': bbox == list(ast.literal_eval(r['bbox'])),
        }
    return out, sorted(sizes)


def partition_and_seams(root, rows):
    vis = [r for r in rows if r['visible'] == 'True']
    names = [r['name'] for r in vis]
    idm = np.zeros((CANVAS_H, CANVAS_W), dtype=np.int16)
    cnt = np.zeros((CANVAS_H, CANVAS_W), dtype=np.int16)
    for i, r in enumerate(vis, 1):
        a = np.array(Image.open(os.path.join(root, r['png'])).convert('RGBA'))[:, :, 3] > 0
        idm[a] = i
        cnt += a
    overlap_px = int((cnt >= 2).sum())

    def pair_codes(a, b):
        m = (a > 0) & (b > 0) & (a != b)
        x = np.minimum(a[m], b[m]).astype(np.int32)
        y = np.maximum(a[m], b[m]).astype(np.int32)
        return x * 1000 + y

    codes = np.concatenate([pair_codes(idm[:, :-1], idm[:, 1:]), pair_codes(idm[:-1, :], idm[1:, :])])
    u, c = np.unique(codes, return_counts=True)
    seams = []
    for k in np.argsort(-c):
        i, j = divmod(int(u[k]), 1000)
        seams.append({'a': names[i - 1], 'b': names[j - 1], 'contact_px': int(c[k])})
    return {
        'visible_layers': len(vis), 'overlap_pixels': overlap_px,
        'covered_pixels': int((cnt == 1).sum()), 'touching_pairs': len(seams), 'seams': seams,
    }


def psd_audit(root, rows):
    path = os.path.join(root, '02_Layered_Artwork', 'Aoi_Cetara_ArtPrep_v1.psd')
    info = read_psd_layers(path)
    real = [l for l in info['layers'] if l['section'] is None]
    groups = [l for l in info['layers'] if l['section'] in (1, 2)]
    man = {r['name']: r['visible'] == 'True' for r in rows}
    names = [l['name'] for l in real]
    return {
        'canvas': [info['width'], info['height']], 'depth': info['depth'], 'mode_rgb': info['mode'] == 3,
        'icc_embedded': info['has_icc_profile'], 'raster_layers': len(real), 'groups': len(groups),
        'layers_with_mask': sum(l['has_mask'] for l in real),
        'opacity_values': sorted({l['opacity'] for l in real}),
        'blend_modes': sorted({l['blend'] for l in real}),
        'names_unique': len(names) == len(set(names)),
        'names_match_manifest': set(names) == set(man),
        'visibility_matches_manifest': all(l['visible'] == man.get(l['name']) for l in real),
        'group_order_bottom_to_top': [l['name'] for l in groups if l['section'] == 1],
        'note': 'PSD dibuat oleh skrip, bukan Photoshop/Clip Studio Paint (aplikasi yang dijamin Live2D).',
    }


def lr_convention(metrics):
    bad, ok = [], 0
    for n, m in metrics.items():
        if m.get('empty') or not n.endswith('_LEFT'):
            continue
        other = n[:-5] + '_RIGHT'
        if other not in metrics:
            continue
        ok_pair = metrics[n]['cx'] > CANVAS_W // 2 > metrics[other]['cx']
        # hair/skirt halves are cut at x=512 so centre comparison still holds
        if ok_pair:
            ok += 1
        else:
            bad.append([n, metrics[n]['cx'], other, metrics[other]['cx']])
    return {'pairs_consistent': ok, 'inconsistent': bad,
            'convention': 'LEFT = sisi kiri anatomi karakter = sisi KANAN layar'}


def face_metrics(metrics):
    pairs = []
    for s in ('LEFT', 'RIGHT'):
        pairs += [(f'EYE_WHITE_{s}', f'ALT_SCLERA_{s}'), (f'IRIS_{s}', f'ALT_IRIS_FULL_{s}'),
                  (f'PUPIL_{s}', f'ALT_PUPIL_FULL_{s}'), (f'HIGHLIGHT_{s}', f'ALT_GLINT_{s}'),
                  (f'EYEBROW_{s}', f'ALT_EYEBROW_FULL_{s}'), (f'UPPER_EYELID_{s}', f'ALT_LASH_UPPER_{s}'),
                  (f'LOWER_EYELID_{s}', f'ALT_LASH_LOWER_{s}')]
    out = []
    for a, b in pairs:
        if a in metrics and b in metrics:
            ma, mb = metrics[a], metrics[b]
            out.append({'active': a, 'alt': b, 'active_wh': [ma['w'], ma['h']], 'alt_wh': [mb['w'], mb['h']],
                        'active_px': ma['alpha_px'], 'alt_px': mb['alpha_px'],
                        'center_offset': [mb['cx'] - ma['cx'], mb['cy'] - ma['cy']]})
    mouth = {n: [metrics[n]['w'], metrics[n]['h']] for n in
             ('MOUTH_CLOSED_NEUTRAL', 'ALT_MOUTH_CLOSED_ALT', 'ALT_MOUTH_UPPER', 'ALT_MOUTH_LOWER',
              'ALT_MOUTH_INSIDE', 'ALT_TEETH', 'ALT_TONGUE') if n in metrics}
    size = {n: [metrics[n]['w'], metrics[n]['h']] for n in ('FACE', 'BF_FACE_COMPLETE', 'NOSE', 'NECK') if n in metrics}
    return {'eye_pairs': out, 'mouth_wh': mouth, 'head_wh': size}


def highres_dims(root):
    d = {}
    for f in sorted(glob.glob(os.path.join(root, '03_PNG_Layers', 'Face_Components_Highres', '*.png'))):
        d[os.path.basename(f)] = list(Image.open(f).size)
    return d


def load_json(path):
    with open(path, encoding='utf-8-sig') as f:
        return json.load(f)


def parse_all_json(root):
    ok, bad = 0, []
    for p in glob.glob(os.path.join(root, '**', '*.json'), recursive=True):
        try:
            load_json(p)
            ok += 1
        except Exception as e:  # noqa: BLE001
            bad.append([os.path.relpath(p, root), str(e)])
    return {'parsed_ok': ok, 'failed': bad}


def spec_crossrefs(root, layer_names):
    spec = os.path.join(root, '04_Rigging_Spec')
    params = {r['id']: r for r in csv.DictReader(open(os.path.join(spec, 'Parameter_Spec.csv'), encoding='utf-8-sig'))}
    pids = set(params)
    res = {'parameter_count': len(pids)}
    phys = load_json(os.path.join(spec, 'Aoi_Cetara_TEMPLATE.physics3.json'))
    in_ids, out_ids, schema_missing = set(), set(), []
    settings = phys['PhysicsSettings']
    for s in settings:
        for i in s['Input']:
            in_ids.add(i['Source']['Id'])
            for k in ('Source', 'Weight', 'Type', 'Reflect'):
                if k not in i:
                    schema_missing.append([s['Id'], 'Input', k])
        for o in s['Output']:
            out_ids.add(o['Destination']['Id'])
            for k in ('Destination', 'VertexIndex', 'Scale', 'Weight', 'Type', 'Reflect'):
                if k not in o:
                    schema_missing.append([s['Id'], 'Output', k])
        for v in s['Vertices']:
            for k in ('Position', 'Mobility', 'Delay', 'Acceleration', 'Radius'):
                if k not in v:
                    schema_missing.append([s['Id'], 'Vertex', k])
        for k in ('Position', 'Angle'):
            if k not in s['Normalization']:
                schema_missing.append([s['Id'], 'Normalization', k])
    meta = phys['Meta']
    sig = {json.dumps([i['Source']['Id'] + i['Type'] + str(i['Weight']) for i in s['Input']]) for s in settings}
    vtx = {json.dumps(s['Vertices']) for s in settings}
    res['physics'] = {
        'settings': len(settings), 'meta_counts_match': (
            meta['PhysicsSettingCount'] == len(settings)
            and meta['TotalInputCount'] == sum(len(s['Input']) for s in settings)
            and meta['TotalOutputCount'] == sum(len(s['Output']) for s in settings)
            and meta['VertexCount'] == sum(len(s['Vertices']) for s in settings)),
        'input_ids': sorted(in_ids), 'output_ids': sorted(out_ids),
        'unknown_refs': sorted((in_ids | out_ids) - pids), 'schema_missing': schema_missing,
        'distinct_input_signatures': len(sig), 'distinct_vertex_profiles': len(vtx),
        'uses_ParamAngleY_input': 'ParamAngleY' in in_ids,
        'output_scales': sorted({o['Scale'] for s in settings for o in s['Output']}),
    }
    exp_unknown, exp_params, expr = {}, {}, {}
    for p in sorted(glob.glob(os.path.join(root, '05_Expression_Templates', '*.exp3.json'))):
        d = load_json(p)
        name = os.path.basename(p).replace('.exp3.json', '')
        ids = [x['Id'] for x in d['Parameters']]
        expr[name] = {x['Id']: x['Value'] for x in d['Parameters']}
        unk = sorted(set(ids) - pids)
        if unk:
            exp_unknown[name] = unk
        exp_params[name] = ids
    res['expressions'] = {'files': len(exp_params), 'unknown_refs': exp_unknown, 'values': expr}
    mo_unknown = {}
    for p in glob.glob(os.path.join(spec, 'Motion_Templates', '*.motion3.json')):
        ids = {c['Id'] for c in load_json(p)['Curves']}
        if ids - pids:
            mo_unknown[os.path.basename(p)] = sorted(ids - pids)
    res['motions'] = {'unknown_refs': mo_unknown}
    dspec = load_json(os.path.join(spec, 'Deformer_Hierarchy.spec.json'))['deformers']
    driven = set()
    explicit = set()
    unk_def = {}
    for d in dspec:
        for p in d['parameters']:
            driven.add(p)
            if p not in pids:
                unk_def.setdefault(d['id'], []).append(p)
        for m in d['members']:
            for n in layer_names:
                if fnmatch.fnmatchcase(n, m) and m != 'all':
                    explicit.add(n)
    res['deformers'] = {
        'count': len(dspec), 'unknown_param_refs': unk_def,
        'params_without_any_deformer_driver': sorted(pids - driven),
        'layers_named_explicitly_in_members': len(explicit),
        'layers_not_named_explicitly': sorted(set(layer_names) - explicit),
        'deformers_with_null_pivot': [d['id'] for d in dspec if d.get('pivot') is None],
    }
    res['params_without_physics_output'] = sorted(
        p for p in pids if p.endswith('Sway') and p not in out_ids)
    brow = {k: v for k, v in params.items() if k.startswith('ParamBrow') and k.endswith(('Form', 'Angle'))}
    res['brow_polarity_note_in_spec'] = {k: v['purpose'] for k, v in brow.items()}
    res['expression_brow_form'] = {n: {k: v for k, v in e.items() if 'BrowLForm' in k or 'BrowLAngle' in k}
                                   for n, e in expr.items() if n in ('ANGRY', 'SAD')}
    return res


def runtime_artifacts(root):
    found = {}
    for pat in ('*.cmo3', '*.moc3', '*.model3.json', '*.cdi3.json', '*.vtube.json'):
        found[pat] = [os.path.relpath(p, root) for p in glob.glob(os.path.join(root, '**', pat), recursive=True)]
    found['physics_template_only'] = [os.path.relpath(p, root) for p in
                                      glob.glob(os.path.join(root, '**', '*.physics3.json'), recursive=True)]
    return found


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    root = sys.argv[1]
    out = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else None
    rows = load_manifest(root)
    metrics, sizes = layer_metrics(root, rows)
    names = [r['name'] for r in rows]
    result = {
        'checksums': check_checksums(root),
        'manifest': {'rows': len(rows), 'png_canvas_sizes': sizes,
                     'empty_layers': [n for n, m in metrics.items() if m.get('empty')],
                     'bbox_mismatch': [n for n, m in metrics.items() if not m.get('empty') and not m['bbox_matches_manifest']],
                     'visible': sum(r['visible'] == 'True' for r in rows),
                     'hidden': sum(r['visible'] != 'True' for r in rows)},
        'partition': partition_and_seams(root, rows),
        'psd': psd_audit(root, rows),
        'lr_convention': lr_convention(metrics),
        'face': face_metrics(metrics),
        'highres_png_dims': highres_dims(root),
        'json': parse_all_json(root),
        'spec_crossrefs': spec_crossrefs(root, names),
        'runtime_artifacts': runtime_artifacts(root),
        'layer_metrics': metrics,
    }
    if out:
        with open(out, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=1)
    p = result['partition']
    print(f"checksum: {result['checksums']['ok']}/{result['checksums']['listed']} OK, "
          f"mismatch={len(result['checksums']['mismatch'])}, missing={len(result['checksums']['missing'])}")
    print(f"manifest: {result['manifest']['rows']} layer ({result['manifest']['visible']} aktif / {result['manifest']['hidden']} tersembunyi), "
          f"ukuran PNG={result['manifest']['png_canvas_sizes']}, kosong={len(result['manifest']['empty_layers'])}, "
          f"bbox beda={len(result['manifest']['bbox_mismatch'])}")
    print(f"partisi: piksel tumpang-tindih antar layer aktif={p['overlap_pixels']}, pasangan bersentuhan={p['touching_pairs']}")
    ps = result['psd']
    print(f"psd: {ps['raster_layers']} layer, {ps['groups']} grup, mask={ps['layers_with_mask']}, "
          f"nama unik={ps['names_unique']}, cocok manifest={ps['names_match_manifest']}, ICC={ps['icc_embedded']}")
    print(f"L/R: {result['lr_convention']['pairs_consistent']} pasangan konsisten, tidak konsisten={len(result['lr_convention']['inconsistent'])}")
    sc = result['spec_crossrefs']
    print(f"spec: physics unknown refs={sc['physics']['unknown_refs']}, expr unknown={sc['expressions']['unknown_refs']}, "
          f"deformer unknown={sc['deformers']['unknown_param_refs']}")
    print(f"      param tanpa driver deformer={sc['deformers']['params_without_any_deformer_driver']}")
    print(f"      physics: input signature berbeda={sc['physics']['distinct_input_signatures']}, vertex profile berbeda={sc['physics']['distinct_vertex_profiles']}")
    ra = result['runtime_artifacts']
    print('artefak runtime ditemukan:', {k: len(v) for k, v in ra.items()})


if __name__ == '__main__':
    main()
