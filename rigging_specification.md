# Spesifikasi Rigging Live2D — Aoi Cetara

Dokumen ini adalah **spesifikasi**, bukan model. Tidak ada ArtMesh, deformer, keyform, physics, atau ekspor yang sudah dibuat; Cubism Editor tidak tersedia di lingkungan pengerjaan. Seluruh isi bagian rancangan berstatus `PROPOSED`.

**Legenda status:** `VERIFIED` = diperiksa langsung dari berkas aset atau dokumentasi resmi; `PROPOSED` = rancangan yang belum diterapkan; `BLOCKED` = belum dapat dikerjakan (alasan dicantumkan); `COMPLETED` = benar-benar selesai dan diuji.

Dokumen pendamping: [asset_audit.md](asset_audit.md), [parameter_map.csv](parameter_map.csv), [deformer_plan.csv](deformer_plan.csv), [physics_plan.csv](physics_plan.csv), [expression_plan.csv](expression_plan.csv), [layer_mapping.csv](layer_mapping.csv), [rigging_checklist.md](rigging_checklist.md), [validation_report.md](validation_report.md).

## 0. Status pekerjaan

| Pekerjaan | Status | Catatan |
| --- | --- | --- |
| Audit aset dan layer | COMPLETED | Dijalankan dengan skrip yang dapat diulang; hasil di asset_audit.md |
| Spesifikasi rigging (dokumen ini + 5 CSV) | COMPLETED sebagai dokumen | Isinya PROPOSED sampai diterapkan di Cubism |
| Perbaikan artwork (overlap, pecah rambut, pasang komponen wajah, naikkan resolusi) | BLOCKED | Butuh editor gambar/ilustrator; bukan pekerjaan skrip |
| Impor PSD ke Cubism, ArtMesh, clipping | BLOCKED | Cubism Editor tidak tersedia |
| Deformer dan keyform | BLOCKED | Sama |
| Physics di Editor | BLOCKED | Template v1 belum diuji pada rig |
| Ekspor `.moc3` / `.model3.json` | BLOCKED | Dibuat hanya oleh Cubism Editor |
| Uji di VTube Studio | BLOCKED | Model runtime belum ada |

**Kesimpulan kesiapan:** artwork belum siap rigging (lihat asset_audit.md, 10 temuan P0). Jangan memulai keyform sebelum tahap perbaikan artwork selesai.

## 1. Dasar, sumber, dan asumsi

### 1.1 Sumber yang dibaca langsung (2026-10-17)

| Sumber | Dipakai untuk | Status |
| --- | --- | --- |
| Live2D, *Standard Parameter List* (Cubism Editor 5), docs.live2d.com/en/cubism-editor-manual/standard-parameter-list/ | ID, rentang, default, arah nilai semua parameter standar | VERIFIED |
| Live2D, *Notes on PSD creation* (diperbarui 2025-08-26), docs.live2d.com/en/cubism-editor-manual/precautions-for-psd-data/ | Syarat PSD impor: RGB, 8-bit, sRGB, tanpa layer mask, nama unik; hanya Photoshop dan Clip Studio Paint yang dijamin | VERIFIED |
| VTube Studio wiki, *Loading your own Models* | VTS mencari `.model3.json`; physics harus diekspor bersama model agar terdaftar; `.cdi3.json` tidak dibutuhkan; VTS membuat `.vtube.json` sendiri; auto-setup mencari ID parameter standar | VERIFIED |
| VTube Studio wiki, *VTS Model Settings* | Daftar input parameter: `FaceAngleX/Y/Z`, `MouthOpen`, `MouthSmile`, `EyeLeftX/Y`, `EyeRightX/Y`, `VoiceVolume`, `VoiceVolumePlusMouthOpen`, `VoiceFrequency`, `VoiceFrequencyPlusMouthSmile`, `VoiceA/I/U/E/O` | VERIFIED |
| Dokumentasi SDK dan parser pihak ketiga untuk `physics3.json` | Skema: `Input` (Source, Weight, Type, Reflect), `Output` (Destination, VertexIndex, Scale, Weight, Type, Reflect), `Vertices`, `Normalization` | Sebagian VERIFIED (halaman spesifikasi resmi di GitHub tidak berhasil dibuka) |

### 1.2 Hal yang tidak berhasil diverifikasi

- Batas versi Cubism Core pada VTube Studio. Satu proyek pihak ketiga menyebut inti VTS berhenti di SDK 5.0; ini tidak diverifikasi dari sumber resmi. Cek catatan rilis VTS sebelum memilih target SDK saat ekspor, dan hindari fitur Editor yang lebih baru dari target tersebut (Live2D menerbitkan halaman "Notes on model creation using the new functions of Cubism 5.3").
- Nama input tracker untuk kedipan dan alis (`EyeOpenLeft`, `EyeOpenRight`, `Brows`) berasal dari panduan v1 dan tidak ada di halaman VTS yang saya baca.
- Konvensi sisi "L/R" pada VTS: dokumentasi Live2D tidak menyatakan apakah `ParamEyeLOpen` adalah mata kiri anatomi atau kiri layar. Proyek memakai konvensi anatomi (L = kanan layar; **VERIFIED** konsisten pada 39 pasangan layer). Uji dengan wink nyata di VTS dan balik pemetaan bila terbalik.
- Apakah Cubism Editor dapat mengimpor `physics3.json` yang sudah ada. Rencana: bangun physics langsung di Editor dengan template v1 sebagai referensi, bukan sebagai berkas impor.

