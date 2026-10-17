# Audit Aset Aoi Cetara — Persiapan Rigging Live2D

Tanggal audit: 2026-10-17. Sumber: `Aoi_Cetara_Production_v1.zip` (34.072.843 byte, 179 berkas), diekstrak ke folder kerja sementara; berkas sumber tidak diubah.

**Legenda status:** `VERIFIED` = diperiksa langsung dari berkas atau dokumentasi resmi; `PROPOSED` = rancangan, belum diterapkan; `BLOCKED` = belum bisa dikerjakan (alasan dicantumkan); `COMPLETED` = selesai dan diuji.

## 1. Kesimpulan

- **Artwork BELUM siap rigging.** Paket ini adalah artwork berlayer tahap awal dan template; bukan model Live2D. Format PSD memenuhi syarat teknis impor Cubism, tetapi pemisahan layer belum cukup untuk animasi (10 temuan prioritas P0 di bagian 3: T1–T8, T11, T12). Status audit: **COMPLETED**; status kesiapan rigging: **BLOCKED** sampai perbaikan artwork selesai.
- Tidak ada `.cmo3`, `.moc3`, `.model3.json`, atlas runtime, atau `.vtube.json` di paket (**VERIFIED**). Semua JSON lain adalah template yang belum diuji pada rig.
- Klaim paket v1 yang terbukti benar: 113 layer, ukuran kanvas seragam, tidak ada layer kosong, checksum utuh, PSD tanpa mask, komposit layer aktif identik dengan master pada piksel terlihat. Klaim yang perlu dikoreksi atau dilengkapi: lihat bagian 3 (T1, T2, T6, T12).

### Hasil pemeriksaan

| Pemeriksaan | Hasil | Status |
| --- | --- | --- |
| Checksum SHA256 | 178/178 cocok; tidak ada yang hilang atau tak terdaftar | VERIFIED |
| Dekode gambar | 144 gambar terdekode tanpa kegagalan (142 PNG: 135 layer termasuk 22 Highres, 6 sumber, 1 preview; 2 JPG) | VERIFIED |
| JSON | 20 berkas JSON diparse tanpa galat | VERIFIED |
| Manifest vs PNG | 113 baris; semua PNG 1024x1536; tidak ada layer kosong; bbox cocok manifest 113/113 | VERIFIED |
| PSD | RGB, 8-bit; 113 layer raster, 14 grup; mask 0; opacity [255]; blend ['norm']; nama unik; cocok manifest; ICC tertanam (ImageMagick: sRGB) | VERIFIED |
| ORA | CRC arsip valid; 117 entri | VERIFIED |
| Konvensi LEFT/RIGHT | 39 pasangan konsisten: LEFT = sisi kiri anatomi karakter = kanan layar | VERIFIED |
| Rekomposisi layer aktif vs master | Beda alpha maks 0, beda RGB maks 0 pada 964.002 piksel terlihat: 86 layer aktif menyusun ulang master persis | VERIFIED |
| Overlap antar layer aktif | 0 piksel dari 964.002 piksel tertutup; 218 pasangan layer bersentuhan | VERIFIED |
| Dibuat oleh Photoshop/CSP | Tidak: menurut README v1 dan skrip di 07_Tools, PSD dihasilkan skrip. Live2D hanya menjamin impor PSD dari Photoshop dan Clip Studio Paint | VERIFIED |
| Impor ke Cubism, deformasi, physics, VTube Studio | Tidak dapat diuji: Cubism Editor dan VTube Studio tidak tersedia | BLOCKED |

## 2. Metode dan lingkungan

- Skrip `scripts/audit_assets.py` dan `scripts/psd_inspect.py` (disertakan; dapat dijalankan ulang) membaca PNG dengan Pillow/numpy dan struktur PSD dengan pembaca stdlib tanpa mendekode piksel. Hasil mentah ada di `data/audit_results.json`.
- Pemeriksaan tambahan: ImageMagick (`identify`) untuk jumlah frame/layer PSD, `unzip -t` untuk ORA, inspeksi visual komposit dan peta layer wajah.
- Dokumentasi resmi dibaca pada 2026-10-17: Standard Parameter List dan Notes on PSD creation (docs.live2d.com, Cubism Editor 5), wiki VTube Studio (Loading your own Models, VTS Model Settings). Spesifikasi `physics3.json` resmi tidak berhasil dibuka langsung; skema diperiksa terhadap parser pihak ketiga dan dokumentasi SDK (lihat rigging_specification.md bagian 1).
- Tidak tersedia: Live2D Cubism Editor, VTube Studio, Photoshop/CSP. Jaringan dari lingkungan eksekusi dimatikan; pencarian web dipakai hanya untuk membaca dokumentasi.

## 3. Temuan utama

Prioritas: **P0** harus selesai sebelum rigging dimulai, **P1** diselesaikan saat rigging, **P2** poles.

### T1 (P0) — Layer aktif adalah partisi tanpa overlap
86 layer aktif tidak punya satu pun piksel yang tumpang-tindih (0 piksel). Setiap piksel karakter dimiliki tepat satu layer, dan 218 pasang layer saling bersentuhan. Begitu satu bagian bergerak (rambut, rok, lengan, kelopak), garis potong terbuka sebagai celah. Kontak terpanjang: TRAIN_RIGHT–OVERSKIRT_RIGHT (1.265 px); SKIRT_BACK_RIGHT–TRAIN_RIGHT (1.150 px); TRAIN_LEFT–OVERSKIRT_LEFT (915 px); SKIRT_BACK_LEFT–TRAIN_LEFT (914 px); HAIR_BACK_LEFT–HAIR_TIP_LEFT (653 px).
Tindakan: tambahkan overlap/ekstensi di setiap sambungan (akar helai ke bawah tetangga, tepi kain ke bawah lapis di atasnya). Ini artwork baru; belum dikerjakan (**BLOCKED**: butuh editor gambar).

### T2 (P0) — Potongan lurus dan poligon memotong objek
`HAIR_BACK_RIGHT` memiliki bbox x 0–512 dan `HAIR_BACK_LEFT` x 512–984 (keduanya y 0–1000); `SKIRT_BACK_RIGHT/LEFT` x 0–512/512–998 mulai tepat di y=1000. Rambut dan rok belakang dipotong oleh garis lurus di x=512 dan y=1000 yang tidak mengikuti bentuk. Peta layer area wajah menunjukkan batas poligon bersudut yang memotong wajah, poni, dan rambut samping. Tepi seperti ini akan terlihat saat deformasi; perlu digambar ulang.

### T3 (P0) — Rambut belakang hanya dua layer besar
`HAIR_BACK_RIGHT` (81.304 px alpha) dan `HAIR_BACK_LEFT` (89.320 px) masing-masing satu massa rambut, ditambah `HAIR_TIP_*`. Brief meminta rambut dengan banyak helai yang dapat digerakkan terpisah. Dengan dua massa, physics hanya bisa menggoyang seluruh sisi sekaligus. Perlu dipecah 3–5 kelompok helai per sisi dengan overlap akar–ujung (usulan di layer_mapping.csv).

### T4 (P0) — Mata: komponen aktif terpotong, pengganti penuh belum dipasang
Komponen mata aktif adalah potongan dari master dan terpotong kelopak. Pengganti penuh (`ALT_*`, tersembunyi) tersedia dan sejajar dengan komponen aktif (selisih pusat ≤ 2 px).

| Komponen | Aktif (lebar x tinggi px) | Pengganti ALT | Catatan |
| --- | --- | --- | --- |
| EYE_WHITE | 51x20 | ALT_SCLERA 50x28 | sisi kanan layar; sisi kiri layar serupa |
| IRIS | 27x21 | ALT_IRIS_FULL 28x28 | sisi kanan layar; sisi kiri layar serupa |
| PUPIL | 9x12 | ALT_PUPIL_FULL 8x17 | sisi kanan layar; sisi kiri layar serupa |
| HIGHLIGHT | 8x7 | ALT_GLINT 14x12 | sisi kanan layar; sisi kiri layar serupa |
| EYEBROW | 41x13 | ALT_EYEBROW_FULL 40x12 | sisi kanan layar; sisi kiri layar serupa |
| UPPER_EYELID | 59x16 | ALT_LASH_UPPER 52x15 | sisi kanan layar; sisi kiri layar serupa |
| LOWER_EYELID | 44x8 | ALT_LASH_LOWER 43x8 | sisi kanan layar; sisi kiri layar serupa |

Iris aktif (27x21) lebih pendek dari iris penuh (28x28), pupil aktif 9x12 dibanding 8x17, putih mata aktif 51x20 dibanding sclera 50x28. Saat bola mata bergerak atau mata menyipit, tepi terpotong akan tampak. Clipping iris/pupil/glint ke sclera penuh belum ada.

