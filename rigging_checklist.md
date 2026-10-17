# Daftar Pekerjaan Berurutan — Aoi Cetara (artwork → model VTube Studio)

**Legenda status:** `VERIFIED` = diperiksa langsung; `PROPOSED` = rancangan/usulan yang menunggu keputusan atau penerapan; `BLOCKED` = belum bisa dikerjakan (alasan di kolom); `COMPLETED` = selesai dan diuji.

Urutan mengikuti ketergantungan: jangan mulai tahap berikutnya sebelum kriteria selesai tahap sebelumnya terpenuhi. Detail teknis: [rigging_specification.md](rigging_specification.md); temuan: [asset_audit.md](asset_audit.md); daftar per layer: [layer_mapping.csv](layer_mapping.csv).

## Sudah selesai

| ID | Pekerjaan | Bukti | Status |
| --- | --- | --- | --- |
| S1 | Ekstrak dan audit seluruh 179 berkas | `scripts/audit_assets.py`, `data/audit_results.json`, asset_audit.md | COMPLETED |
| S2 | Verifikasi independen PSD, manifest, PNG, checksum, ORA | asset_audit.md bagian 1 | COMPLETED (VERIFIED) |
| S3 | Verifikasi parameter standar dan syarat PSD terhadap dokumentasi resmi Live2D | rigging_specification.md bagian 1 | COMPLETED (VERIFIED) |
| S4 | Spesifikasi: parameter, deformer, physics, ekspresi, pemetaan layer | 5 berkas CSV + rigging_specification.md | COMPLETED sebagai dokumen; isinya PROPOSED |
| S5 | Skrip validasi dokumen dan pemeriksa paket ekspor | `scripts/validate_outputs.py`, `scripts/check_export_bundle.py` | COMPLETED (pemeriksa ekspor diuji hanya pada contoh sintetis) |

## Tahap 0 — Keputusan pemilik proyek

| ID | Keputusan | Dibutuhkan sebelum | Status |
| --- | --- | --- | --- |
| K1 | Skala kanvas kerja (1x, 2x, atau 3x dari 1024x1536) | A01 | PROPOSED |
| K2 | Setuju memakai polaritas alis standar (negatif = marah) | K04, E01 | PROPOSED |
| K3 | Setuju mengganti `ParamMouthVowel` dengan 5 parameter vokal (fase 2) | K02 fase 2 | PROPOSED |
| K4 | Aksesori kaki kanan: tambah atau tidak | A09 | PROPOSED |
| K5 | Versi VTube Studio yang dipakai → target SDK `.moc3` | X02 | PROPOSED |
| K6 | Sumber suara AI dan jalur audio ke VTS | L02 | PROPOSED |

## Tahap 1 — Perbaikan artwork (editor gambar: Photoshop atau Clip Studio Paint)

Semua tugas tahap ini `BLOCKED`: butuh kerja ilustrasi manual; lingkungan pengerjaan tidak menyediakan editor gambar dan perbaikan seperti ini tidak dapat diotomatisasi dengan aman.