### 1.3 Keputusan yang diperlukan dari pemilik proyek

| ID | Keputusan | Rekomendasi |
| --- | --- | --- |
| K1 | Skala kanvas kerja (kanvas sekarang 1024x1536; wajah 110x145 px) | Naikkan kanvas 2–3x sebelum rigging bila model dipakai setengah badan; pakai komponen Highres untuk wajah |
| K2 | Polaritas alis | Ikuti standar resmi: nilai negatif = marah (bagian 3.2) |
| K3 | Vokal | Ganti `ParamMouthVowel` dengan lima parameter `ParamMouthA/I/U/E/O` (fase 2) |
| K4 | Aksesori kaki sisi kanan | Konfirmasi apakah asimetri disengaja |
| K5 | Target versi SDK `.moc3` | Tentukan setelah memeriksa versi VTS yang dipakai |
| K6 | Sumber suara AI dan jalurnya ke VTS | Tentukan perangkat audio virtual atau jalur API (bagian 8) |

## 2. Hierarki model

### 2.1 Tiga tingkat penamaan

Cubism membuat ArtMesh dari layer saat impor PSD, sehingga nama ArtMesh = nama layer. Untuk menghindari kebingungan, tabel di [layer_mapping.csv](layer_mapping.csv) memisahkan:

| Tingkat | Isi | Status |
| --- | --- | --- |
| Nama layer asli | 113 layer di PSD/manifest | VERIFIED |
| Nama ArtMesh diusulkan | Sama dengan nama layer, kecuali layer yang harus dipecah (mis. `HAIR_BACK_RIGHT` menjadi beberapa helai bernama baru setelah artwork dipecah) | PROPOSED |
| ArtMesh yang benar-benar dibuat | Tidak ada (kolom `artmesh_sudah_ada` = TIDAK) | BLOCKED |

### 2.2 Struktur Parts (folder organisasi, rancangan)

| Part | Isi (layer asli) |
| --- | --- |
| PART_HAIR_BACK | `BF_HAIR_BACK_COMPLETE`, `HAIR_BACK_*`, `HAIR_TIP_*`, `HAIR_STAR_*` |
| PART_SKIRT_BACK | `SKIRT_BACK_*`, `TRAIN_*`, `TRAIN_GEM_*` |
| PART_BACKFILL_BODY | `BF_LOWER_SKIRT`, `BF_NECK_AND_TORSO`, `BF_CLOTHING_BODY` |
| PART_LEGS | `LEG_*`, `SHOE_*`, `THIGH_GARTER_LEFT`, `THIGH_JEWELS_LEFT` |
| PART_SKIRT_FRONT | `SKIRT_FRONT_*`, `OVERSKIRT_*`, `WAIST_CHAIN`, `WAIST_RIBBON_*` |
| PART_BODY | `TORSO_UPPER`, `NECK`, `BODICE`, `CHEST_*`, `COLLAR`, `NECK_RIBBON`, `NECK_PENDANT` |
| PART_ARM_R / PART_ARM_L | `ARM_*`, `HAND_*`, `SLEEVE_*`, `SLEEVE_FLOWER_*`, `BRACELET_*` |
| PART_FACE | `BF_FACE_COMPLETE`, `EAR_*`, `FACE`, `NOSE`, `ALT_BLUSH_*` |
| PART_EYE_R / PART_EYE_L | `EYE_WHITE_*`/`ALT_SCLERA_*`, iris, pupil, highlight/glint, kelopak/bulu mata |
| PART_BROWS | `EYEBROW_*`, `ALT_EYEBROW_FULL_*` |
| PART_MOUTH | `MOUTH_CLOSED_NEUTRAL`, `ALT_MOUTH_*`, `ALT_TEETH`, `ALT_TONGUE` |
| PART_HAIR_SIDE | `EARRING_*`, `HAIR_SIDE_*`, `HAIR_TRESS_*`, `HAIR_CHAIN_*` |
| PART_HAIR_FRONT | `HAIR_CROWN`, `BANG_*` |
| PART_HEAD_ACC | `HAIR_CLIP_RIGHT`, `TIARA`, `FOREHEAD_JEWEL`, `HAIR_FLOWER_*`, `WHALE_TAIL_ORNAMENT` |

Brief meminta struktur seperti BODY/HEAD/FACE/EYES/…; padanannya di atas. Layer yang diminta brief tetapi tidak ada di artwork (HEAD, EFFECTS, CAPE, dst.) dicatat di asset_audit.md T13 dan tidak dibuat-buat.

### 2.3 Rantai parent–child (rancangan; rincian di [deformer_plan.csv](deformer_plan.csv))

```
(root)
├─ D_BODY_Z (rotasi, BodyAngleZ)
│  └─ D_BODY_XY (warp, BodyAngleX/Y)
│     ├─ D_BREATH (warp, Breath) → dada, bodice, kerah, rantai/pita dada
│     ├─ D_NECK (warp, AngleX/Y/Z ikut)
│     ├─ D_ARM_L / D_ARM_R (warp)
│     ├─ D_SKIRT_C / D_SKIRT_L / D_SKIRT_R (warp, sway rok) → pita/rantai pinggang
│     └─ D_HEAD_Z (rotasi, AngleZ)
│        ├─ D_HEAD_XY (warp, AngleX/Y)
│        │  ├─ D_EYE_L/R → D_GAZE_L/R
│        │  ├─ D_BROW_L/R
│        │  ├─ D_MOUTH
│        │  ├─ D_HAIR_FRONT
│        │  ├─ anting, ornamen ekor paus, aksesori kepala kaku
│        ├─ D_HAIR_SIDE_L/R → D_HAIR_CHAIN_L/R
│        └─ D_HAIR_BACK_ROOT → D_HAIR_BACK_L/R → D_HAIR_TIP_*, D_HAIR_STAR_*
(root) └─ D_LEGS (kaki dikunci)
```