### T5 (P0) — Mulut: satu garis; komponen buka-mulut sangat kecil
Mulut aktif hanya `MOUTH_CLOSED_NEUTRAL` (21x12 px), satu garis yang tidak bisa dibuka. Bibir atas dan bawah pengganti hanya 22x5 dan 17x4 px, rongga 26x16, gigi 20x5, lidah 15x7. Pada ukuran ini deformasi bibir dan bukaan akan kasar. Semua komponen mulut belum terpasang di tubuh wajah (tersembunyi dan belum diselaraskan).

### T6 (P0) — Resolusi kanvas rendah untuk wajah; versi Highres di luar PSD
Kanvas 1024x1536. Wajah aktif (`FACE`) 110x145 px; wajah utuh (`BF_FACE_COMPLETE`) 169x212 px. Untuk tampilan setengah badan di VTube Studio, wajah akan diperbesar dan terlihat buram. Paket menyertakan 22 PNG komponen wajah resolusi sumber (`Face_Components_Highres`) yang tidak ada di PSD maupun manifest; misalnya bibir atas 196x32 px dibanding 22x5 px pada kanvas (PNG Highres memuat margin transparan, sehingga rasio hanya perkiraan: sekitar 5–9x). Keputusan yang dibutuhkan: skala kanvas kerja (usulan: naikkan ke 2–3x sebelum rigging, atau terima kualitas 1x untuk tampilan jauh).

### T7 (P0) — Backfill ada tetapi belum diselaraskan; sebagian area belum punya backfill
Lima backfill (`BF_FACE_COMPLETE`, `BF_NECK_AND_TORSO`, `BF_CLOTHING_BODY`, `BF_LOWER_SKIRT`, `BF_HAIR_BACK_COMPLETE`) tersembunyi dan bernote "alignment required" (offset awal y+20 pada manifest). Tidak ditemukan plate khusus untuk: bagian atas lengan di bawah lengan baju (lengan mulai y=492/495, lengan baju mulai y=366), bagian atas kaki di bawah rok (kaki mulai y=771), dan area di balik tangan.

### T8 (P0) — Leher sangat pendek dan terpisah
`NECK` hanya 84x42 px (y 250–292) dan tertutup kerah di bawah. Saat kepala menoleh atau miring, ujung atas dan bawah leher harus meluas (ekstensi ke bawah dagu dan ke bawah kerah). `BF_NECK_AND_TORSO` dapat menjadi dasar.

### T9 (P1) — Kaki saling bersentuhan dan berhenti tepat di bawah rok
`LEG_LEFT` dan `LEG_RIGHT` bersentuhan 504 piksel dan berawal di y=771, tempat tepi rok depan. Saat rok bergoyang, pangkal paha akan terlihat terpotong. Perlu ekstensi paha di bawah rok.

### T10 (P2) — Aksesori: banyak dan kecil; beberapa asimetris
Ada 32 aksesori. Rantai sangat tipis (`CHEST_CHAIN` 18 px lebar, `HAIR_CHAIN_*` 32–48 px lebar) dan perhiasan kecil rawan tepi kasar. `THIGH_GARTER_LEFT`, `THIGH_JEWELS_LEFT`, dan `HAIR_CLIP_RIGHT` hanya ada satu sisi (brief menyebut aksesori kaki kiri dan kanan; ini mungkin keputusan desain, perlu dikonfirmasi).

### T11 (P0) — PSD bukan dari Photoshop atau Clip Studio Paint
Dokumentasi resmi menyatakan PSD dari aplikasi lain "may not load properly". Strukturnya sesuai syarat (RGB, 8-bit, tanpa mask, nama unik, sRGB), tetapi impor belum diuji. Simpan ulang melalui Photoshop atau Clip Studio Paint setelah retouch (sudah dianjurkan oleh PANDUAN_CUBISM.md).

### T12 (P0) — Koreksi pada spesifikasi v1
- **Polaritas alis terbalik.** Standard Parameter List resmi: `ParamBrow{L,R}Angle` dan `ParamBrow{L,R}Form` bernilai NEGATIF untuk marah. Parameter_Spec.csv v1 menyatakan +1 = marah, dan `ANGRY.exp3.json` memakai `BrowLForm = 1` (diverifikasi dari berkas), `SAD.exp3.json` memakai `-1`.
- **Parameter tanpa deformer pengendali** pada Deformer_Hierarchy.spec.json: `ParamBrowLAngle`, `ParamBrowLForm`, `ParamBrowLY`, `ParamBrowRAngle`, `ParamBrowRForm`, `ParamBrowRY`, `ParamCheek`, `ParamHairSideLSway`, `ParamHairSideRSway` (alis tidak punya deformer; rambut samping punya parameter dan physics tetapi tanpa deformer; `ParamCheek` hanya memerlukan keyform opacity).
- **Template physics seragam:** 12 pengaturan hanya memakai 2 kombinasi input dan 3 profil bandul; tidak ada `ParamAngleY`; Scale output [0.05, 0.08]. Skema dan jumlah meta konsisten (VERIFIED), tetapi nilainya belum dituning dan rambut/pita bergerak identik.
- Deformer v1 tidak memiliki leher, kaki, atau lengan; rambut belakang memakai satu deformer untuk kiri dan kanan. Penggantinya ada di `deformer_plan.csv`.

### T13 — Perbedaan nama layer terhadap brief (VERIFIED dari perbandingan nama)
| Diminta di brief | Kondisi di paket |
| --- | --- |
| MOUTH_BASE, MOUTH_INSIDE, MOUTH_UPPER, MOUTH_LOWER, TEETH, TONGUE | Hanya `MOUTH_CLOSED_NEUTRAL` aktif; sisanya hanya sebagai `ALT_MOUTH_*`, `ALT_TEETH`, `ALT_TONGUE` (tersembunyi) |
| BLUSH_LEFT/RIGHT | Hanya `ALT_BLUSH_*` (tersembunyi) |
| HEAD, CHEST, WAIST sebagai layer terpisah | Tidak ada layer bernama itu; diwakili `FACE`, `BODICE`, `TORSO_UPPER`, `BF_*` |
| INNER_CLOTHING, DRESS, CAPE, TRANSPARENT_FABRIC, FABRIC_DETAILS, ORNAMENTS | Tidak ada layer bernama itu; pakaian dipecah menjadi `BODICE`, `SKIRT_*`, `OVERSKIRT_*`, `TRAIN_*`, `SLEEVE_*` |
| HAIR_STRANDS, HAIR_ACCESSORIES | Helai terpisah belum ada (lihat T3); aksesori rambut ada sebagai item terpisah |
| Grup EFFECTS | Tidak ada |
| LEG_ACCESSORY_LEFT/RIGHT | Hanya sisi kiri (`THIGH_GARTER_LEFT`, `THIGH_JEWELS_LEFT`) |

## 4. Pemeriksaan khusus sesuai daftar audit

| Item | Ditemukan | Cukup untuk animasi? | Tindakan |
| --- | --- | --- | --- |
| Mata kiri dan kanan | Masing-masing 6 layer aktif + 6 pengganti; pusat iris (545,188) dan (474,188) | Belum (T4) | Pasang komponen penuh, buat clipping |
| Iris, pupil, highlight, putih mata | Ada terpisah; aktif terpotong; versi penuh tersembunyi | Belum | Ganti ke ALT_IRIS_FULL, ALT_PUPIL_FULL, ALT_GLINT, ALT_SCLERA |
| Kelopak atas dan bawah | `UPPER/LOWER_EYELID_*` aktif; `ALT_LASH_*` pengganti | Perlu dipilih satu versi | Pilih versi konsisten; uji tutup penuh tanpa bocor |
| Alis kiri dan kanan | `EYEBROW_*` aktif dan `ALT_EYEBROW_FULL_*` | Hampir; kulit di bawah alis perlu ada | Pilih satu; BF_FACE_COMPLETE mengisi |
| Mulut tertutup dan terbuka | Tertutup: satu garis. Terbuka: komponen ALT kecil, belum terpasang | Belum (T5) | Pasang set ALT/Highres; keyform Open x Form |
| Rambut depan | `BANG_*` 3 helai + `HAIR_CROWN` | Cukup untuk sway dasar bila overlap ditambah | Gambar ulang tepi poligon |
| Rambut samping | `HAIR_SIDE_*`, `HAIR_TRESS_*` | Belum; potongan poligon di wajah | Gambar ulang; deformer D_HAIR_SIDE_* baru |
| Rambut belakang | 2 massa + 2 ujung + backfill tersembunyi | Belum (T2, T3) | Pecah helai; hapus potongan lurus |
| Leher, kepala, badan, pakaian | Leher 84x42 px; wajah berlubang; badan/pakaian partisi tanpa overlap | Belum (T1, T8) | Ekstensi dan overlap; aktifkan backfill |
| Aksesori yang perlu bergerak | Anting, rantai, pita, ornamen ekor paus, bintang rambut, permata dada/pinggang | Cukup terpisah | Tambah titik gantung; rapikan tepi tipis |
| Bagian tertutup yang perlu redraw | Lengan di bawah lengan baju, kaki di bawah rok, balik tangan, balik poni/rambut samping | Belum ada | Gambar ekstensi (T7, T9) |
| Area kosong/celah saat bergerak | 218 sambungan tanpa overlap; terlihat pada rambut, rok, kaki, lengan | Belum | Overlap di semua seam (T1) |

