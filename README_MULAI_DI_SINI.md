# Aoi Cetara — paket artwork dan persiapan Live2D v1

**Status: artwork berlayer tahap awal dan template rigging. Belum menjadi model yang dapat dipasang di VTube Studio.**

Karakter mengikuti referensi: perempuan dewasa muda bertema paus biru, rambut panjang icy blue–silver, gaun putih–biru muda, tiara, ornamen ekor paus, bunga, mutiara, dan perhiasan laut. Artwork utama memakai pandangan depan, ekspresi tenang, serta mulut tertutup.

## Buka file ini terlebih dahulu

- `02_Layered_Artwork/Aoi_Cetara_ArtPrep_v1.psd` — artwork dengan 113 layer raster yang dapat diedit.
- `06_Previews/Aoi_Cetara_Layered_Composite.png` — tampilan default hasil susunan layer.
- `06_Previews/Layer_Contact_Sheet.jpg` — ikhtisar isi layer.
- `04_Rigging_Spec/PANDUAN_CUBISM.md` — urutan pekerjaan hingga ekspor ke VTube Studio.

## Isi paket dan batas penggunaannya

| Komponen | Tersedia | Status |
| --- | --- | --- |
| Master karakter transparan | PNG 1024 × 1536 | Artwork netral; resolusi asli, tidak diklaim sebagai 4K |
| Artwork berlayer | PSD dan OpenRaster/ORA | 86 potongan aktif + 5 backfill + 22 komponen wajah opsional |
| PNG setiap layer | 113 PNG berukuran kanvas sama | Nama, koordinat, pivot, dan status ada di manifest |
| Komponen wajah resolusi sumber | 22 PNG tambahan | Iris utuh, pupil, glint, sclera, eyelash, bibir, mulut, gigi, lidah, blush, alis |
| Parameter dan struktur deformer | 35 parameter; rencana hierarki | Spesifikasi untuk dibuat di Cubism, belum terhubung ke mesh |
| Ekspresi | 9 `.exp3.json` | Template yang memerlukan parameter dan keyform yang sesuai |
| Physics | 12 pengaturan dalam template `.physics3.json` | Nilai awal; belum diuji terhadap rig |
| Gerak | Template kedipan dan napas `.motion3.json` | Data kurva saja; belum ada model untuk memainkannya |
| Proyek/hasil ekspor Cubism | `.cmo3`, `.moc3`, `.model3.json`, atlas runtime | **Belum tersedia** |

Pemisahan aktif dibuat dari piksel master menggunakan batas bagian yang dapat diedit. Susunan default merekonstruksi piksel artwork utama. Ini membuktikan susunannya utuh, **bukan** bahwa setiap potongan sudah aman untuk semua sudut gerak. Potongan rantai, renda, aksesori kecil, batas rambut, serta sambungan kulit/kain masih memerlukan pemeriksaan dan retouch.

Lima backfill berasal dari artwork tambahan yang direkonstruksi. Layer tersebut, bersama komponen wajah pengganti, sengaja tersembunyi pada susunan awal karena posisi, kontur, dan warnanya harus diselaraskan terlebih dahulu. Jangan menyalakan semua layer pengganti sekaligus; ganti bagian yang sesuai dan sembunyikan versi lamanya. Di Cubism, atur opacity bagian opsional secara eksplisit karena layer tersembunyi PSD juga dapat diimpor.

## Tiga langkah berikutnya

1. **Rapikan artwork.** Buka PSD di Photoshop atau Clip Studio Paint. Periksa tepi potongan, selaraskan backfill, lengkapi bidang tersembunyi di sambungan, lalu susun mata dan bibir pengganti. Simpan salinan PSD untuk impor.
2. **Kerjakan rig di Cubism.** Buat ArtMesh, clipping, deformer dan keyform mengikuti spesifikasi. Uji kombinasi gerak, lip-sync, dan physics. Simpan proyek `.cmo3`.
3. **Ekspor dan uji di VTube Studio.** Ekspor `.moc3` beserta `.model3.json`, atlas tekstur, dan physics. Masukkan seluruh folder hasil ekspor ke folder model VTube Studio, lalu kalibrasikan pelacakan dan hotkey.

## Catatan penting untuk rigger

- `LEFT` dan `RIGHT` selalu mengikuti sisi anatomi karakter. Mata di kiri layar adalah `RIGHT`, terkait `ParamEyeROpen`.
- Default: `ParamMouthOpenY = 0`, `ParamMouthForm = 0`, kedua mata terbuka, `ParamCheek = 0`, dan tidak ada ekspresi emosi aktif.
- `DEFAULT.exp3.json` adalah resep reset bentuk emosi, bukan pengganti posisi default pada rig. Jangan menjadikannya cara mengunci semua parameter pelacakan.
- `BLINK.exp3.json` menahan mata tertutup selama aktif. Untuk satu kedipan, gunakan `Blink_Once_TEMPLATE.motion3.json` setelah keyform tersedia.
- `SURPRISED.exp3.json` mengatur bukaan mulut. Nonaktifkan kembali agar tidak mengunci bukaan saat lip-sync.
- Lima vokal A–I–U–E–O dicatat sebagai keyform `ParamMouthVowel`. Input volume audio saja tidak mengenali vokal; penggerak fonem tambahan diperlukan jika ingin pemilihan vokal otomatis.
- Tidak ada file `.moc3` kosong atau `.model3.json` palsu. Template JSON tidak menggantikan rig dan tidak dapat digunakan sendirian sebagai model.

## Pemeriksaan yang sudah dilakukan

Nama layer unik, layer tidak kosong, kedalaman 8-bit, profil sRGB, tidak memakai layer mask PSD, dan rekonstruksi default cocok dengan master pada piksel terlihat. PSD dibuka kembali untuk memeriksa strukturnya. Referensi parameter dalam template diperiksa terhadap daftar parameter proyek. Rincian tersedia di `06_Previews/QA_Result.json`.

Impor native Cubism, deformasi saat bergerak, physics pada model, serta pemuatan VTube Studio **belum diuji**, karena Cubism Editor dan runtime model tidak tersedia di lingkungan pengerjaan.

## Sumber dan reproduksi

Artwork dibuat melalui imagegen berdasarkan referensi yang diberikan. Semua plate asli dan prompt disimpan di `01_Source`. Skrip di `07_Tools` melakukan pemisahan teknis, penyusunan berkas, dan pembuatan spesifikasi; skrip tersebut tidak membuat atau mengompilasi model Live2D. Untuk menjalankannya kembali, pasang dependensi di `07_Tools/requirements.txt`. Jalankan dari salinan kerja agar hasil retouch manual tidak tertimpa.

Dokumentasi resmi yang menjadi acuan teknis tercantum di `04_Rigging_Spec/SUMBER_TEKNIS.md`.