Perubahan dari rencana v1 (semua `PROPOSED`): badan dipecah menjadi rotasi Z dan warp XY; deformer leher, kaki, lengan, alis, dan rambut samping ditambahkan; rambut belakang dibagi kiri/kanan di bawah satu akar yang mengikuti kepala.

### 2.4 Urutan gambar (draw order) usulan

Kolom `urutan_gambar_diusulkan` di layer_mapping.csv memberi indeks 1 (paling belakang) sampai 113 (paling depan). Ringkasan blok:

| Indeks | Blok |
| --- | --- |
| 1–7 | Rambut belakang, ujung, hiasan bintang |
| 8–14 | Rok belakang, ekor gaun, permata ekor |
| 15–17 | Backfill rok bawah, leher-torso, pakaian badan |
| 18–23 | Kaki, sepatu, aksesori paha |
| 24–31 | Rok depan, rok luar, rantai/pita pinggang |
| 32–43 | Dada atas, leher, bodice, pita/rantai dada, kerah |
| 44–53 | Lengan, tangan, lengan baju, bunga, gelang |
| 54–60 | Wajah utuh, telinga, wajah, hidung, blush |
| 61–84 | Mata (putih → iris → pupil → highlight → kelopak bawah → kelopak atas; pengganti ALT tepat di atas aslinya) |
| 85–88 | Alis |
| 89–95 | Mulut (rongga → lidah → gigi → garis tertutup → bibir bawah → bibir atas) |
| 96–104 | Anting, rambut samping, helai, rantai rambut, rambut atas |
| 105–113 | Poni, jepit, tiara, permata dahi, bunga, ornamen ekor paus |

Status: `PROPOSED`. Saat ini tidak berpengaruh karena layer aktif tidak saling tumpang-tindih (asset_audit.md T1); urutan menjadi penting begitu overlap ditambahkan. Beberapa keputusan perlu uji visual: kaki di belakang rok depan tetapi di depan rok belakang; helai samping di depan lengan baju; rambut belakang di belakang lengan.

### 2.5 Masking dan clipping (rancangan)

| ArtMesh yang di-clip | Masker | Alasan |
| --- | --- | --- |
| `ALT_IRIS_FULL_*`, `ALT_PUPIL_FULL_*`, `ALT_GLINT_*` | `ALT_SCLERA_*` | Iris tidak boleh keluar sclera; hilang saat mata tertutup |
| `ALT_TEETH`, `ALT_TONGUE` | `ALT_MOUTH_INSIDE` | Interior tersembunyi saat mulut tertutup |
| `ALT_BLUSH_*` | `FACE` (setelah diganti wajah utuh) | Blush tidak keluar dari kontur pipi |

Impor PSD tidak membawa clipping: Cubism mengharuskan layer mask dan clipping dilebur sebelum impor, sehingga masker dibuat ulang di Editor. Clipping tidak dipakai pada rambut atau pakaian.

## 3. Parameter

Tabel lengkap 40 baris (22 standar + 1 vokal v1 + 5 vokal baru + 12 sway) ada di [parameter_map.csv](parameter_map.csv) dengan kolom nama, ID, rentang, default, bagian terpengaruh, deformer, jumlah keyform, perilaku ekstrem, metode uji, sumber input, dan status.

### 3.1 Ringkasan

| Kelompok | Parameter | Asal | Status |
| --- | --- | --- | --- |
| Kepala | `ParamAngleX/Y/Z` −30..30 | Standar | VERIFIED |
| Badan | `ParamBodyAngleX/Y/Z` −10..10, `ParamBreath` 0..1 | Standar | VERIFIED |
| Mata | `ParamEyeL/ROpen` 0..1 (default 1), `ParamEyeL/RSmile` 0..1, `ParamEyeBallX/Y` −1..1 | Standar | VERIFIED |
| Alis | `ParamBrowL/RY`, `Angle`, `Form` −1..1 | Standar | VERIFIED (arah diperbaiki, bagian 3.2) |
| Mulut | `ParamMouthOpenY` 0..1, `ParamMouthForm` −1..1 | Standar | VERIFIED |
| Pipi | `ParamCheek` 0..1 (default proyek 0) | Standar | VERIFIED |
| Vokal | `ParamMouthA/I/U/E/O` 0..1 | Kustom | PROPOSED (fase 2) |
| Sway | 12 parameter output physics, −1..1 | Kustom | PROPOSED |

Semua parameter memiliki keyform = **belum dibuat** (BLOCKED).

### 3.2 Keputusan dan koreksi terhadap v1