## 5. Inventaris lengkap (179 berkas)

Dibuat otomatis dari isi folder; kondisi layer diambil dari pemeriksaan piksel dan manifest. Rincian per layer (bbox, fungsi rig, parent) ada di `layer_mapping.csv`.

| No. | File/Layer | Jenis | Fungsi | Kondisi | Tindakan |
| --- | --- | --- | --- | --- | --- |
| 1 | `01_Source/Aoi_Cetara_Neutral_Master.png` | PNG sumber | Master karakter transparan 1024x1536 | Terdekode; checksum OK | Arsip; jangan diubah |
| 2 | `01_Source/Backfill_Head_and_Dressed_Body.png` | PNG sumber | Plate backfill kepala + badan berpakaian | Terdekode; checksum OK | Arsip; sumber BF_FACE/BF_NECK/BF_CLOTHING |
| 3 | `01_Source/Backfill_Rear_Hair.png` | PNG sumber | Plate backfill rambut belakang | Terdekode; checksum OK | Arsip; sumber BF_HAIR_BACK_COMPLETE |
| 4 | `01_Source/Face_Components_Sheet.png` | PNG sumber | Lembar komponen wajah (1254x1254) | Terdekode; checksum OK | Arsip |
| 5 | `01_Source/Facial_Supplement_Prompt.txt` | Teks | Prompt pembuatan suplemen wajah | Terbaca | Arsip |
| 6 | `01_Source/Facial_Supplement_Sheet.png` | PNG sumber | Lembar suplemen bibir/blush/alis (1254x1254) | Terdekode; checksum OK | Arsip |
| 7 | `01_Source/Generation_Prompts.json` | JSON | Prompt pembuatan master/plate | Parse OK | Arsip |
| 8 | `01_Source/User_Brief.md` | Markdown | Brief karakter dan persyaratan rigging dari pengguna | Terbaca | Acuan identitas visual; tidak diubah |
| 9 | `01_Source/User_Character_Reference.png` | PNG sumber | Gambar referensi karakter (1254x1254) | Terdekode; checksum OK | Acuan identitas visual |
| 10 | `02_Layered_Artwork/Aoi_Cetara_ArtPrep_v1.ora` | OpenRaster | Salinan layered artwork format terbuka | CRC arsip OK; 117 entri | Cadangan; PSD adalah file kerja |
| 11 | `02_Layered_Artwork/Aoi_Cetara_ArtPrep_v1.psd` | PSD | Artwork berlayer utama untuk impor Cubism | Struktur terbaca: 113 layer, 14 grup, 0 mask, RGB 8-bit, ICC tertanam. Bukan dibuat Photoshop/CSP | Rapikan artwork lalu simpan ulang lewat Photoshop/CSP (P0) |
| 12 | `02_Layered_Artwork/Layer_Manifest.csv` | CSV | Manifest 113 layer (nama, grup, bbox, pivot, status) | Parse OK; 113/113 cocok PSD dan PNG | Pakai sebagai referensi; perbarui setelah retouch |
| 13 | `02_Layered_Artwork/Layer_Manifest.json` | JSON | Manifest layer format JSON | Parse OK | Pakai bersama CSV |
| 14 | `03_PNG_Layers/00_BACKFILL_ALIGN_FIRST/BF_CLOTHING_BODY.png` | PNG layer (kanvas 1024x1536) | Backfill: BF_CLOTHING_BODY | Tersembunyi (opsional); terdekode; belum diselaraskan | Selaraskan lalu aktifkan sebagai pengganti (lihat layer_mapping.csv) |
| 15 | `03_PNG_Layers/00_BACKFILL_ALIGN_FIRST/BF_FACE_COMPLETE.png` | PNG layer (kanvas 1024x1536) | Backfill: BF_FACE_COMPLETE | Tersembunyi (opsional); terdekode; belum diselaraskan | Selaraskan lalu aktifkan sebagai pengganti (lihat layer_mapping.csv) |
| 16 | `03_PNG_Layers/00_BACKFILL_ALIGN_FIRST/BF_HAIR_BACK_COMPLETE.png` | PNG layer (kanvas 1024x1536) | Backfill: BF_HAIR_BACK_COMPLETE | Tersembunyi (opsional); terdekode; belum diselaraskan | Selaraskan lalu aktifkan sebagai pengganti (lihat layer_mapping.csv) |
| 17 | `03_PNG_Layers/00_BACKFILL_ALIGN_FIRST/BF_LOWER_SKIRT.png` | PNG layer (kanvas 1024x1536) | Backfill: BF_LOWER_SKIRT | Tersembunyi (opsional); terdekode; belum diselaraskan | Selaraskan lalu aktifkan sebagai pengganti (lihat layer_mapping.csv) |
| 18 | `03_PNG_Layers/00_BACKFILL_ALIGN_FIRST/BF_NECK_AND_TORSO.png` | PNG layer (kanvas 1024x1536) | Backfill: BF_NECK_AND_TORSO | Tersembunyi (opsional); terdekode; belum diselaraskan | Selaraskan lalu aktifkan sebagai pengganti (lihat layer_mapping.csv) |
| 19 | `03_PNG_Layers/01_HAIR_BACK/HAIR_BACK_LEFT.png` | PNG layer (kanvas 1024x1536) | 01_HAIR_BACK: HAIR_BACK_LEFT | Aktif; terdekode; tanpa overlap; menyentuh 25 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 20 | `03_PNG_Layers/01_HAIR_BACK/HAIR_BACK_RIGHT.png` | PNG layer (kanvas 1024x1536) | 01_HAIR_BACK: HAIR_BACK_RIGHT | Aktif; terdekode; tanpa overlap; menyentuh 21 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 21 | `03_PNG_Layers/01_HAIR_BACK/HAIR_TIP_LEFT.png` | PNG layer (kanvas 1024x1536) | 01_HAIR_BACK: HAIR_TIP_LEFT | Aktif; terdekode; tanpa overlap; menyentuh 3 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 22 | `03_PNG_Layers/01_HAIR_BACK/HAIR_TIP_RIGHT.png` | PNG layer (kanvas 1024x1536) | 01_HAIR_BACK: HAIR_TIP_RIGHT | Aktif; terdekode; tanpa overlap; menyentuh 3 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 23 | `03_PNG_Layers/02_CLOTHING_BACK/SKIRT_BACK_CENTER.png` | PNG layer (kanvas 1024x1536) | 02_CLOTHING_BACK: SKIRT_BACK_CENTER | Aktif; terdekode; tanpa overlap; menyentuh 9 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 24 | `03_PNG_Layers/02_CLOTHING_BACK/SKIRT_BACK_LEFT.png` | PNG layer (kanvas 1024x1536) | 02_CLOTHING_BACK: SKIRT_BACK_LEFT | Aktif; terdekode; tanpa overlap; menyentuh 7 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 25 | `03_PNG_Layers/02_CLOTHING_BACK/SKIRT_BACK_RIGHT.png` | PNG layer (kanvas 1024x1536) | 02_CLOTHING_BACK: SKIRT_BACK_RIGHT | Aktif; terdekode; tanpa overlap; menyentuh 7 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 26 | `03_PNG_Layers/03_CLOTHING/BODICE.png` | PNG layer (kanvas 1024x1536) | 03_CLOTHING: BODICE | Aktif; terdekode; tanpa overlap; menyentuh 16 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 27 | `03_PNG_Layers/03_CLOTHING/OVERSKIRT_LEFT.png` | PNG layer (kanvas 1024x1536) | 03_CLOTHING: OVERSKIRT_LEFT | Aktif; terdekode; tanpa overlap; menyentuh 9 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 28 | `03_PNG_Layers/03_CLOTHING/OVERSKIRT_RIGHT.png` | PNG layer (kanvas 1024x1536) | 03_CLOTHING: OVERSKIRT_RIGHT | Aktif; terdekode; tanpa overlap; menyentuh 7 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 29 | `03_PNG_Layers/03_CLOTHING/SKIRT_FRONT_CENTER.png` | PNG layer (kanvas 1024x1536) | 03_CLOTHING: SKIRT_FRONT_CENTER | Aktif; terdekode; tanpa overlap; menyentuh 8 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 30 | `03_PNG_Layers/03_CLOTHING/SKIRT_FRONT_LEFT.png` | PNG layer (kanvas 1024x1536) | 03_CLOTHING: SKIRT_FRONT_LEFT | Aktif; terdekode; tanpa overlap; menyentuh 7 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 31 | `03_PNG_Layers/03_CLOTHING/SKIRT_FRONT_RIGHT.png` | PNG layer (kanvas 1024x1536) | 03_CLOTHING: SKIRT_FRONT_RIGHT | Aktif; terdekode; tanpa overlap; menyentuh 7 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 32 | `03_PNG_Layers/03_CLOTHING/SLEEVE_LEFT.png` | PNG layer (kanvas 1024x1536) | 03_CLOTHING: SLEEVE_LEFT | Aktif; terdekode; tanpa overlap; menyentuh 5 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 33 | `03_PNG_Layers/03_CLOTHING/SLEEVE_RIGHT.png` | PNG layer (kanvas 1024x1536) | 03_CLOTHING: SLEEVE_RIGHT | Aktif; terdekode; tanpa overlap; menyentuh 5 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 34 | `03_PNG_Layers/03_CLOTHING/TRAIN_LEFT.png` | PNG layer (kanvas 1024x1536) | 03_CLOTHING: TRAIN_LEFT | Aktif; terdekode; tanpa overlap; menyentuh 3 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 35 | `03_PNG_Layers/03_CLOTHING/TRAIN_RIGHT.png` | PNG layer (kanvas 1024x1536) | 03_CLOTHING: TRAIN_RIGHT | Aktif; terdekode; tanpa overlap; menyentuh 4 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 36 | `03_PNG_Layers/04_BODY/LEG_LEFT.png` | PNG layer (kanvas 1024x1536) | 04_BODY: LEG_LEFT | Aktif; terdekode; tanpa overlap; menyentuh 8 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 37 | `03_PNG_Layers/04_BODY/LEG_RIGHT.png` | PNG layer (kanvas 1024x1536) | 04_BODY: LEG_RIGHT | Aktif; terdekode; tanpa overlap; menyentuh 5 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 38 | `03_PNG_Layers/04_BODY/NECK.png` | PNG layer (kanvas 1024x1536) | 04_BODY: NECK | Aktif; terdekode; tanpa overlap; menyentuh 5 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 39 | `03_PNG_Layers/04_BODY/SHOE_LEFT.png` | PNG layer (kanvas 1024x1536) | 04_BODY: SHOE_LEFT | Aktif; terdekode; tanpa overlap; menyentuh 5 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 40 | `03_PNG_Layers/04_BODY/SHOE_RIGHT.png` | PNG layer (kanvas 1024x1536) | 04_BODY: SHOE_RIGHT | Aktif; terdekode; tanpa overlap; menyentuh 4 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 41 | `03_PNG_Layers/04_BODY/TORSO_UPPER.png` | PNG layer (kanvas 1024x1536) | 04_BODY: TORSO_UPPER | Aktif; terdekode; tanpa overlap; menyentuh 11 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 42 | `03_PNG_Layers/05_ARMS/ARM_LEFT.png` | PNG layer (kanvas 1024x1536) | 05_ARMS: ARM_LEFT | Aktif; terdekode; tanpa overlap; menyentuh 5 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 43 | `03_PNG_Layers/05_ARMS/ARM_RIGHT.png` | PNG layer (kanvas 1024x1536) | 05_ARMS: ARM_RIGHT | Aktif; terdekode; tanpa overlap; menyentuh 5 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 44 | `03_PNG_Layers/05_ARMS/HAND_LEFT.png` | PNG layer (kanvas 1024x1536) | 05_ARMS: HAND_LEFT | Aktif; terdekode; tanpa overlap; menyentuh 3 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 45 | `03_PNG_Layers/05_ARMS/HAND_RIGHT.png` | PNG layer (kanvas 1024x1536) | 05_ARMS: HAND_RIGHT | Aktif; terdekode; tanpa overlap; menyentuh 3 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 46 | `03_PNG_Layers/06_FACE/EAR_LEFT.png` | PNG layer (kanvas 1024x1536) | 06_FACE: EAR_LEFT | Aktif; terdekode; tanpa overlap; menyentuh 5 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 47 | `03_PNG_Layers/06_FACE/EAR_RIGHT.png` | PNG layer (kanvas 1024x1536) | 06_FACE: EAR_RIGHT | Aktif; terdekode; tanpa overlap; menyentuh 3 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 48 | `03_PNG_Layers/06_FACE/FACE.png` | PNG layer (kanvas 1024x1536) | 06_FACE: FACE | Aktif; terdekode; tanpa overlap; menyentuh 20 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 49 | `03_PNG_Layers/06_FACE/NOSE.png` | PNG layer (kanvas 1024x1536) | 06_FACE: NOSE | Aktif; terdekode; tanpa overlap; menyentuh 1 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 50 | `03_PNG_Layers/07_EYES/EYE_WHITE_LEFT.png` | PNG layer (kanvas 1024x1536) | 07_EYES: EYE_WHITE_LEFT | Aktif; terdekode; tanpa overlap; menyentuh 5 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 51 | `03_PNG_Layers/07_EYES/EYE_WHITE_RIGHT.png` | PNG layer (kanvas 1024x1536) | 07_EYES: EYE_WHITE_RIGHT | Aktif; terdekode; tanpa overlap; menyentuh 5 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 52 | `03_PNG_Layers/07_EYES/HIGHLIGHT_LEFT.png` | PNG layer (kanvas 1024x1536) | 07_EYES: HIGHLIGHT_LEFT | Aktif; terdekode; tanpa overlap; menyentuh 3 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 53 | `03_PNG_Layers/07_EYES/HIGHLIGHT_RIGHT.png` | PNG layer (kanvas 1024x1536) | 07_EYES: HIGHLIGHT_RIGHT | Aktif; terdekode; tanpa overlap; menyentuh 3 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 54 | `03_PNG_Layers/07_EYES/IRIS_LEFT.png` | PNG layer (kanvas 1024x1536) | 07_EYES: IRIS_LEFT | Aktif; terdekode; tanpa overlap; menyentuh 5 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 55 | `03_PNG_Layers/07_EYES/IRIS_RIGHT.png` | PNG layer (kanvas 1024x1536) | 07_EYES: IRIS_RIGHT | Aktif; terdekode; tanpa overlap; menyentuh 5 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 56 | `03_PNG_Layers/07_EYES/LOWER_EYELID_LEFT.png` | PNG layer (kanvas 1024x1536) | 07_EYES: LOWER_EYELID_LEFT | Aktif; terdekode; tanpa overlap; menyentuh 6 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 57 | `03_PNG_Layers/07_EYES/LOWER_EYELID_RIGHT.png` | PNG layer (kanvas 1024x1536) | 07_EYES: LOWER_EYELID_RIGHT | Aktif; terdekode; tanpa overlap; menyentuh 4 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 58 | `03_PNG_Layers/07_EYES/PUPIL_LEFT.png` | PNG layer (kanvas 1024x1536) | 07_EYES: PUPIL_LEFT | Aktif; terdekode; tanpa overlap; menyentuh 2 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 59 | `03_PNG_Layers/07_EYES/PUPIL_RIGHT.png` | PNG layer (kanvas 1024x1536) | 07_EYES: PUPIL_RIGHT | Aktif; terdekode; tanpa overlap; menyentuh 2 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 60 | `03_PNG_Layers/07_EYES/UPPER_EYELID_LEFT.png` | PNG layer (kanvas 1024x1536) | 07_EYES: UPPER_EYELID_LEFT | Aktif; terdekode; tanpa overlap; menyentuh 6 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 61 | `03_PNG_Layers/07_EYES/UPPER_EYELID_RIGHT.png` | PNG layer (kanvas 1024x1536) | 07_EYES: UPPER_EYELID_RIGHT | Aktif; terdekode; tanpa overlap; menyentuh 5 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 62 | `03_PNG_Layers/08_BROWS/EYEBROW_LEFT.png` | PNG layer (kanvas 1024x1536) | 08_BROWS: EYEBROW_LEFT | Aktif; terdekode; tanpa overlap; menyentuh 3 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 63 | `03_PNG_Layers/08_BROWS/EYEBROW_RIGHT.png` | PNG layer (kanvas 1024x1536) | 08_BROWS: EYEBROW_RIGHT | Aktif; terdekode; tanpa overlap; menyentuh 3 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 64 | `03_PNG_Layers/09_MOUTH/MOUTH_CLOSED_NEUTRAL.png` | PNG layer (kanvas 1024x1536) | 09_MOUTH: MOUTH_CLOSED_NEUTRAL | Aktif; terdekode; tanpa overlap; menyentuh 1 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 65 | `03_PNG_Layers/10_HAIR_SIDE/HAIR_SIDE_LEFT.png` | PNG layer (kanvas 1024x1536) | 10_HAIR_SIDE: HAIR_SIDE_LEFT | Aktif; terdekode; tanpa overlap; menyentuh 8 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 66 | `03_PNG_Layers/10_HAIR_SIDE/HAIR_SIDE_RIGHT.png` | PNG layer (kanvas 1024x1536) | 10_HAIR_SIDE: HAIR_SIDE_RIGHT | Aktif; terdekode; tanpa overlap; menyentuh 9 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 67 | `03_PNG_Layers/10_HAIR_SIDE/HAIR_TRESS_LEFT.png` | PNG layer (kanvas 1024x1536) | 10_HAIR_SIDE: HAIR_TRESS_LEFT | Aktif; terdekode; tanpa overlap; menyentuh 2 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 68 | `03_PNG_Layers/10_HAIR_SIDE/HAIR_TRESS_RIGHT.png` | PNG layer (kanvas 1024x1536) | 10_HAIR_SIDE: HAIR_TRESS_RIGHT | Aktif; terdekode; tanpa overlap; menyentuh 3 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 69 | `03_PNG_Layers/11_HAIR_FRONT/BANG_CENTER.png` | PNG layer (kanvas 1024x1536) | 11_HAIR_FRONT: BANG_CENTER | Aktif; terdekode; tanpa overlap; menyentuh 10 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 70 | `03_PNG_Layers/11_HAIR_FRONT/BANG_LEFT.png` | PNG layer (kanvas 1024x1536) | 11_HAIR_FRONT: BANG_LEFT | Aktif; terdekode; tanpa overlap; menyentuh 10 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 71 | `03_PNG_Layers/11_HAIR_FRONT/BANG_RIGHT.png` | PNG layer (kanvas 1024x1536) | 11_HAIR_FRONT: BANG_RIGHT | Aktif; terdekode; tanpa overlap; menyentuh 9 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 72 | `03_PNG_Layers/11_HAIR_FRONT/HAIR_CROWN.png` | PNG layer (kanvas 1024x1536) | 11_HAIR_FRONT: HAIR_CROWN | Aktif; terdekode; tanpa overlap; menyentuh 12 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 73 | `03_PNG_Layers/12_ACCESSORIES/BRACELET_LEFT.png` | PNG layer (kanvas 1024x1536) | 12_ACCESSORIES: BRACELET_LEFT | Aktif; terdekode; tanpa overlap; menyentuh 3 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 74 | `03_PNG_Layers/12_ACCESSORIES/BRACELET_RIGHT.png` | PNG layer (kanvas 1024x1536) | 12_ACCESSORIES: BRACELET_RIGHT | Aktif; terdekode; tanpa overlap; menyentuh 3 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 75 | `03_PNG_Layers/12_ACCESSORIES/CHEST_CHAIN.png` | PNG layer (kanvas 1024x1536) | 12_ACCESSORIES: CHEST_CHAIN | Aktif; terdekode; tanpa overlap; menyentuh 4 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 76 | `03_PNG_Layers/12_ACCESSORIES/CHEST_GEM.png` | PNG layer (kanvas 1024x1536) | 12_ACCESSORIES: CHEST_GEM | Aktif; terdekode; tanpa overlap; menyentuh 6 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 77 | `03_PNG_Layers/12_ACCESSORIES/CHEST_RIBBON_LEFT.png` | PNG layer (kanvas 1024x1536) | 12_ACCESSORIES: CHEST_RIBBON_LEFT | Aktif; terdekode; tanpa overlap; menyentuh 3 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 78 | `03_PNG_Layers/12_ACCESSORIES/CHEST_RIBBON_RIGHT.png` | PNG layer (kanvas 1024x1536) | 12_ACCESSORIES: CHEST_RIBBON_RIGHT | Aktif; terdekode; tanpa overlap; menyentuh 2 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 79 | `03_PNG_Layers/12_ACCESSORIES/CHEST_RIBBON_TAIL_LEFT.png` | PNG layer (kanvas 1024x1536) | 12_ACCESSORIES: CHEST_RIBBON_TAIL_LEFT | Aktif; terdekode; tanpa overlap; menyentuh 4 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 80 | `03_PNG_Layers/12_ACCESSORIES/CHEST_RIBBON_TAIL_RIGHT.png` | PNG layer (kanvas 1024x1536) | 12_ACCESSORIES: CHEST_RIBBON_TAIL_RIGHT | Aktif; terdekode; tanpa overlap; menyentuh 3 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 81 | `03_PNG_Layers/12_ACCESSORIES/COLLAR.png` | PNG layer (kanvas 1024x1536) | 12_ACCESSORIES: COLLAR | Aktif; terdekode; tanpa overlap; menyentuh 4 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 82 | `03_PNG_Layers/12_ACCESSORIES/EARRING_LEFT.png` | PNG layer (kanvas 1024x1536) | 12_ACCESSORIES: EARRING_LEFT | Aktif; terdekode; tanpa overlap; menyentuh 3 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 83 | `03_PNG_Layers/12_ACCESSORIES/EARRING_RIGHT.png` | PNG layer (kanvas 1024x1536) | 12_ACCESSORIES: EARRING_RIGHT | Aktif; terdekode; tanpa overlap; menyentuh 2 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 84 | `03_PNG_Layers/12_ACCESSORIES/FOREHEAD_JEWEL.png` | PNG layer (kanvas 1024x1536) | 12_ACCESSORIES: FOREHEAD_JEWEL | Aktif; terdekode; tanpa overlap; menyentuh 1 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 85 | `03_PNG_Layers/12_ACCESSORIES/HAIR_CHAIN_LEFT.png` | PNG layer (kanvas 1024x1536) | 12_ACCESSORIES: HAIR_CHAIN_LEFT | Aktif; terdekode; tanpa overlap; menyentuh 3 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 86 | `03_PNG_Layers/12_ACCESSORIES/HAIR_CHAIN_RIGHT.png` | PNG layer (kanvas 1024x1536) | 12_ACCESSORIES: HAIR_CHAIN_RIGHT | Aktif; terdekode; tanpa overlap; menyentuh 3 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 87 | `03_PNG_Layers/12_ACCESSORIES/HAIR_CLIP_RIGHT.png` | PNG layer (kanvas 1024x1536) | 12_ACCESSORIES: HAIR_CLIP_RIGHT | Aktif; terdekode; tanpa overlap; menyentuh 2 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 88 | `03_PNG_Layers/12_ACCESSORIES/HAIR_FLOWERS_SMALL.png` | PNG layer (kanvas 1024x1536) | 12_ACCESSORIES: HAIR_FLOWERS_SMALL | Aktif; terdekode; tanpa overlap; menyentuh 3 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 89 | `03_PNG_Layers/12_ACCESSORIES/HAIR_FLOWER_MAIN.png` | PNG layer (kanvas 1024x1536) | 12_ACCESSORIES: HAIR_FLOWER_MAIN | Aktif; terdekode; tanpa overlap; menyentuh 4 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 90 | `03_PNG_Layers/12_ACCESSORIES/HAIR_STAR_LEFT.png` | PNG layer (kanvas 1024x1536) | 12_ACCESSORIES: HAIR_STAR_LEFT | Aktif; terdekode; tanpa overlap; menyentuh 1 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 91 | `03_PNG_Layers/12_ACCESSORIES/HAIR_STAR_RIGHT.png` | PNG layer (kanvas 1024x1536) | 12_ACCESSORIES: HAIR_STAR_RIGHT | Aktif; terdekode; tanpa overlap; menyentuh 1 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 92 | `03_PNG_Layers/12_ACCESSORIES/NECK_PENDANT.png` | PNG layer (kanvas 1024x1536) | 12_ACCESSORIES: NECK_PENDANT | Aktif; terdekode; tanpa overlap; menyentuh 2 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 93 | `03_PNG_Layers/12_ACCESSORIES/NECK_RIBBON.png` | PNG layer (kanvas 1024x1536) | 12_ACCESSORIES: NECK_RIBBON | Aktif; terdekode; tanpa overlap; menyentuh 3 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 94 | `03_PNG_Layers/12_ACCESSORIES/SLEEVE_FLOWER_LEFT.png` | PNG layer (kanvas 1024x1536) | 12_ACCESSORIES: SLEEVE_FLOWER_LEFT | Aktif; terdekode; tanpa overlap; menyentuh 1 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 95 | `03_PNG_Layers/12_ACCESSORIES/SLEEVE_FLOWER_RIGHT.png` | PNG layer (kanvas 1024x1536) | 12_ACCESSORIES: SLEEVE_FLOWER_RIGHT | Aktif; terdekode; tanpa overlap; menyentuh 1 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 96 | `03_PNG_Layers/12_ACCESSORIES/THIGH_GARTER_LEFT.png` | PNG layer (kanvas 1024x1536) | 12_ACCESSORIES: THIGH_GARTER_LEFT | Aktif; terdekode; tanpa overlap; menyentuh 3 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 97 | `03_PNG_Layers/12_ACCESSORIES/THIGH_JEWELS_LEFT.png` | PNG layer (kanvas 1024x1536) | 12_ACCESSORIES: THIGH_JEWELS_LEFT | Aktif; terdekode; tanpa overlap; menyentuh 3 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 98 | `03_PNG_Layers/12_ACCESSORIES/TIARA.png` | PNG layer (kanvas 1024x1536) | 12_ACCESSORIES: TIARA | Aktif; terdekode; tanpa overlap; menyentuh 4 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 99 | `03_PNG_Layers/12_ACCESSORIES/TRAIN_GEM_LEFT.png` | PNG layer (kanvas 1024x1536) | 12_ACCESSORIES: TRAIN_GEM_LEFT | Aktif; terdekode; tanpa overlap; menyentuh 1 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 100 | `03_PNG_Layers/12_ACCESSORIES/TRAIN_GEM_RIGHT.png` | PNG layer (kanvas 1024x1536) | 12_ACCESSORIES: TRAIN_GEM_RIGHT | Aktif; terdekode; tanpa overlap; menyentuh 1 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 101 | `03_PNG_Layers/12_ACCESSORIES/WAIST_CHAIN.png` | PNG layer (kanvas 1024x1536) | 12_ACCESSORIES: WAIST_CHAIN | Aktif; terdekode; tanpa overlap; menyentuh 4 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 102 | `03_PNG_Layers/12_ACCESSORIES/WAIST_RIBBON_LEFT.png` | PNG layer (kanvas 1024x1536) | 12_ACCESSORIES: WAIST_RIBBON_LEFT | Aktif; terdekode; tanpa overlap; menyentuh 2 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 103 | `03_PNG_Layers/12_ACCESSORIES/WAIST_RIBBON_RIGHT.png` | PNG layer (kanvas 1024x1536) | 12_ACCESSORIES: WAIST_RIBBON_RIGHT | Aktif; terdekode; tanpa overlap; menyentuh 2 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 104 | `03_PNG_Layers/12_ACCESSORIES/WHALE_TAIL_ORNAMENT.png` | PNG layer (kanvas 1024x1536) | 12_ACCESSORIES: WHALE_TAIL_ORNAMENT | Aktif; terdekode; tanpa overlap; menyentuh 4 layer lain | Rapikan tepi dan tambah overlap (lihat layer_mapping.csv) |
| 105 | `03_PNG_Layers/13_FACE_COMPONENTS_ALTERNATES/ALT_BLUSH_LEFT.png` | PNG layer (kanvas 1024x1536) | Komponen wajah pengganti: ALT_BLUSH_LEFT | Tersembunyi (opsional); terdekode; belum diselaraskan | Selaraskan lalu aktifkan sebagai pengganti (lihat layer_mapping.csv) |
| 106 | `03_PNG_Layers/13_FACE_COMPONENTS_ALTERNATES/ALT_BLUSH_RIGHT.png` | PNG layer (kanvas 1024x1536) | Komponen wajah pengganti: ALT_BLUSH_RIGHT | Tersembunyi (opsional); terdekode; belum diselaraskan | Selaraskan lalu aktifkan sebagai pengganti (lihat layer_mapping.csv) |
| 107 | `03_PNG_Layers/13_FACE_COMPONENTS_ALTERNATES/ALT_EYEBROW_FULL_LEFT.png` | PNG layer (kanvas 1024x1536) | Komponen wajah pengganti: ALT_EYEBROW_FULL_LEFT | Tersembunyi (opsional); terdekode; belum diselaraskan | Selaraskan lalu aktifkan sebagai pengganti (lihat layer_mapping.csv) |
| 108 | `03_PNG_Layers/13_FACE_COMPONENTS_ALTERNATES/ALT_EYEBROW_FULL_RIGHT.png` | PNG layer (kanvas 1024x1536) | Komponen wajah pengganti: ALT_EYEBROW_FULL_RIGHT | Tersembunyi (opsional); terdekode; belum diselaraskan | Selaraskan lalu aktifkan sebagai pengganti (lihat layer_mapping.csv) |
| 109 | `03_PNG_Layers/13_FACE_COMPONENTS_ALTERNATES/ALT_GLINT_LEFT.png` | PNG layer (kanvas 1024x1536) | Komponen wajah pengganti: ALT_GLINT_LEFT | Tersembunyi (opsional); terdekode; belum diselaraskan | Selaraskan lalu aktifkan sebagai pengganti (lihat layer_mapping.csv) |
| 110 | `03_PNG_Layers/13_FACE_COMPONENTS_ALTERNATES/ALT_GLINT_RIGHT.png` | PNG layer (kanvas 1024x1536) | Komponen wajah pengganti: ALT_GLINT_RIGHT | Tersembunyi (opsional); terdekode; belum diselaraskan | Selaraskan lalu aktifkan sebagai pengganti (lihat layer_mapping.csv) |
| 111 | `03_PNG_Layers/13_FACE_COMPONENTS_ALTERNATES/ALT_IRIS_FULL_LEFT.png` | PNG layer (kanvas 1024x1536) | Komponen wajah pengganti: ALT_IRIS_FULL_LEFT | Tersembunyi (opsional); terdekode; belum diselaraskan | Selaraskan lalu aktifkan sebagai pengganti (lihat layer_mapping.csv) |
| 112 | `03_PNG_Layers/13_FACE_COMPONENTS_ALTERNATES/ALT_IRIS_FULL_RIGHT.png` | PNG layer (kanvas 1024x1536) | Komponen wajah pengganti: ALT_IRIS_FULL_RIGHT | Tersembunyi (opsional); terdekode; belum diselaraskan | Selaraskan lalu aktifkan sebagai pengganti (lihat layer_mapping.csv) |
| 113 | `03_PNG_Layers/13_FACE_COMPONENTS_ALTERNATES/ALT_LASH_LOWER_LEFT.png` | PNG layer (kanvas 1024x1536) | Komponen wajah pengganti: ALT_LASH_LOWER_LEFT | Tersembunyi (opsional); terdekode; belum diselaraskan | Selaraskan lalu aktifkan sebagai pengganti (lihat layer_mapping.csv) |
| 114 | `03_PNG_Layers/13_FACE_COMPONENTS_ALTERNATES/ALT_LASH_LOWER_RIGHT.png` | PNG layer (kanvas 1024x1536) | Komponen wajah pengganti: ALT_LASH_LOWER_RIGHT | Tersembunyi (opsional); terdekode; belum diselaraskan | Selaraskan lalu aktifkan sebagai pengganti (lihat layer_mapping.csv) |
| 115 | `03_PNG_Layers/13_FACE_COMPONENTS_ALTERNATES/ALT_LASH_UPPER_LEFT.png` | PNG layer (kanvas 1024x1536) | Komponen wajah pengganti: ALT_LASH_UPPER_LEFT | Tersembunyi (opsional); terdekode; belum diselaraskan | Selaraskan lalu aktifkan sebagai pengganti (lihat layer_mapping.csv) |
| 116 | `03_PNG_Layers/13_FACE_COMPONENTS_ALTERNATES/ALT_LASH_UPPER_RIGHT.png` | PNG layer (kanvas 1024x1536) | Komponen wajah pengganti: ALT_LASH_UPPER_RIGHT | Tersembunyi (opsional); terdekode; belum diselaraskan | Selaraskan lalu aktifkan sebagai pengganti (lihat layer_mapping.csv) |
| 117 | `03_PNG_Layers/13_FACE_COMPONENTS_ALTERNATES/ALT_MOUTH_CLOSED_ALT.png` | PNG layer (kanvas 1024x1536) | Komponen wajah pengganti: ALT_MOUTH_CLOSED_ALT | Tersembunyi (opsional); terdekode; belum diselaraskan | Selaraskan lalu aktifkan sebagai pengganti (lihat layer_mapping.csv) |
| 118 | `03_PNG_Layers/13_FACE_COMPONENTS_ALTERNATES/ALT_MOUTH_INSIDE.png` | PNG layer (kanvas 1024x1536) | Komponen wajah pengganti: ALT_MOUTH_INSIDE | Tersembunyi (opsional); terdekode; belum diselaraskan | Selaraskan lalu aktifkan sebagai pengganti (lihat layer_mapping.csv) |
| 119 | `03_PNG_Layers/13_FACE_COMPONENTS_ALTERNATES/ALT_MOUTH_LOWER.png` | PNG layer (kanvas 1024x1536) | Komponen wajah pengganti: ALT_MOUTH_LOWER | Tersembunyi (opsional); terdekode; belum diselaraskan | Selaraskan lalu aktifkan sebagai pengganti (lihat layer_mapping.csv) |
| 120 | `03_PNG_Layers/13_FACE_COMPONENTS_ALTERNATES/ALT_MOUTH_UPPER.png` | PNG layer (kanvas 1024x1536) | Komponen wajah pengganti: ALT_MOUTH_UPPER | Tersembunyi (opsional); terdekode; belum diselaraskan | Selaraskan lalu aktifkan sebagai pengganti (lihat layer_mapping.csv) |
| 121 | `03_PNG_Layers/13_FACE_COMPONENTS_ALTERNATES/ALT_PUPIL_FULL_LEFT.png` | PNG layer (kanvas 1024x1536) | Komponen wajah pengganti: ALT_PUPIL_FULL_LEFT | Tersembunyi (opsional); terdekode; belum diselaraskan | Selaraskan lalu aktifkan sebagai pengganti (lihat layer_mapping.csv) |
| 122 | `03_PNG_Layers/13_FACE_COMPONENTS_ALTERNATES/ALT_PUPIL_FULL_RIGHT.png` | PNG layer (kanvas 1024x1536) | Komponen wajah pengganti: ALT_PUPIL_FULL_RIGHT | Tersembunyi (opsional); terdekode; belum diselaraskan | Selaraskan lalu aktifkan sebagai pengganti (lihat layer_mapping.csv) |
| 123 | `03_PNG_Layers/13_FACE_COMPONENTS_ALTERNATES/ALT_SCLERA_LEFT.png` | PNG layer (kanvas 1024x1536) | Komponen wajah pengganti: ALT_SCLERA_LEFT | Tersembunyi (opsional); terdekode; belum diselaraskan | Selaraskan lalu aktifkan sebagai pengganti (lihat layer_mapping.csv) |
| 124 | `03_PNG_Layers/13_FACE_COMPONENTS_ALTERNATES/ALT_SCLERA_RIGHT.png` | PNG layer (kanvas 1024x1536) | Komponen wajah pengganti: ALT_SCLERA_RIGHT | Tersembunyi (opsional); terdekode; belum diselaraskan | Selaraskan lalu aktifkan sebagai pengganti (lihat layer_mapping.csv) |
| 125 | `03_PNG_Layers/13_FACE_COMPONENTS_ALTERNATES/ALT_TEETH.png` | PNG layer (kanvas 1024x1536) | Komponen wajah pengganti: ALT_TEETH | Tersembunyi (opsional); terdekode; belum diselaraskan | Selaraskan lalu aktifkan sebagai pengganti (lihat layer_mapping.csv) |
| 126 | `03_PNG_Layers/13_FACE_COMPONENTS_ALTERNATES/ALT_TONGUE.png` | PNG layer (kanvas 1024x1536) | Komponen wajah pengganti: ALT_TONGUE | Tersembunyi (opsional); terdekode; belum diselaraskan | Selaraskan lalu aktifkan sebagai pengganti (lihat layer_mapping.csv) |
| 127 | `03_PNG_Layers/Face_Components_Highres/BLUSH_LEFT.png` | PNG komponen resolusi sumber | Blush kiri (resolusi sumber) | Terdekode; 279x189 px; tidak ada di PSD maupun manifest | Kandidat bahan resolusi tinggi untuk komponen ALT_*; putuskan skala kanvas dulu |
| 128 | `03_PNG_Layers/Face_Components_Highres/BLUSH_RIGHT.png` | PNG komponen resolusi sumber | Blush kanan (resolusi sumber) | Terdekode; 277x193 px; tidak ada di PSD maupun manifest | Kandidat bahan resolusi tinggi untuk komponen ALT_*; putuskan skala kanvas dulu |
| 129 | `03_PNG_Layers/Face_Components_Highres/EYEBROW_FULL_LEFT.png` | PNG komponen resolusi sumber | Alis penuh kiri (resolusi sumber) | Terdekode; 294x70 px; tidak ada di PSD maupun manifest | Kandidat bahan resolusi tinggi untuk komponen ALT_*; putuskan skala kanvas dulu |
| 130 | `03_PNG_Layers/Face_Components_Highres/EYEBROW_FULL_RIGHT.png` | PNG komponen resolusi sumber | Alis penuh kanan (resolusi sumber) | Terdekode; 295x70 px; tidak ada di PSD maupun manifest | Kandidat bahan resolusi tinggi untuk komponen ALT_*; putuskan skala kanvas dulu |
| 131 | `03_PNG_Layers/Face_Components_Highres/GLINT_LEFT.png` | PNG komponen resolusi sumber | Kilau mata kiri (resolusi sumber) | Terdekode; 135x309 px; tidak ada di PSD maupun manifest | Kandidat bahan resolusi tinggi untuk komponen ALT_*; putuskan skala kanvas dulu |
| 132 | `03_PNG_Layers/Face_Components_Highres/GLINT_RIGHT.png` | PNG komponen resolusi sumber | Kilau mata kanan (resolusi sumber) | Terdekode; 142x309 px; tidak ada di PSD maupun manifest | Kandidat bahan resolusi tinggi untuk komponen ALT_*; putuskan skala kanvas dulu |
| 133 | `03_PNG_Layers/Face_Components_Highres/IRIS_FULL_LEFT.png` | PNG komponen resolusi sumber | Iris penuh kiri (resolusi sumber) | Terdekode; 210x196 px; tidak ada di PSD maupun manifest | Kandidat bahan resolusi tinggi untuk komponen ALT_*; putuskan skala kanvas dulu |
| 134 | `03_PNG_Layers/Face_Components_Highres/IRIS_FULL_RIGHT.png` | PNG komponen resolusi sumber | Iris penuh kanan (resolusi sumber) | Terdekode; 291x196 px; tidak ada di PSD maupun manifest | Kandidat bahan resolusi tinggi untuk komponen ALT_*; putuskan skala kanvas dulu |
| 135 | `03_PNG_Layers/Face_Components_Highres/LASH_LOWER_LEFT.png` | PNG komponen resolusi sumber | Bulu mata bawah kiri (resolusi sumber) | Terdekode; 165x89 px; tidak ada di PSD maupun manifest | Kandidat bahan resolusi tinggi untuk komponen ALT_*; putuskan skala kanvas dulu |
| 136 | `03_PNG_Layers/Face_Components_Highres/LASH_LOWER_RIGHT.png` | PNG komponen resolusi sumber | Bulu mata bawah kanan (resolusi sumber) | Terdekode; 243x87 px; tidak ada di PSD maupun manifest | Kandidat bahan resolusi tinggi untuk komponen ALT_*; putuskan skala kanvas dulu |
| 137 | `03_PNG_Layers/Face_Components_Highres/LASH_UPPER_LEFT.png` | PNG komponen resolusi sumber | Bulu mata atas kiri (resolusi sumber) | Terdekode; 313x103 px; tidak ada di PSD maupun manifest | Kandidat bahan resolusi tinggi untuk komponen ALT_*; putuskan skala kanvas dulu |
| 138 | `03_PNG_Layers/Face_Components_Highres/LASH_UPPER_RIGHT.png` | PNG komponen resolusi sumber | Bulu mata atas kanan (resolusi sumber) | Terdekode; 268x104 px; tidak ada di PSD maupun manifest | Kandidat bahan resolusi tinggi untuk komponen ALT_*; putuskan skala kanvas dulu |
| 139 | `03_PNG_Layers/Face_Components_Highres/MOUTH_CLOSED_ALT.png` | PNG komponen resolusi sumber | Mulut tertutup alternatif (resolusi sumber) | Terdekode; 178x13 px; tidak ada di PSD maupun manifest | Kandidat bahan resolusi tinggi untuk komponen ALT_*; putuskan skala kanvas dulu |
| 140 | `03_PNG_Layers/Face_Components_Highres/MOUTH_INSIDE.png` | PNG komponen resolusi sumber | Rongga mulut (resolusi sumber) | Terdekode; 180x74 px; tidak ada di PSD maupun manifest | Kandidat bahan resolusi tinggi untuk komponen ALT_*; putuskan skala kanvas dulu |
| 141 | `03_PNG_Layers/Face_Components_Highres/MOUTH_LOWER.png` | PNG komponen resolusi sumber | Bibir bawah (resolusi sumber) | Terdekode; 100x27 px; tidak ada di PSD maupun manifest | Kandidat bahan resolusi tinggi untuk komponen ALT_*; putuskan skala kanvas dulu |
| 142 | `03_PNG_Layers/Face_Components_Highres/MOUTH_UPPER.png` | PNG komponen resolusi sumber | Bibir atas (resolusi sumber) | Terdekode; 196x32 px; tidak ada di PSD maupun manifest | Kandidat bahan resolusi tinggi untuk komponen ALT_*; putuskan skala kanvas dulu |
| 143 | `03_PNG_Layers/Face_Components_Highres/PUPIL_FULL_LEFT.png` | PNG komponen resolusi sumber | Pupil penuh kiri (resolusi sumber) | Terdekode; 42x103 px; tidak ada di PSD maupun manifest | Kandidat bahan resolusi tinggi untuk komponen ALT_*; putuskan skala kanvas dulu |
| 144 | `03_PNG_Layers/Face_Components_Highres/PUPIL_FULL_RIGHT.png` | PNG komponen resolusi sumber | Pupil penuh kanan (resolusi sumber) | Terdekode; 42x103 px; tidak ada di PSD maupun manifest | Kandidat bahan resolusi tinggi untuk komponen ALT_*; putuskan skala kanvas dulu |
| 145 | `03_PNG_Layers/Face_Components_Highres/SCLERA_LEFT.png` | PNG komponen resolusi sumber | Sclera kiri (resolusi sumber) | Terdekode; 235x140 px; tidak ada di PSD maupun manifest | Kandidat bahan resolusi tinggi untuk komponen ALT_*; putuskan skala kanvas dulu |
| 146 | `03_PNG_Layers/Face_Components_Highres/SCLERA_RIGHT.png` | PNG komponen resolusi sumber | Sclera kanan (resolusi sumber) | Terdekode; 245x139 px; tidak ada di PSD maupun manifest | Kandidat bahan resolusi tinggi untuk komponen ALT_*; putuskan skala kanvas dulu |
| 147 | `03_PNG_Layers/Face_Components_Highres/TEETH.png` | PNG komponen resolusi sumber | Gigi (resolusi sumber) | Terdekode; 173x43 px; tidak ada di PSD maupun manifest | Kandidat bahan resolusi tinggi untuk komponen ALT_*; putuskan skala kanvas dulu |
| 148 | `03_PNG_Layers/Face_Components_Highres/TONGUE.png` | PNG komponen resolusi sumber | Lidah (resolusi sumber) | Terdekode; 114x75 px; tidak ada di PSD maupun manifest | Kandidat bahan resolusi tinggi untuk komponen ALT_*; putuskan skala kanvas dulu |
| 149 | `04_Rigging_Spec/Aoi_Cetara_TEMPLATE.physics3.json` | JSON template | Template physics 12 grup (v1) | Parse OK; skema lengkap; BELUM dituning; hanya 2 kombinasi input dan 3 profil bandul | Jangan dipakai sebagai physics final; rancang ulang di Cubism (lihat physics_plan.csv) |
| 150 | `04_Rigging_Spec/Brief_Parameter_Mapping.json` | JSON | Pemetaan nama brief ke ID parameter | Parse OK | Gunakan |
| 151 | `04_Rigging_Spec/Deformer_Hierarchy.spec.json` | JSON rencana | Rencana deformer v1 (bukan impor native) | Parse OK; tanpa deformer alis, rambut samping, leher, kaki | Gantikan dengan deformer_plan.csv |
| 152 | `04_Rigging_Spec/Motion_Templates/Blink_Once_TEMPLATE.motion3.json` | JSON template | Kurva satu kedipan 0.3 s | Parse OK; ID parameter valid; belum dimainkan pada model | Pakai setelah keyform mata dibuat |
| 153 | `04_Rigging_Spec/Motion_Templates/Breath_Idle_TEMPLATE.motion3.json` | JSON template | Kurva napas loop 4 s | Parse OK; ID parameter valid; belum dimainkan | Pakai setelah ParamBreath dibuat |
| 154 | `04_Rigging_Spec/PANDUAN_CUBISM.md` | Markdown | Panduan alur v1 | Terbaca | Acuan; koreksi polaritas alis (lihat rigging_specification.md) |
| 155 | `04_Rigging_Spec/Parameter_Spec.csv` | CSV | 35 parameter v1 | Parse OK; semua KEYFORMS_NOT_BUILT | Gantikan dengan parameter_map.csv |
| 156 | `04_Rigging_Spec/Parameter_Spec.json` | JSON | 35 parameter v1 (JSON) | Parse OK | Arsip |
| 157 | `04_Rigging_Spec/Runtime_Export_Contract.json` | JSON | Kontrak ekspor: status NOT_EXPORTED_NOT_LOADABLE | Parse OK; sesuai kenyataan (tidak ada .cmo3/.moc3/.model3.json) | Pertahankan sampai ekspor nyata |
| 158 | `04_Rigging_Spec/SUMBER_TEKNIS.md` | Markdown | Daftar dokumentasi resmi | Terbaca | Acuan |
| 159 | `04_Rigging_Spec/VTube_Studio_Mapping.spec.json` | JSON panduan | Panduan pemetaan input VTS (bukan file VTS) | Parse OK; status GUIDE_ONLY | Verifikasi nama input di VTS Model Settings |
| 160 | `05_Expression_Templates/ANGRY.exp3.json` | JSON template | Resep ekspresi ANGRY (v1) | Parse OK; ID parameter valid; belum diuji pada model; polaritas alis terbalik | Susun ulang sesuai expression_plan.csv |
| 161 | `05_Expression_Templates/BLINK.exp3.json` | JSON template | Resep ekspresi BLINK (v1) | Parse OK; ID parameter valid; belum diuji pada model | Susun ulang sesuai expression_plan.csv |
| 162 | `05_Expression_Templates/DEFAULT.exp3.json` | JSON template | Resep ekspresi DEFAULT (v1) | Parse OK; ID parameter valid; belum diuji pada model | Pakai setelah keyform siap |
| 163 | `05_Expression_Templates/HAPPY.exp3.json` | JSON template | Resep ekspresi HAPPY (v1) | Parse OK; ID parameter valid; belum diuji pada model | Pakai setelah keyform siap |
| 164 | `05_Expression_Templates/SAD.exp3.json` | JSON template | Resep ekspresi SAD (v1) | Parse OK; ID parameter valid; belum diuji pada model; polaritas alis terbalik | Susun ulang sesuai expression_plan.csv |
| 165 | `05_Expression_Templates/SHY.exp3.json` | JSON template | Resep ekspresi SHY (v1) | Parse OK; ID parameter valid; belum diuji pada model | Pakai setelah keyform siap |
| 166 | `05_Expression_Templates/SMILE.exp3.json` | JSON template | Resep ekspresi SMILE (v1) | Parse OK; ID parameter valid; belum diuji pada model | Pakai setelah keyform siap |
| 167 | `05_Expression_Templates/SURPRISED.exp3.json` | JSON template | Resep ekspresi SURPRISED (v1) | Parse OK; ID parameter valid; belum diuji pada model | Susun ulang sesuai expression_plan.csv |
| 168 | `05_Expression_Templates/WINK.exp3.json` | JSON template | Resep ekspresi WINK (v1) | Parse OK; ID parameter valid; belum diuji pada model | Susun ulang sesuai expression_plan.csv |
| 169 | `06_Previews/Aoi_Cetara_Layered_Composite.png` | PNG preview | Komposit default layer aktif | Terdekode; piksel alpha = 964.002 sama dengan gabungan layer aktif | Bukti susunan utuh, bukan bukti kelayakan gerak |
| 170 | `06_Previews/Layer_Contact_Sheet.jpg` | JPG preview | Ikhtisar isi layer | Terdekode | Acuan visual |
| 171 | `06_Previews/Neutral_Background_Check.jpg` | JPG preview | Cek latar netral | Terdekode | Acuan visual |
| 172 | `06_Previews/QA_RINGKAS.md` | Markdown | Ringkasan QA v1 | Terbaca; sebagian klaim diverifikasi ulang di dokumen ini | Acuan |
| 173 | `06_Previews/QA_Result.json` | JSON | Hasil QA v1 | Parse OK | Acuan |
| 174 | `07_Tools/build_layered_art.py` | Python | Skrip pemisahan layer v1 | Sintaks Python valid (diparse AST; tidak dijalankan) | Tidak dijalankan (akan menimpa hasil retouch); jalankan dari salinan kerja |
| 175 | `07_Tools/build_rigging_templates.py` | Python | Skrip pembuat template rigging v1 | Sintaks Python valid (diparse AST; tidak dijalankan) | Tidak dijalankan |
| 176 | `07_Tools/repack_artwork.py` | Python | Skrip pengemas ulang artwork v1 | Sintaks Python valid (diparse AST; tidak dijalankan) | Tidak dijalankan |
| 177 | `07_Tools/requirements.txt` | Teks | Dependensi skrip v1 (Pillow, numpy, psd-tools 1.25.0) | Terbaca | psd-tools tidak terpasang di lingkungan audit; tidak dibutuhkan skrip audit ini |
| 178 | `README_MULAI_DI_SINI.md` | Markdown | README paket v1 | Terbaca; jujur soal status (tidak ada model) | Acuan |
| 179 | `SHA256SUMS.txt` | Teks | Checksum 178 berkas | 178/178 cocok | Pakai untuk memeriksa integritas |

## 6. Ringkasan perbaikan artwork

Jumlah layer per prioritas pada `layer_mapping.csv`: P0 = 36, P1 = 44, P2 = 33. Urutan kerja ada di `rigging_checklist.md` (status seluruh perbaikan artwork: **BLOCKED**, butuh ilustrator/editor gambar).
