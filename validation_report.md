# Laporan Validasi — Aoi Cetara (spesifikasi rigging)

Tanggal: 2026-10-17. **Legenda status:** `VERIFIED` = diperiksa langsung; `PROPOSED` = rancangan; `BLOCKED` = belum dapat dikerjakan/diuji (alasan dicantumkan); `COMPLETED` = selesai dan diuji.

Laporan ini membedakan tiga hal: (A) pengujian yang benar-benar dijalankan, (B) kekurangan yang ditemukan pada aset, (C) pengujian yang tidak dapat dijalankan. **Tidak ada pengujian pada model Live2D, Cubism Editor, atau VTube Studio**, karena model runtime belum ada dan aplikasinya tidak tersedia.

## A. Pengujian yang dijalankan

| No. | Pengujian | Hasil | Status |
| --- | --- | --- | --- |
| A1 | Checksum SHA256 seluruh paket (`audit_assets.py`) | 178/178 cocok; 0 hilang; 0 tak terdaftar | COMPLETED |
| A2 | Manifest vs PNG layer | 113 baris; semua PNG 1024x1536; 0 kosong; bbox cocok 113/113 | COMPLETED |
| A3 | Struktur PSD (`psd_inspect.py`, ImageMagick) | 113 layer, 14 grup, 0 mask, RGB 8-bit, ICC tertanam, nama unik, visibilitas cocok manifest | COMPLETED |
| A4 | Dekode semua gambar dan CRC ORA | 144 gambar terdekode tanpa gagal; arsip ORA tanpa galat | COMPLETED |
| A5 | Rekomposisi 86 layer aktif vs master | beda alpha maks 0, beda RGB maks 0 pada 964.002 piksel | COMPLETED |
| A6 | Overlap antar layer aktif | 0 piksel overlap; 218 pasangan bersentuhan (HASIL: tidak memenuhi syarat animasi) | COMPLETED |
| A7 | Konvensi LEFT/RIGHT | 39 pasangan konsisten, 0 tidak konsisten | COMPLETED |
| A8 | Referensi parameter pada physics/ekspresi/motion/deformer v1 | Semua ID ada di Parameter_Spec.csv; skema physics lengkap; hitungan meta cocok | COMPLETED |
| A9 | Parameter standar vs halaman resmi Live2D | ID, min, default, max 22 parameter standar cocok; polaritas alis v1 TIDAK cocok | COMPLETED |
| A10 | Sintaks semua skrip (`py_compile`) | Lulus untuk 4 skrip yang disertakan | COMPLETED |
| A11 | `check_export_bundle.py` pada folder SINTETIS (lengkap, rusak, ID tak dikenal) | LULUS, GAGAL, GAGAL sesuai yang diharapkan; bukan model nyata | COMPLETED (hanya sintetis) |
| A12 | `validate_outputs.py` — uji negatif (5 kesalahan sengaja: ID parameter palsu, status tidak sah, berkas `.moc3` palsu, berkas hilang, parent yatim) | Kelima kesalahan terdeteksi | COMPLETED |
| A13 | `validate_outputs.py` pada paket akhir (10 berkas wajib + data) | LULUS 34, GAGAL 0, kode keluar 0 | COMPLETED |

## B. Kekurangan yang ditemukan (hasil audit, belum diperbaiki)

