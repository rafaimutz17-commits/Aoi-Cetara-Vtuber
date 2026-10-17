#!/usr/bin/env python3
"""Pembaca struktur PSD minimal (hanya stdlib) — membaca RECORD layer, bukan piksel.

Memeriksa: jumlah layer, nama (luni/pascal), visibilitas, opacity, blend mode,
bbox, penanda grup (lsct), keberadaan layer mask. Tidak mendekode data gambar.
Dipakai sebagai pembanding independen terhadap Layer_Manifest.csv.

Pemakaian: python3 psd_inspect.py <file.psd> [--json out.json]
"""
import struct, sys, json


def read_psd_layers(path):
    with open(path, 'rb') as f:
        data = f.read()
    if data[:4] != b'8BPS':
        raise ValueError('bukan PSD (signature 8BPS tidak ditemukan)')
    version, = struct.unpack('>H', data[4:6])
    if version != 1:
        raise ValueError(f'versi PSD {version} (PSB) tidak didukung')
    channels, height, width, depth, mode = struct.unpack('>HIIHH', data[12:26])
    pos = 26
    n, = struct.unpack('>I', data[pos:pos + 4]); pos += 4 + n   # color mode data
    n, = struct.unpack('>I', data[pos:pos + 4]); pos += 4
    resource_ids, rpos, rend = [], pos, pos + n
    while rpos + 12 <= rend and data[rpos:rpos + 4] == b'8BIM':
        rid, = struct.unpack('>H', data[rpos + 4:rpos + 6])
        plen = data[rpos + 6]
        rpos += 7 + plen + ((1 + plen) % 2)
        rsize, = struct.unpack('>I', data[rpos:rpos + 4])
        rpos += 4 + rsize + (rsize % 2)
        resource_ids.append(rid)
    pos = rend                                                    # image resources
    lm_len, = struct.unpack('>I', data[pos:pos + 4]); pos += 4
    lm_end = pos + lm_len
    li_len, = struct.unpack('>I', data[pos:pos + 4]); pos += 4
    count, = struct.unpack('>h', data[pos:pos + 2]); pos += 2
    count = abs(count)
    layers = []
    for _ in range(count):
        top, left, bottom, right, nch = struct.unpack('>iiiiH', data[pos:pos + 18]); pos += 18
        pos += 6 * nch
        sig, key = data[pos:pos + 4], data[pos + 4:pos + 8]; pos += 8
        opacity, clip, flags, _fill = struct.unpack('>BBBB', data[pos:pos + 4]); pos += 4
        extra_len, = struct.unpack('>I', data[pos:pos + 4]); pos += 4
        extra_end = pos + extra_len
        mlen, = struct.unpack('>I', data[pos:pos + 4]); pos += 4 + mlen
        blen, = struct.unpack('>I', data[pos:pos + 4]); pos += 4 + blen
        plen = data[pos]
        pname = data[pos + 1:pos + 1 + plen].decode('latin-1')
        pos += 1 + plen
        pos += (-(1 + plen)) % 4
        name, section = pname, None
        while pos + 12 <= extra_end:
            asig, akey = data[pos:pos + 4], data[pos + 4:pos + 8]
            alen, = struct.unpack('>I', data[pos + 8:pos + 12])
            body = data[pos + 12:pos + 12 + alen]
            if akey == b'luni':
                ln, = struct.unpack('>I', body[:4])
                name = body[4:4 + ln * 2].decode('utf-16-be')
            elif akey == b'lsct':
                section, = struct.unpack('>I', body[:4])
            pos += 12 + alen + (alen % 2)
        pos = extra_end
        layers.append(dict(name=name, bbox=[left, top, right, bottom], opacity=opacity,
                           visible=not bool(flags & 2), blend=key.decode('latin-1'),
                           has_mask=mlen > 0, section=section))
    return dict(width=width, height=height, depth=depth, mode=mode, channels=channels,
                layer_count=count, layers=layers, resource_ids=resource_ids,
                has_icc_profile=1039 in resource_ids)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    info = read_psd_layers(sys.argv[1])
    print(f"{info['width']}x{info['height']} depth={info['depth']} mode={info['mode']} layers={info['layer_count']}")
    groups = [l for l in info['layers'] if l['section'] in (1, 2, 3)]
    print('penanda grup (lsct 1/2/3):', len(groups))
    print('layer dengan mask:', sum(l['has_mask'] for l in info['layers']))
    print('ICC profile tertanam (resource 1039):', info['has_icc_profile'])
    print('visible/hidden:', sum(l['visible'] for l in info['layers']), '/', sum(not l['visible'] for l in info['layers']))
    if '--json' in sys.argv:
        out = sys.argv[sys.argv.index('--json') + 1]
        json.dump(info, open(out, 'w'), ensure_ascii=False, indent=1)