1. **Polaritas alis.** Standar resmi: `ParamBrowLAngle`, `ParamBrowRAngle`, `ParamBrowLForm`, `ParamBrowRForm` bernilai negatif untuk ekspresi marah; `ParamBrowLY/RY` positif = alis naik. Template v1 memakai +1 = marah dan −1 = sedih (terbalik dari standar). Usulan: marah = negatif, sedih = positif, dan `ANGRY`/`SAD` ditulis ulang (lihat [expression_plan.csv](expression_plan.csv)). Memakai arah standar juga menjaga kompatibilitas dengan auto-setup VTS yang mengasumsikan parameter standar.
2. **Vokal.** `ParamMouthVowel` (0..5, satu parameter berurutan) tidak cocok: interpolasi antar keyform menghasilkan bentuk campuran (mis. 1,5 = campuran A–I), dan VTS menyediakan input `VoiceA/I/U/E/O` terpisah (0–1). Ganti dengan lima parameter mandiri; semuanya fase 2.
3. **Arah sway.** Konvensi: nilai positif = bergerak ke kanan layar, sama seperti `ParamHairFront/Side/Back` standar.
4. **Default.** Mata terbuka (1), `ParamMouthOpenY` 0, `ParamMouthForm` 0, `ParamCheek` 0, alis 0, semua sway 0: ekspresi netral, tenang, mulut tertutup, tidak tersenyum (sesuai brief).
5. **Rentang ekstrem kepala.** Standar resmi menyarankan −45..45 bila ingin berputar lebih dari ±30; untuk Aoi tetap ±30 sampai backfill terbukti cukup.

### 3.3 Nilai awal dan kalibrasi

- ID, minimum, default, maksimum parameter standar adalah **VERIFIED** terhadap halaman resmi.
- Jumlah keyform adalah minimum yang diusulkan; tambahkan kunci hanya bila deformasi di antara dua kunci terlihat kaku. Kunci 0,25 pada `ParamMouthOpenY` ditambahkan hanya jika transisi tertutup–terbuka terasa mekanis.
- Amplitudo `ParamBodyAngle*` dan semua sway: perkiraan, ditentukan saat deformasi dibuat.
- Kepala dan badan tidak boleh menghasilkan distorsi wajah, celah, atau sambungan leher terputus pada ±30/±10 dan kombinasi diagonal. Jika gagal, turunkan rentang sementara sebelum menambah artwork.

## 4. Deformer dan ArtMesh

Rencana lengkap (41 deformer, dengan induk, jenis, parameter, pivot, keyform, kepadatan mesh, risiko, validasi) ada di [deformer_plan.csv](deformer_plan.csv). Pivot mata, mulut, dan alis **VERIFIED** dari bbox layer; pivot lain berasal dari v1 atau manifest dan harus disesuaikan di Editor (sistem koordinat manifest: piksel sumber, titik nol kiri atas).

### 4.1 Rantai kepala

| Objek | Parent | Jenis | Parameter | Keyform | Risiko | Validasi |
| --- | --- | --- | --- | --- | --- | --- |
| Kepala, wajah, telinga, hidung | D_HEAD_Z → D_HEAD_XY | Rotasi lalu Warp | AngleZ; AngleX/Y | 3; 3x3 | Distorsi kontur pipi/dagu, celah rambut | Sapu ±30 dan 8 diagonal |
| Leher | D_NECK | Warp | AngleX/Y/Z (ikut) | 3x3 + 3 | Leher terputus dari kerah | Kepala diagonal, kerah menutup sambungan |
| Rambut belakang (akar) | D_HAIR_BACK_ROOT | Warp | AngleX/Y | 3x3 | Rambut tertinggal dari kepala | Diagonal kepala |

### 4.2 Mata dan alis

| Objek | Parent | Jenis | Parameter | Keyform | Risiko | Validasi |
| --- | --- | --- | --- | --- | --- | --- |
| Sclera, kelopak, bulu mata (kiri/kanan) | D_EYE_L/R | Warp | `ParamEyeL/ROpen`, `ParamEyeL/RSmile` | 3x2 = 6 | Bocor putih mata saat tutup | Sapu Open x Smile, zoom 400% |
| Iris, pupil, glint | D_GAZE_L/R (anak D_EYE) | Warp | `ParamEyeBallX/Y` | 3x3 | Iris keluar sclera | Sapu X/Y pada mata terbuka dan setengah |
| Alis | D_BROW_L/R | Warp | `ParamBrow*Y/Angle/Form` | 3 per parameter | Alis menembus poni | Sapu tiap parameter |

Iris dan pupil aktif terpotong (asset_audit.md T4); rig harus memakai komponen penuh `ALT_*` dengan clipping ke `ALT_SCLERA_*`. Bagian dalam sclera di bawah kelopak bagian atas harus ada saat kelopak terangkat.

### 4.3 Mulut

| Objek | Parent | Jenis | Parameter | Keyform | Risiko | Validasi |
| --- | --- | --- | --- | --- | --- | --- |
| Bibir atas/bawah, rongga, gigi, lidah | D_MOUTH | Warp | `ParamMouthOpenY`, `ParamMouthForm` (+ vokal fase 2) | 3x3 = 9 (+2 per vokal) | Interior bocor saat Open=0; bibir menyatu | Grid 3x3, Open=0 tertutup netral |

Syarat: pada `ParamMouthOpenY` = 0 dan `ParamMouthForm` = 0 mulut tertutup tanpa senyum; interior, gigi, dan lidah tidak terlihat. Komponen mulut pada kanvas sangat kecil (bibir 22x5 dan 17x4 px): wajib memakai versi Highres atau menaikkan skala kanvas sebelum membuat keyform.