| ID | Pekerjaan | Kriteria selesai | Prioritas |
| --- | --- | --- | --- |
| A01 | Terapkan skala kanvas (K1); gunakan komponen `Face_Components_Highres` untuk mata/mulut | Komponen wajah tidak buram pada ukuran tampil yang dituju | P0 |
| A02 | Tambah overlap di semua seam, mulai dari kontak terbesar (`TRAIN_*`/`OVERSKIRT_*`, `SKIRT_BACK_*`, `HAIR_BACK_*`/`HAIR_TIP_*`) | `audit_assets.py` melaporkan overlap > 0 pada seam yang bergerak | P0 |
| A03 | Pecah `HAIR_BACK_RIGHT/LEFT` menjadi 3–5 kelompok helai per sisi; hapus potongan lurus x=512 | Tidak ada garis potong lurus; tiap kelompok punya akar di bawah tetangga | P0 |
| A04 | Gambar ulang `HAIR_SIDE_*`, `BANG_*`, dan batas poligon di wajah | Tepi mengikuti bentuk helai; dahi dan pipi di balik poni terisi | P0 |
| A05 | Selaraskan lima backfill (offset awal y+20); jadikan `BF_FACE_COMPLETE` pengganti `FACE` | Kontur, shading, warna cocok; tidak ada tepi terlihat | P0 |
| A06 | Pasang sclera, iris, pupil, glint penuh; pilih satu versi kelopak/bulu mata; alis penuh | Tidak ada potongan di tepi saat dibandingkan dengan mata terbuka | P0 |
| A07 | Pasang set mulut (bibir atas/bawah, rongga, gigi, lidah) dari Highres | Mulut tertutup netral tanpa senyum; komponen terbuka tersedia | P0 |
| A08 | Ekstensi leher (atas dan bawah), lengan di bawah lengan baju, kaki di bawah rok, rok belakang tengah | Tidak ada tepi potong terlihat saat bagian digeser ±10% | P0 |
| A09 | Rapikan tepi aksesori tipis (rantai, anting, gantungan); putuskan aksesori kaki kanan (K4) | Tepi bersih pada perbesaran 400% | P2 |
| A10 | Letakkan blush di pipi dengan opacity default 0 | Blush tidak terlihat pada default | P1 |
| A11 | Atur opacity eksplisit untuk semua layer opsional/pengganti; sembunyikan versi lama | Tidak ada dua versi bagian yang sama tampil bersamaan setelah impor | P0 |
| A12 | Gabungkan lineart/warna per bagian; tanpa layer mask; RGB, 8-bit, sRGB; nama unik; simpan ulang via Photoshop/CSP sebagai file impor baru | Memenuhi syarat resmi Live2D untuk PSD impor | P0 |
| A13 | Perbarui manifest layer dan jalankan ulang `audit_assets.py` pada hasil | Laporan audit baru tanpa temuan P0 | P0 |

## Tahap 2 — Penyiapan model di Cubism Editor (`BLOCKED`: Cubism Editor tidak tersedia)

| ID | Pekerjaan | Kriteria selesai |
| --- | --- | --- |
| C01 | Impor PSD (V10); periksa jumlah ArtMesh dan opacity bagian opsional | Semua layer menjadi ArtMesh; tidak ada bagian ganda |
| C02 | Buat Parts sesuai rigging_specification.md bagian 2.2 | Struktur Parts rapi |
| C03 | Terapkan urutan gambar usulan (kolom `urutan_gambar_diusulkan`) dan uji visual | Tidak ada tumpang-tindih salah urut |
| C04 | Buat mesh dengan kepadatan sesuai bagian 4.6 | Mesh rapat hanya pada kelopak, bibir, ujung rambut/kain |
| C05 | Buat clipping (iris/pupil/glint ke sclera; gigi/lidah ke rongga; blush ke wajah) | Tidak ada bocor pada mata/mulut tertutup |

## Tahap 3 — Deformer (`BLOCKED`)

Urutan: kedipan dan mulut dulu, lalu kepala, badan, rambut, pakaian (mengikuti panduan v1), memakai [deformer_plan.csv](deformer_plan.csv).

| ID | Pekerjaan | Kriteria selesai |
| --- | --- | --- |
| D01 | Deformer mata, tatapan, alis, mulut | Rantai parent sesuai deformer_plan.csv |
| D02 | D_HEAD_Z, D_HEAD_XY, D_NECK | Pivot kepala benar |
| D03 | D_BODY_Z, D_BODY_XY, D_BREATH, D_ARM_L/R, D_LEGS | Kaki terkunci |
| D04 | Deformer rambut (depan, samping, belakang, ujung) | Memakai ArtMesh hasil pecah A03 |
| D05 | Deformer rok, pita, rantai, anting, ornamen | Titik pivot di akar benda |

## Tahap 4 — Keyform (`BLOCKED`)

