# Penyelesaian Aoi Cetara di Cubism

Status awal paket: artwork terpisah tahap awal; belum ada mesh, keyform, rig native, atau atlas runtime.

## 1. Siapkan PSD impor

Buka `Aoi_Cetara_ArtPrep_v1.psd`. Pertahankan ukuran 1024 × 1536, RGB 8-bit/channel dan sRGB. Simpan hasil yang dirapikan dengan nama baru, misalnya `Aoi_Cetara_Import_t001.psd`. Bila PSD hasil program tidak terbaca di Cubism, buka lalu simpan ulang melalui Photoshop atau Clip Studio Paint; keduanya merupakan aplikasi yang secara resmi dikonfirmasi Live2D untuk impor PSD.

Periksa dahulu bagian berikut:

| Bagian | Tindakan sebelum rig |
| --- | --- |
| Rambut dan aksesori | Bersihkan sisa warna bagian tetangga di batas potongan; tambahkan overlap akar–ujung |
| Kepala dan leher | Selaraskan `BF_FACE_COMPLETE` dan `BF_NECK_AND_TORSO`; isi kulit di belakang mata, mulut, dan rambut |
| Lengan dan kain | Isi sambungan yang tersembunyi, termasuk pakaian di belakang lengan; jangan menganggap plate backfill sudah mencakup semua gerak |
| Mata | Pasang sclera utuh, iris utuh, pupil dan glint; gunakan eyelid asli atau pengganti yang paling konsisten |
| Mulut | Ganti garis tunggal dengan `ALT_MOUTH_UPPER`, `ALT_MOUTH_LOWER`, `ALT_MOUTH_INSIDE`, `ALT_TEETH`, `ALT_TONGUE`; selaraskan kontur serta shading |
| Blush | Letakkan masing-masing pada pipi; opacity default 0 |

Jangan gabungkan seluruh karakter. Gabungkan hanya lineart, warna, atau efek yang memang merupakan satu bagian gerak. Pertahankan nama bagian yang unik. Hindari layer mask pada PSD impor; terapkan mask menjadi transparansi layer sebelum menyimpan.

## 2. Buat model dan mesh

Impor PSD melalui File → Open atau tarik ke area Modeling, lalu buat model baru. Susunan layer menjadi bahan ArtMesh; impor saja belum menghasilkan rig. Periksa opacity seluruh bagian opsional setelah impor.

Buat mesh lebih rapat di kelopak, bibir, ujung rambut, serta lipatan kain yang akan melengkung. Gunakan mesh sederhana pada aksesori kaku. Periksa draw order: rambut belakang berada di belakang badan; mata dan mulut berada di atas wajah; bangs dan aksesori kepala berada di atasnya.

## 3. Bangun deformer dan keyform

Gunakan `Deformer_Hierarchy.spec.json` sebagai rencana, bukan file impor native. Titik pivot di manifest memakai koordinat piksel sumber dengan titik nol di kiri atas; sesuaikan dengan ruang koordinat editor.

Mulai dari kedipan dan mulut, lalu kepala, badan, rambut, dan pakaian. Detail parameter ada di `Parameter_Spec.csv`.

- Kepala: buat keyform X/Y/Z pada −30, 0, +30. Periksa kombinasi X–Y serta sudut diagonal; kurangi rentang sementara jika backfill belum cukup.
- Mata: buat buka/tutup 0–1, senyum 0–1, dan pandangan X/Y −1 sampai +1. Clip iris/pupil/glint pada area sclera; pada mata tertutup tidak boleh tersisa iris atau putih mata.
- Mulut: buat grid `ParamMouthOpenY` × `ParamMouthForm`. Ketika bukaan 0, interior, gigi, dan lidah tidak terlihat. Bentuk netral harus tertutup dan tanpa senyum.
- Vokal tambahan: buat `ParamMouthVowel` 0 netral, 1 A, 2 I, 3 U, 4 E, 5 O. Nilai ini merupakan rancangan khusus proyek, bukan detektor vokal otomatis.
- Badan: gerakkan ringan pada `ParamBodyAngleX/Y/Z`; pertahankan posisi kaki. Napas memakai `ParamBreath`.
- Physics: bangun bentuk pada nilai −1, 0, +1 untuk setiap parameter output sway sebelum memasang simulasi. Parameter yang belum memiliki keyform tidak akan menggerakkan artwork.

## 4. Atur physics dan ekspresi

`Aoi_Cetara_TEMPLATE.physics3.json` berisi rancangan 12 kelompok. Gunakan sebagai referensi penyusunan physics atau uji alur pemuatan yang didukung versi Cubism yang dipakai. Sesuaikan output, kecepatan, dan amplitudo terhadap rig nyata; nilai dalam template belum dituning melalui simulasi. Ekspor ulang physics bersama model final.

Uji satu gerakan kepala singkat, lalu hentikan. Rambut, pita, rok, rantai dan anting seharusnya mereda tanpa getaran berkepanjangan. Hindari membuat semua bagian bergerak identik atau menembus wajah dan tubuh.

Sembilan `.exp3.json` adalah resep parameter. Terapkan hanya setelah keyform terkait berfungsi. Aktifkan satu emosi pada satu waktu agar parameter overwrite tidak saling menimpa. Rilis ekspresi BLINK/WINK setelah digunakan. Template gerak di `Motion_Templates` memerlukan parameter dan rig yang sama.

## 5. Ekspor runtime

Simpan proyek sebagai `.cmo3`. Buat texture atlas, kemudian pilih File → Export For Runtime → Export as .moc3 file. Pilih target SDK stabil yang didukung versi VTube Studio yang digunakan; sertakan ekspor physics.

Pastikan folder hasil ekspor memiliki `.moc3`, `.model3.json`, atlas PNG yang direferensikan, dan physics hasil ekspor. Gunakan `.model3.json` yang dibuat Cubism. Nama serta jalur pada file itu harus cocok dengan berkas nyata. Tambahkan ekspresi dan motion yang sudah diuji sesuai alur pengaturan aplikasi.

## 6. Uji di VTube Studio

Buka lokasi folder model dari VTube Studio, lalu salin satu folder hasil ekspor lengkap ke `Live2DModels`. Muat ulang aplikasi bila model belum muncul. Kalibrasikan kamera dan periksa pemetaan parameter. Jangan menyalin folder ArtPrep ini sebagai pengganti folder runtime.

Luluskan pemeriksaan berikut sebelum menyebut model siap dipakai: kedipan tanpa kebocoran; iris tidak keluar sclera; mulut kembali tertutup saat diam; tidak ada lubang saat kepala berputar; aksesori tidak lepas dari pivot; physics stabil; ekspresi dapat dimatikan; tekstur dan file model dapat dimuat tanpa error.