### 4.4 Rambut

| Objek | Parent | Jenis | Parameter | Keyform | Risiko | Validasi |
| --- | --- | --- | --- | --- | --- | --- |
| `BANG_*`, `HAIR_CROWN` | D_HAIR_FRONT | Warp | `ParamHairFrontSway` | 3 | Poni menutup mata | Sway ±1 sebelum physics |
| `HAIR_SIDE_*`, `HAIR_TRESS_*` | D_HAIR_SIDE_L/R | Warp | `ParamHairSideL/RSway` | 3 | Tembus pipi/bahu | Cek terhadap `FACE` dan `SLEEVE_*` |
| `HAIR_BACK_*` (pecah 3–5 helai/sisi), tips | D_HAIR_BACK_L/R → D_HAIR_TIP_* | Warp, Rotasi | `ParamHairBackL/RSway` | 3 | Helai terpisah dari akar, potongan x=512 | Sway ±1, cek pangkal di balik leher |

### 4.5 Badan, pakaian, aksesori

| Objek | Parent | Jenis | Parameter | Keyform | Risiko | Validasi |
| --- | --- | --- | --- | --- | --- | --- |
| Bodice, dada, kerah | D_BREATH | Warp | `ParamBreath` | 2 | Rantai/pita terlepas | Loop napas 4 s |
| Lengan, tangan, lengan baju, gelang | D_ARM_L/R | Warp | `ParamBodyAngle*` | 3x3 | Celah di bahu | Sapu badan ±10 |
| Rok depan/luar/ekor/belakang | D_SKIRT_C/L/R | Warp | `ParamSkirtL/RSway`, `ParamBodyAngleX` | 3 | Kain menembus kaki; seam antar lapis | Sway ±1, cek terhadap kaki |
| Kaki, sepatu, aksesori paha | D_LEGS | Warp | dikunci | 1 | Pangkal paha terlihat saat rok bergerak | Sway rok ±1 |
| Pita, rantai, liontin, anting, ornamen ekor paus | D_RIBBON_*, D_CHAIN_*, D_PENDANT_NECK, D_EARRING_*, D_WHALE_ORNAMENT | Rotasi | sway terkait | 3 | Menembus bodice/rambut | Sway ±1 |

### 4.6 Rekomendasi kepadatan mesh

Jumlah vertex final tidak ditetapkan sebelum ArtMesh dibuat dari artwork akhir (resolusi kanvas belum diputuskan). Tingkatan:

| Bagian | Kepadatan | Alasan |
| --- | --- | --- |
| Tepi kelopak, garis bibir, rongga mulut | Tinggi | Bentuk berubah besar pada bukaan kecil |
| Kontur wajah (pipi/dagu) | Sedang-tinggi | Kontur harus halus saat menoleh |
| Rambut panjang, kain panjang (`OVERSKIRT_*`, `TRAIN_*`) | Sedang di massa, tinggi di ujung/lipatan | Lengkung memanjang saat sway |
| Sclera, alis, bodice, lengan | Sedang | Deformasi ringan |
| Aksesori kaku (tiara, permata, bunga, kerah, gelang) | Rendah | Hanya ikut induk; mesh rapat tanpa manfaat |
| Iris, pupil, glint | Rendah | Translasi di dalam sclera |

### 4.7 ArtMesh yang membutuhkan pemisahan atau ekstensi

36 layer berprioritas P0 dan 44 berprioritas P1 tercantum di layer_mapping.csv (kolom `kebutuhan_pemisahan_atau_ekstensi` dan `tindakan`). Intinya: (1) overlap di seluruh seam; (2) pecah `HAIR_BACK_*`; (3) pasang komponen mata/mulut penuh; (4) selaraskan lima backfill; (5) ekstensi leher, lengan di bawah lengan baju, dan kaki di bawah rok; (6) gambar ulang potongan poligon di wajah/poni/rambut samping.

## 5. Physics

Tabel kelompok ada di [physics_plan.csv](physics_plan.csv) (kolom: grup, input, output, respons, redaman, objek, status, catatan). Ringkasan:

| Physics Group | Input | Output | Respons | Redaman | Catatan |
| --- | --- | --- | --- | --- | --- |
| HairFront | AngleX, AngleZ | ParamHairFrontSway | sedang-cepat, bandul pendek | tinggi | Amplitudo kecil; poni tidak boleh menutup mata |
| HairSideL / R | AngleX, AngleZ | ParamHairSideL/RSway | sedang | sedang | Perlu deformer baru; cegah tembus pipi |
| HairBackL / R | AngleX, AngleZ, BodyAngleX (ringan) | ParamHairBackL/RSway | lambat, bandul panjang | rendah | Pecah menjadi beberapa output per kelompok helai |
| Ribbon | AngleX, AngleZ, BodyAngleX | ParamRibbonSway | sedang | sedang-tinggi | Pertimbangkan pisah pita dada/pinggang |
| SkirtL / R | BodyAngleX, BodyAngleZ | ParamSkirtL/RSway | lambat | sedang | Amplitudo dibatasi agar tidak menembus kaki |
| EarringL / R | AngleX, AngleZ | ParamEarringL/RSway | cepat | sedang | Anting kecil, amplitudo rendah |
| Chain | AngleX, AngleZ, BodyAngleX | ParamChainSway | cepat | sedang | Tetap di depan bodice |
| WhaleOrnament | AngleX, AngleZ | ParamWhaleOrnamentSway | lambat-sedang | tinggi | Siluet identitas harus terjaga |