| ID | Pekerjaan | Uji |
| --- | --- | --- |
| K01 | Kedipan: `ParamEyeL/ROpen` 0, 0,5, 1 dan `ParamEyeL/RSmile` | V11 |
| K02 | Mulut: grid `ParamMouthOpenY` x `ParamMouthForm` 3x3 (vokal fase 2 setelah lip-sync volume berfungsi) | V14 |
| K03 | Tatapan: `ParamEyeBallX/Y` | V12 |
| K04 | Alis dengan polaritas standar (negatif = marah) | V13 |
| K05 | Kepala: `ParamAngleX/Y/Z` dengan kunci empat sudut otomatis; turunkan rentang bila perlu | V15 |
| K06 | Badan dan napas: `ParamBodyAngle*`, `ParamBreath` | V16 |
| K07 | Sway manual −1/0/+1 untuk semua parameter sway sebelum physics | V17 |
| K08 | Pipi: opacity `ParamCheek` | V14 (blush) |

## Tahap 5 — Physics (`BLOCKED`)

| ID | Pekerjaan | Kriteria selesai |
| --- | --- | --- |
| P01 | Bangun grup di Editor mengikuti [physics_plan.csv](physics_plan.csv); rambut tidak identik | Tiap kelompok punya profil sendiri |
| P02 | Tuning respons dan redaman; batasi amplitudo di sisi dalam | V18, V19 lulus |
| P03 | Pastikan benda kaku tidak diberi physics | Daftar kaku di physics_plan.csv |

## Tahap 6 — Ekspresi dan motion (`BLOCKED`)

| ID | Pekerjaan | Uji |
| --- | --- | --- |
| E01 | Tulis ulang ANGRY/SAD dengan polaritas standar; buat WINK_L dan WINK_R; perbaiki SURPRISED (jangan mengunci mulut) | V20 |
| E02 | Uji motion kedipan dan napas pada model nyata | V11, V16 |

## Tahap 7 — Lip-sync dan tracking (konfigurasi di VTube Studio; `BLOCKED`: model belum ada)

| ID | Pekerjaan | Uji |
| --- | --- | --- |
| L01 | Fase 1: `VoiceVolumePlusMouthOpen` → `ParamMouthOpenY` | V21 |
| L02 | Jalur audio suara AI ke VTS (K6) | V21 |
| L03 | Fase 2: `VoiceA/I/U/E/O` → parameter vokal bila kualitasnya baik | V22 |

## Tahap 8 — Ekspor (`BLOCKED`)

| ID | Pekerjaan | Kriteria selesai |
| --- | --- | --- |
| X01 | Simpan `.cmo3`; buat atlas tekstur | Atlas sesuai ukuran target |
| X02 | Pilih target SDK sesuai K5; Export For Runtime `.moc3` dengan physics, ekspresi, motion | Berkas ekspor lengkap |
| X03 | Jalankan `scripts/check_export_bundle.py` pada folder ekspor | Hasil LULUS |
| X04 | (Opsional) alat verifikasi konsistensi `.moc3` dari Live2D | Tanpa galat |

## Tahap 9 — Uji di VTube Studio (`BLOCKED`)

| ID | Pekerjaan | Uji |
| --- | --- | --- |
| T01 | Salin folder ekspor ke `Live2DModels`; muat | V24 |
| T02 | Jalankan auto-setup; periksa pemetaan parameter | — |
| T03 | Wink nyata untuk memverifikasi konvensi L/R | V25 |
| T04 | Kalibrasi kamera; periksa kepala, mata, mulut, alis | V15, V11, V12 |
| T05 | Bandingkan physics di VTS dengan di Editor | V18 |
| T06 | Periksa tepi tekstur (garis/halo) | V26 |

## Tahap 10 — QA akhir dan pembekuan

| ID | Pekerjaan | Kriteria selesai |
| --- | --- | --- |
| Q01 | Jalankan semua uji V10–V26; catat di validation_report.md | Semua lulus atau kekurangan terdokumentasi |
| Q02 | Ubah status dokumen menjadi `COMPLETED` hanya untuk yang benar-benar diuji | Tidak ada klaim "siap dipasang" sebelum T01 lulus |
