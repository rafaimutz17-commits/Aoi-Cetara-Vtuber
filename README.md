# Aoi Cetara — Paket Spesifikasi Rigging Live2D

Paket ini berisi audit aset, spesifikasi rigging, tabel perencanaan, dan skrip pemeriksa untuk proyek `Aoi_Cetara_Production_v1.zip`.

**Ini bukan model Live2D.** Tidak ada `.cmo3`, `.moc3`, `.model3.json`, atau atlas runtime. Cubism Editor tidak tersedia saat pekerjaan ini dibuat, sehingga semua tahap yang memerlukannya berstatus BLOCKED. Model belum pernah dibuka di Cubism maupun VTube Studio.

Legenda status yang dipakai di seluruh dokumen: `VERIFIED` (diperiksa langsung dari aset/dokumentasi resmi), `PROPOSED` (rancangan), `BLOCKED` (belum bisa dikerjakan, dengan alasan), `COMPLETED` (selesai dan diuji).

## Kesimpulan singkat

- Artwork belum siap rigging. Format PSD memenuhi syarat teknis impor, tetapi 86 layer aktif tidak punya overlap sama sekali, rambut belakang hanya dua massa besar dengan potongan lurus, komponen mata aktif terpotong, mulut hanya satu garis, dan resolusi kanvas rendah untuk wajah. Rincian: `asset_audit.md`.
- Spesifikasi v1 yang ada perlu dikoreksi: polaritas alis terbalik terhadap standar resmi, deformer alis/rambut samping/leher/kaki tidak ada, template physics seragam. Rincian: `rigging_specification.md`.

## Isi folder

| Berkas | Isi |
| --- | --- |
| `README.md` | Panduan ini |
| `asset_audit.md` | Hasil audit, 13 temuan, inventaris 179 berkas |
| `rigging_specification.md` | Spesifikasi lengkap: hierarki, parameter, deformer, physics, ekspresi, lip-sync, ekspor, validasi |
| `parameter_map.csv` | 40 parameter: ID, rentang, default, deformer, keyform, uji, status |
| `deformer_plan.csv` | 41 deformer: induk, jenis, parameter, pivot, keyform, risiko, validasi |
| `physics_plan.csv` | 15 baris kelompok physics dan benda kaku |
| `expression_plan.csv` | Ekspresi per parameter (28 baris) |
| `layer_mapping.csv` | 113 layer asli → fungsi rig, parent, clipping, urutan gambar, prioritas, tindakan |
| `rigging_checklist.md` | Daftar pekerjaan berurutan |
| `validation_report.md` | Pengujian yang dijalankan, hasil, dan kekurangan |
| `data/audit_results.json` | Data mentah audit (termasuk metrik per layer) |
| `scripts/` | `audit_assets.py`, `psd_inspect.py`, `validate_outputs.py`, `check_export_bundle.py` |

## Dependensi

- Python 3.9 atau lebih baru
- `numpy` dan `Pillow` (`pip install numpy Pillow`)
- Tidak ada library lain; pembaca PSD memakai modul standar saja

Skrip hanya membaca berkas; tidak mengubah proyek sumber.

## Menjalankan pipeline

1. Ekstrak `Aoi_Cetara_Production_v1.zip` ke folder kerja (jangan menimpa arsip asli).
2. Audit aset (ulangi setiap kali artwork berubah dan manifest diperbarui):

   ```
   python3 scripts/audit_assets.py <folder_proyek_terekstrak> --out data/audit_results.json
   ```

   Keluaran ringkas di terminal: checksum, manifest, overlap, PSD, konvensi L/R, referensi spesifikasi, dan artefak runtime.
3. Periksa struktur PSD saja:

   ```
   python3 scripts/psd_inspect.py <file.psd> [--json hasil.json]
   ```

4. Validasi paket dokumen ini (CSV, Markdown, referensi silang, tidak ada berkas runtime palsu):

   ```
   python3 scripts/validate_outputs.py . --project <folder_proyek_terekstrak>
   ```

5. Setelah Anda benar-benar mengekspor model dari Cubism Editor:

   ```
   python3 scripts/check_export_bundle.py <folder_ekspor> --params parameter_map.csv
   ```

   Skrip ini memeriksa bahwa semua berkas yang direferensikan `.model3.json` ada dan ID parameter dikenal. Skrip ini diuji hanya pada folder sintetis, bukan model nyata, dan tidak membuktikan model dapat dimuat di VTube Studio.

## Cara menguji skrip

- `audit_assets.py` dan `validate_outputs.py`: jalankan pada paket ini; `validate_outputs.py` mengeluarkan jumlah LULUS/GAGAL dan kode keluar 1 bila ada kegagalan. Hasil uji yang dijalankan tercatat di `validation_report.md`.
- `check_export_bundle.py`: buat folder kecil berisi `T.model3.json` yang mereferensikan berkas yang tidak ada; skrip harus melaporkan GAGAL dan kode keluar 1; lalu lengkapi berkasnya, skrip harus LULUS.

## Bagian yang tetap manual

Retouch artwork (overlap, pecah rambut, pasang komponen wajah, naikkan resolusi), simpan ulang PSD lewat Photoshop atau Clip Studio Paint, serta seluruh pekerjaan di Cubism Editor: ArtMesh, clipping, deformer, keyform, physics, ekspor. Konfigurasi VTube Studio dan uji tracking juga manual.

## Langkah berikutnya

Ikuti `rigging_checklist.md`: (1) putuskan K1–K6, (2) perbaiki artwork tahap A01–A13, (3) impor ke Cubism dan bangun rig, (4) ekspor dan jalankan `check_export_bundle.py`, (5) uji di VTube Studio.