**Status nilai:** respons dan redaman di atas adalah arah (kualitatif); nilai numerik awal mengikuti template v1 (Delay 0,28–0,336; Acceleration 0,7; Mobility 0,58–0,72; Scale output 0,05–0,08) dan berstatus **perkiraan untuk diuji**. Pemetaan istilah dialog Editor ke field JSON belum diverifikasi.

**Hasil audit template v1 (VERIFIED):** 12 pengaturan, skema lengkap, hitungan meta cocok, semua ID parameter valid. Namun hanya 2 kombinasi input dan 3 profil bandul; rambut belakang/samping/depan identik; tidak ada `ParamAngleY`. Konsekuensinya semua rambut bergerak seragam, bertentangan dengan permintaan gerak natural.

**Mencegah rambut menembus wajah, aksesori, dan pakaian (PROPOSED):**
1. Batasi rentang keyform sway di sisi dalam (dekat pipi) lebih kecil daripada sisi luar.
2. Susun draw order agar helai samping berada di depan bahu dan di belakang poni.
3. Tambah keyform dorong ke luar pada sudut kepala ekstrem.
4. Bangun dan uji keyform sway pada −1/0/+1 secara manual sebelum menghubungkan physics.
5. Uji pada rotasi kepala ±30 dengan gerak cepat 0,3 detik dan diam 60 detik: tidak boleh bergetar berkepanjangan.
6. Jangan menambahkan physics pada objek kaku (tiara, permata, bunga, kerah, gelang, sepatu, bodice).

## 6. Ekspresi

Spesifikasi per parameter ada di [expression_plan.csv](expression_plan.csv).

### 6.1 Parameter model vs berkas ekspresi

| Perilaku | Mekanisme | Mengapa |
| --- | --- | --- |
| Kedipan, tatapan, sudut kepala/badan, bukaan mulut saat bicara | Parameter model, digerakkan tracking dan audio | Terus berubah; mengunci nilainya mematikan tracking |
| Emosi: HAPPY, SAD, ANGRY, SURPRISED, SHY, SMILE, WINK_L, WINK_R | Berkas `.exp3.json` terpisah | Pose tetap yang dipicu hotkey |
| TALKING | Parameter model (`ParamMouthOpenY`, fase 2 vokal), bukan berkas ekspresi | Bicara = audio; berkas yang mengunci mulut akan mematikan lip-sync |
| Satu kedipan | Motion (`Blink_Once_TEMPLATE.motion3.json`), bukan ekspresi | `BLINK.exp3.json` v1 menahan mata tertutup selama aktif |
| NEUTRAL | `DEFAULT.exp3.json` sebagai reset emosi | Bukan pengganti default parameter model |

### 6.2 Nilai ekspresi (perkiraan, harus dituning setelah keyform ada)

| Ekspresi | Parameter utama | Catatan |
| --- | --- | --- |
| NEUTRAL | Semua emosi 0 | Tenang, mulut tertutup, tidak tersenyum |
| HAPPY | MouthForm 0,85; EyeL/RSmile 1; BrowY 0,15 | Nilai v1 dipertahankan |
| SAD | MouthForm −0,5; BrowAngle 0,7; BrowY −0,2 | Polaritas alis dikoreksi |
| ANGRY | MouthForm −0,3; BrowAngle −0,8; BrowForm −0,6; BrowY −0,2 | Polaritas alis dikoreksi |
| SURPRISED | BrowY 0,8; MouthOpenY 0,55; MouthForm −0,2 | Mengunci mulut: lepaskan segera atau pakai blend Add |
| WINK_L | EyeLOpen 0; EyeLSmile 0,6; MouthForm 0,25 | Mata kiri anatomi = kanan layar; uji konvensi VTS |
| WINK_R | EyeROpen 0; EyeRSmile 0,6; MouthForm 0,25 | Berkas baru, cermin WINK_L |

Ekspresi tidak boleh mengubah identitas dasar karakter: wajah tetap Aoi, hanya parameter alis/mata/bibir/pipi yang berubah.

**Uji transisi (`BLOCKED`, butuh model):** aktifkan lalu matikan tiap ekspresi: kembali ke netral tanpa residu; ulangi dengan lip-sync aktif dan kepala menoleh ±30; aktifkan dua ekspresi berurutan (parameter yang sama saling menimpa, jadi aktifkan satu emosi pada satu waktu).

## 7. Lip-sync dan tracking

### 7.1 Volume vs fonem

| | Berbasis volume | Berbasis fonem |
| --- | --- | --- |
| Cara kerja | Mengukur keras suara, menghasilkan satu nilai 0–1 | Mengklasifikasi suara menjadi vokal/viseme A, I, U, E, O |
| Parameter | `ParamMouthOpenY` | `ParamMouthA/I/U/E/O` (kustom) |
| Kebutuhan model | Grid Open x Form | Keyform tambahan per vokal |
| Kelebihan | Sederhana, stabil, bekerja untuk suara apa pun termasuk suara AI | Bentuk mulut lebih ekspresif |
| Kekurangan | Hanya buka-tutup; tidak ada bentuk vokal | Akurasi deteksi bervariasi; jumlah keyform lebih banyak |

### 7.2 Pilihan implementasi

