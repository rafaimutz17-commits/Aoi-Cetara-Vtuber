# Pemeriksaan hasil Aoi Cetara v1

Hasil ini merupakan paket persiapan artwork. Pemeriksaan file berhasil; kelayakan deformasi masih perlu dinilai saat rigging.

| Kriteria | Hasil |
| --- | --- |
| Wajah netral, pandangan depan, mulut tertutup | Terlihat pada artwork default |
| Full body, kedua tangan dan sepatu terlihat | Terlihat pada artwork default |
| Rambut panjang dan identitas paus biru | Terlihat; ornamen ekor paus dipisah |
| Dominasi biru muda–putih dan aksesori | Dipertahankan dari brief |
| Layer nyata | 113 layer raster: 86 aktif, 5 backfill, 22 komponen wajah opsional |
| Rekonstruksi dari layer aktif | Identik dengan master pada piksel terlihat |
| PSD | RGB, 8-bit/channel, sRGB, nama unik, tidak memakai layer mask |
| Render PSD oleh pembaca lain | Berhasil melalui ImageMagick; alpha identik, perbedaan RGB tampilan kurang dari 1/255 akibat pembulatan |
| PNG tiap layer | Semua dapat didekode; tidak ada PNG kosong/rusak pada hasil akhir |
| OpenRaster | Arsip berisi 117 entri; CRC valid |
| Template JSON | Dapat diparse; parameter yang direferensikan tercantum dalam spesifikasi |
| Batas potongan dan overlap | Perlu retouch, terutama rantai/renda dan sambungan rambut/kain |
| Backfill | Tersedia sebagai plate terpisah; posisi dan kontur perlu diselaraskan; belum mencakup semua kemungkinan deformasi |
| Mata untuk tracking | Komponen tersedia; clipping dan keyform belum dibuat |
| Mulut untuk lip-sync | Komponen tersedia; keyform bukaan, bentuk, dan vokal belum dibuat |
| Physics | Template 12 kelompok tersedia; belum diuji pada rig |
| Cubism dan VTube Studio | Belum diuji; tidak tersedia proyek `.cmo3`, binary `.moc3`, index runtime `.model3.json`, maupun atlas runtime |

Rincian numerik ada di `QA_Result.json`. Preview merupakan susunan artwork netral, bukan bukti model telah bergerak.