| ID | Kekurangan | Bukti | Prioritas | Status perbaikan |
| --- | --- | --- | --- | --- |
| B1 | Layer aktif tanpa overlap | 0 px overlap, 218 seam | P0 | BLOCKED (kerja gambar) |
| B2 | Potongan lurus x=512 dan y=1000 pada rambut/rok belakang; potongan poligon di wajah | bbox HAIR_BACK_* dan SKIRT_BACK_*; peta layer wajah | P0 | BLOCKED |
| B3 | Rambut belakang hanya dua massa besar | 81.304 dan 89.320 px | P0 | BLOCKED |
| B4 | Komponen mata aktif terpotong; pengganti penuh belum dipasang | iris 27x21 vs 28x28; pupil 9x12 vs 8x17 | P0 | BLOCKED |
| B5 | Mulut satu garis; komponen buka-mulut sangat kecil dan belum terpasang | bibir 22x5 dan 17x4 px | P0 | BLOCKED |
| B6 | Resolusi kanvas rendah untuk wajah; 22 PNG Highres di luar PSD | FACE 110x145 px | P0 | BLOCKED (keputusan K1) |
| B7 | Lima backfill belum diselaraskan; tidak ada backfill lengan/kaki | manifest: alignment required | P0 | BLOCKED |
| B8 | Leher hanya 84x42 px | bbox NECK | P0 | BLOCKED |
| B9 | PSD tidak dibuat Photoshop/CSP | README v1 dan dokumentasi Live2D | P0 | BLOCKED |
| B10 | Polaritas alis v1 terbalik terhadap standar resmi | ANGRY BrowLForm=1, SAD=-1; resmi negatif=marah | P0 | Dikoreksi di dokumen (PROPOSED); template v1 belum diubah |
| B11 | Parameter tanpa deformer pengendali pada rencana v1 | ParamBrowLAngle, ParamBrowLForm, ParamBrowLY, ParamBrowRAngle, ParamBrowRForm, ParamBrowRY, ParamCheek, ParamHairSideLSway, ParamHairSideRSway | P1 | Dikoreksi di deformer_plan.csv (PROPOSED) |
| B12 | Template physics v1 seragam | 2 kombinasi input, 3 profil bandul, tanpa AngleY | P1 | Diganti rencana di physics_plan.csv (PROPOSED) |
| B13 | Kaki saling bersentuhan dan berhenti di bawah rok | 504 px kontak; kaki mulai y=771 | P1 | BLOCKED |

## C. Pengujian yang tidak dapat dijalankan (BLOCKED)

| Pengujian | Alasan |
| --- | --- |
| Impor PSD ke Cubism (V10) | Cubism Editor tidak tersedia |
| Kedipan, tatapan, alis, mulut, kepala, badan, sway (V11–V17) | Belum ada ArtMesh, deformer, keyform |
| Physics: stabilitas, penetrasi (V18, V19) | Belum ada rig; template v1 belum diuji |
| Ekspresi dan transisi (V20) | Parameter belum memiliki keyform |
| Lip-sync volume dan fonem, suara AI (V21, V22) | Belum ada model; jalur audio AI belum ditentukan |
| Ekspor dan pemeriksa paket pada model nyata (V23) | Tidak ada `.moc3`/`.model3.json`; pemeriksa hanya diuji sintetis |
| Muat di VTube Studio, konvensi L/R, tepi tekstur (V24–V26) | VTube Studio tidak tersedia; model runtime belum ada |

## D. Keterbatasan validasi

- Pemeriksaan nama layer pada `deformer_plan.csv` bersifat longgar (pencocokan awalan); ia menangkap nama yang tidak dikenal, bukan semua kesalahan penempatan.
- Nilai numerik awal physics dan nilai ekspresi adalah perkiraan; tidak ada pengujian yang dapat memvalidasinya tanpa rig.
- Spesifikasi `physics3.json` resmi di GitHub tidak berhasil dibuka; skema dicek terhadap parser pihak ketiga dan dokumentasi SDK.
- Batas versi Cubism Core di VTube Studio dan nama input tracker untuk kedipan/alis tidak diverifikasi dari sumber resmi.
- Audit membaca profil ICC hanya sebagai keberadaan (resource 1039) dan ruang warna yang dilaporkan ImageMagick (sRGB); nama profil tidak diurai.
- Penilaian visual (potongan poligon, kualitas tepi) berdasarkan peta layer dan satu komposit; belum ada uji gerak.

## E. Kesimpulan

Dokumen dan skrip yang dibuat lulus validasi otomatis. Artwork **belum lulus** kesiapan rigging (B1–B9). Model runtime **belum ada**; tidak ada klaim bahwa model dapat dibuka di VTube Studio. Langkah berikutnya: `rigging_checklist.md` mulai dari tahap 0 (keputusan K1–K6) dan tahap 1 (perbaikan artwork).