1. **Fase 1 (awal, paling praktis):** volume. Petakan `VoiceVolumePlusMouthOpen` (input terdaftar di wiki VTS, **VERIFIED**) ke `ParamMouthOpenY`. `ParamMouthForm` dibiarkan dikendalikan ekspresi atau kamera; pemetaan `VoiceFrequencyPlusMouthSmile` ke `ParamMouthForm` berisiko membuat senyum berubah-ubah mengikuti frekuensi suara, uji sebelum dipakai.
2. **Fase 2:** fonem. Petakan `VoiceA/I/U/E/O` (**VERIFIED** terdaftar) ke lima parameter vokal setelah keyform dibuat dan kualitas deteksi pada suara AI terbukti baik.
3. **Suara AI (`PROPOSED`, belum diuji):** arahkan keluaran suara AI ke perangkat audio virtual yang dipilih sebagai mikrofon VTS, atau gunakan jalur API plugin VTS bila tersedia; jalur mana yang dipakai bergantung pada sistem operasi dan software suara (keputusan K6).

### 7.3 Perilaku yang diminta

| Perilaku | Kebutuhan pada model | Konfigurasi | Status |
| --- | --- | --- | --- |
| Kedipan otomatis | Keyform `ParamEyeL/ROpen` 0–1 tanpa kebocoran | Tracking kamera, atau `Blink_Once_TEMPLATE.motion3.json` yang dipicu hotkey/timer (mekanisme VTS belum diverifikasi) | BLOCKED |
| Gerakan pupil | Keyform `ParamEyeBallX/Y` + clipping sclera | `EyeLeftX/Y`, `EyeRightX/Y` (hanya bila tracker mendukung) | BLOCKED |
| Tracking sudut kepala | Keyform AngleX/Y/Z + backfill | `FaceAngleX/Y/Z` | BLOCKED |
| Tracking tubuh | Keyform BodyAngle* | Turunan dari kepala atau tidak dipetakan | BLOCKED |
| Mulut mengikuti volume | Grid Open x Form | `VoiceVolumePlusMouthOpen` atau `MouthOpen` | BLOCKED |
| Sinkron suara AI | Seperti di atas + jalur audio | Bagian 7.2 butir 3 | BLOCKED |
| Transisi ekspresi | Keyform alis/mata/mulut/pipi | Hotkey VTS memicu `.exp3.json` | BLOCKED |
| Idle saat tidak ada aktivitas | `ParamBreath` 0–1 | `Breath_Idle_TEMPLATE.motion3.json` (loop 4 s) | BLOCKED |

Memiliki nama parameter tidak berarti model bisa melakukan tracking: setiap perilaku di atas baru berlaku setelah keyform, deformasi, konfigurasi, dan uji runtime ada.

## 8. Ekspor dan kompatibilitas

| Berkas | Fungsi | Status |
| --- | --- | --- |
| `Aoi_Cetara.cmo3` | Proyek sumber Cubism (tidak dimuat VTS) | BLOCKED |
| `Aoi_Cetara.moc3` | Model runtime | BLOCKED |
| `Aoi_Cetara.model3.json` | Indeks model; VTS mencari berkas ini | BLOCKED: harus dibuat Cubism, tidak boleh ditulis tangan |
| `texture_00.png` dst. (atlas) | Tekstur yang direferensikan `.model3.json` | BLOCKED: dibuat saat ekspor |
| `Aoi_Cetara.physics3.json` | Physics | BLOCKED: harus diekspor bersama model agar terdaftar di `.model3.json` (VERIFIED dari wiki VTS); template v1 bukan pengganti |
| `*.exp3.json`, `*.motion3.json` | Ekspresi dan motion | Template v1 ada; BLOCKED sampai parameter dan keyform ada |
| `Aoi_Cetara.cdi3.json` | Nama tampilan parameter | Tidak dibutuhkan VTS (VERIFIED); opsional |
| `Aoi_Cetara.vtube.json` | Konfigurasi VTS | Dibuat VTS otomatis saat model dimuat; jangan ditulis tangan |
| Preview dan dokumentasi | Pengecekan | Preview v1 ada; tidak membuktikan model bergerak |

**Struktur folder ekspor yang diusulkan (`PROPOSED`, belum dibuat):** satu folder `Aoi_Cetara/` berisi `.moc3`, `.model3.json`, `.physics3.json`, atlas PNG, `expressions/`, `motions/`; letakkan di `Live2DModels` VTS. Berkas sumber (`.cmo3`, PSD final) disimpan terpisah.

**Catatan kompatibilitas:** pilih target SDK `.moc3` setelah memeriksa versi VTS (butir 1.2); ekspor physics bersama model; periksa ulang ekspresi dan motion pada model hasil ekspor; setelah ekspor jalankan `scripts/check_export_bundle.py` untuk memeriksa bahwa semua berkas yang direferensikan `.model3.json` benar-benar ada. Live2D juga menyediakan alat verifikasi konsistensi `.moc3` (halaman "Verification Tool" di manual Editor; isinya belum saya baca).

Jangan menyatakan model dapat dibuka di VTS sebelum diuji di VTS.

## 9. Prosedur validasi dan pengujian

Hasil pengujian yang sudah dijalankan ada di [validation_report.md](validation_report.md).

| ID | Uji | Prosedur | Kriteria lulus | Status |
| --- | --- | --- | --- | --- |
| V01 | Integritas paket | `audit_assets.py` (SHA256SUMS) | 178/178 cocok | COMPLETED |
| V02 | Manifest vs PNG | `audit_assets.py` | 113 PNG 1024x1536, tidak kosong, bbox cocok | COMPLETED |
| V03 | Struktur PSD vs syarat impor | `psd_inspect.py`, `audit_assets.py` | RGB, 8-bit, tanpa mask, nama unik | COMPLETED (impor nyata BLOCKED) |
| V04 | Overlap dan seam | `audit_assets.py` | Overlap > 0 di setiap seam yang bergerak | COMPLETED; hasil: GAGAL (0 piksel overlap) |
| V05 | Rekomposisi vs master | `audit_assets.py` | Beda 0 | COMPLETED; hasil: LULUS |
| V06 | Referensi parameter template | `audit_assets.py` | Semua ID ada di Parameter_Spec | COMPLETED; hasil: LULUS |
| V07 | Dokumen keluaran | `validate_outputs.py` | Semua cek lulus | COMPLETED (lihat validation_report.md) |
| V10 | PSD terbuka di Cubism tanpa galat | File → Open | Semua layer menjadi ArtMesh | BLOCKED |
| V11 | Kedipan | Sapu `ParamEyeL/ROpen` 0..1 | Tutup penuh tanpa sclera/iris | BLOCKED |
| V12 | Tatapan | Sapu `ParamEyeBallX/Y` pada Open 1 dan 0,5 | Iris tetap di dalam sclera | BLOCKED |
| V13 | Alis | Sapu Y/Angle/Form | Tidak menembus poni; polaritas marah negatif | BLOCKED |
| V14 | Mulut | Grid Open x Form 3x3 | Open 0 tertutup netral; interior tidak bocor | BLOCKED |
| V15 | Kepala | Sapu ±30, 8 diagonal | Tidak ada celah; leher menyambung; wajah tidak terdistorsi | BLOCKED |
| V16 | Badan | Sapu ±10 | Kaki dan sepatu tetap; bahu menyambung | BLOCKED |
| V17 | Sway manual | −1/0/+1 tiap parameter sway | Tanpa celah; helai tidak terlepas dari akar | BLOCKED |
| V18 | Physics | Gerak kepala 0,3 s; idle 60 s | Mereda cepat; tidak bergetar | BLOCKED |
| V19 | Penetrasi | Kepala ±30 dengan physics aktif | Rambut/aksesori tidak menembus wajah atau pakaian | BLOCKED |
| V20 | Ekspresi | Aktif/nonaktif tiap `.exp3.json`, dengan lip-sync dan menoleh | Kembali ke netral tanpa residu | BLOCKED |
| V21 | Lip-sync volume | Putar suara AI | Menutup saat hening; tidak macet terbuka | BLOCKED |
| V22 | Lip-sync fonem | Ucapkan A, I, U, E, O | Bentuk benar; campuran tidak merusak bibir | BLOCKED |
| V23 | Ekspor | Export for Runtime + `check_export_bundle.py` | Semua berkas terreferensi ada | BLOCKED |
| V24 | Muat di VTS | Salin folder ke `Live2DModels` | Tanpa galat; tekstur dan physics termuat | BLOCKED |
| V25 | Konvensi L/R | Wink nyata di VTS | Mata yang benar menutup | BLOCKED |
| V26 | Tepi tekstur | Periksa di VTS tepi bergaris/halo pada ArtMesh | Tidak ada garis; bila ada, haluskan tepi (saran manual Live2D) | BLOCKED |

## 10. Otomasi

| Pekerjaan | Dapat diotomatisasi? | Status |
| --- | --- | --- |
| Audit folder, checksum, manifest, struktur PSD, seam/overlap, rekomposisi | Ya | COMPLETED (`audit_assets.py`, `psd_inspect.py`) |
| Validasi CSV/Markdown dan referensi silang dokumen | Ya | COMPLETED (`validate_outputs.py`) |
| Pemeriksaan kelengkapan paket ekspor (referensi `.model3.json`) | Ya | Skrip dibuat dan diuji hanya pada contoh sintetis; belum pada model nyata (`check_export_bundle.py`) |
| Pembuatan checklist pengujian | Ya | COMPLETED (rigging_checklist.md) |
| Retouch artwork, overlap, pecah rambut | Tidak (kerja gambar) | BLOCKED |
| ArtMesh, deformer, keyform, physics, ekspor | Tidak lewat Python; hanya di Cubism Editor | BLOCKED |
| Otomasi Editor lewat integrasi API eksternal | Tidak dievaluasi: manual Editor memuat halaman "External Application Integration" tetapi kemampuannya untuk rigging tidak diverifikasi dan tidak dipakai | Tidak dikerjakan |

Skrip tidak memakai library di luar numpy dan Pillow; tidak ada API yang dikarang.

## 11. Risiko utama

1. Tanpa overlap dan pemecahan rambut belakang, gerakan kepala/rambut akan menampilkan celah (T1–T3).
2. Resolusi kanvas membatasi kualitas wajah dan mulut (T5, T6).
3. Polaritas alis v1 terbalik; jika tidak dikoreksi sebelum keyform, ekspresi dan auto-setup VTS menjadi membingungkan.
4. PSD hasil skrip mungkin tidak terimpor sempurna; simpan ulang via Photoshop/CSP.
5. Batas versi SDK pada VTS belum diverifikasi.
6. Template physics v1 membuat semua rambut bergerak seragam.
