Saya ingin kamu bertindak sebagai **2D VTuber Character Artist + Live2D Cubism Rigging Specialist + Technical Artist**.

Tugasmu adalah membuat satu karakter VTuber 2D perempuan original berdasarkan gambar referensi yang saya lampirkan, lalu menyiapkan seluruh aset dan struktur yang diperlukan agar karakter tersebut dapat digunakan sebagai model VTuber Live2D.

JANGAN hanya membuat ilustrasi karakter biasa.

Target akhir saya adalah:
**CHARACTER DESIGN → LAYERED ART ASSETS → LIVE2D RIGGING → MODEL SIAP DIGUNAKAN DI VTUBE STUDIO**

\========================

1. IDENTITAS KARAKTER
   \========================

Karakter adalah perempuan dewasa muda dengan tema utama **BLUE WHALE / OCEAN FANTASY**.

Karakter harus memiliki:

- rambut sangat panjang, mengalir hingga melewati pinggang
- warna rambut dominan icy blue, light blue, dan silver-white
- sedikit aksen ocean blue
- mata besar tetapi elegan
- iris ocean blue/cyan
- desain feminin, elegan, cute tetapi tetap mature
- nuansa laut dalam, paus biru, ombak, mutiara, gelembung, sirip, dan ekor paus
- outfit fantasy yang elegan
- warna utama light blue + white + silver
- aksen tambahan lavender/pale cyan/soft gold secukupnya
- banyak aksesori tetapi tetap harmonis
- silhouette karakter harus mudah dikenali

Karakter tidak boleh terlihat seperti memakai kostum paus.

Inspirasi paus harus diterapkan secara elegan melalui:

- motif whale tail
- bentuk fin
- wave pattern
- pearl
- bubble
- ocean crystal
- whale-inspired jewelry
- ornamen rambut
- ornamen pakaian

# ======================== 2. EKSPRESI WAJIB

Ekspresi default karakter HARUS:

**NORMAL, NEUTRAL, CALM, NATURAL**

Ketika karakter sedang diam:

- mata rileks
- alis rileks
- mulut tertutup
- tidak tersenyum
- tidak cemberut
- tidak terkejut
- tidak marah
- tidak sedih
- tidak blush berlebihan
- tidak membuka mulut
- tidak wink
- tidak membuat ekspresi dramatis

Tatapan mengarah natural ke depan.

Karakter harus terlihat seperti sedang idle dalam stream, bukan sedang melakukan pose promosi.

Ekspresi emosional dibuat sebagai parameter terpisah untuk rigging, bukan sebagai ekspresi default.

# ======================== 3. POSE

Buat karakter dalam:

- front-facing
- full body
- berdiri tegak
- posisi tubuh natural
- kepala menghadap kamera
- kedua kaki terlihat
- kedua tangan terlihat
- tidak ada bagian tubuh yang terpotong
- tidak ada pose dinamis
- tidak ada perspektif ekstrem

Pose harus ideal untuk pembuatan model Live2D.

Hindari:

- tangan menutupi wajah
- rambut menutupi seluruh tubuh
- aksesori saling menutupi
- pakaian menyatu tanpa batas layer
- bagian tubuh tersembunyi
- pose menyamping ekstrem

# ======================== 4. DESAIN RAMBUT

Rambut adalah salah satu identitas utama karakter.

Buat rambut:

- sangat panjang
- silky
- flowing
- layered
- memiliki banyak strand
- memiliki bagian depan, samping, dan belakang yang jelas
- ujung rambut sedikit transparan/berkilau
- memiliki gerakan seperti air laut
- memiliki beberapa strand yang dapat dianimasikan secara terpisah

Pisahkan secara logis:

HAIR_BACK
HAIR_BACK_LEFT
HAIR_BACK_RIGHT
HAIR_SIDE_LEFT
HAIR_SIDE_RIGHT
HAIR_FRONT
HAIR_BANGS
HAIR_STRANDS
HAIR_TIPS
HAIR_ACCESSORIES

Jangan membuat seluruh rambut sebagai satu objek.

# ======================== 5. WAJAH

Wajah harus bersih dan mudah digunakan untuk Live2D.

Pisahkan:

FACE
EAR_LEFT
EAR_RIGHT
EYEBROW_LEFT
EYEBROW_RIGHT
EYE_LEFT
EYE_RIGHT
IRIS_LEFT
IRIS_RIGHT
PUPIL_LEFT
PUPIL_RIGHT
HIGHLIGHT_LEFT
HIGHLIGHT_RIGHT
UPPER_EYELID_LEFT
UPPER_EYELID_RIGHT
LOWER_EYELID_LEFT
LOWER_EYELID_RIGHT
NOSE
MOUTH_BASE
MOUTH_INSIDE
MOUTH_UPPER
MOUTH_LOWER
TEETH
TONGUE
BLUSH_LEFT
BLUSH_RIGHT

Default mouth harus CLOSED.

# ======================== 6. MATA

Mata harus dirancang untuk:

- blinking
- eye open/close
- eye tracking
- pupil movement
- gaze direction
- smiling eyes
- angry eyes
- surprised eyes

Buat struktur mata yang memungkinkan deformasi Live2D.

Jangan menyatukan iris, pupil, highlight, eyelid, dan eye white menjadi satu layer.

# ======================== 7. MULUT

Mouth harus mendukung:

- closed
- slightly open
- A
- I
- U
- E
- O
- smile
- small smile
- sad
- surprised

Mouth harus dibuat dengan struktur yang memungkinkan lip-sync.

# ======================== 8. TUBUH

Pisahkan bagian tubuh secara jelas:

HEAD
NECK
TORSO
CHEST
WAIST
ARM_LEFT
ARM_RIGHT
HAND_LEFT
HAND_RIGHT
LEG_LEFT
LEG_RIGHT

Bagian tubuh yang tertutup pakaian tetap harus memiliki hidden/backfill art jika diperlukan untuk deformasi.

Jangan membuat celah transparan ketika kepala atau tangan bergerak.

# ======================== 9. OUTFIT

Outfit harus fantasy ocean princess / elegant deep-sea theme.

Gunakan:

- white
- icy blue
- light blue
- pearl
- silver
- cyan
- sedikit lavender
- sedikit soft gold

Buat outfit kompleks tetapi tetap clean.

Pisahkan:

INNER_CLOTHING
DRESS
SKIRT_FRONT
SKIRT_BACK
SLEEVE_LEFT
SLEEVE_RIGHT
COLLAR
RIBBON
WAIST_RIBBON
CAPE
TRANSPARENT_FABRIC
FABRIC_DETAILS
ORNAMENTS

Semua kain yang mungkin bergerak harus memiliki layer terpisah.

# ======================== 10. AKSESORI

Karakter harus memiliki banyak aksesori.

Namun setiap aksesori harus dibuat sebagai objek terpisah.

Contoh:

TIARA
HAIR_ORNAMENT
WHALE_TAIL_ORNAMENT
FLOWER_ORNAMENT
PEARL_CHAIN
EARRING_LEFT
EARRING_RIGHT
NECKLACE
GEMSTONE
RIBBON_LEFT
RIBBON_RIGHT
WAIST_CHAIN
BRACELET_LEFT
BRACELET_RIGHT
LEG_ACCESSORY_LEFT
LEG_ACCESSORY_RIGHT
SHOE_LEFT
SHOE_RIGHT

Aksesori yang menggantung harus memiliki struktur layer sendiri sehingga dapat diberi physics.

# ======================== 11. WHALE MOTIF

Buat whale motif menjadi identitas visual utama tetapi jangan literal.

Gunakan secara halus:

- whale tail
- whale fin
- whale silhouette
- ocean waves
- bubbles
- pearls
- deep ocean crystals
- water droplets
- moonlit ocean motif

Tambahkan satu **signature whale-tail accessory** yang mudah dikenali sebagai ciri khas karakter.

# ======================== 12. LAYERING REQUIREMENT

Ini sangat penting.

Jangan membuat satu gambar flattened.

Semua bagian yang mungkin bergerak harus dipisahkan menjadi layer.

Gunakan struktur layer yang rapi seperti:

VTUBER_MODEL
│
├── BODY
│
├── HEAD
│
├── FACE
│
├── EYES
│
├── EYEBROWS
│
├── NOSE
│
├── MOUTH
│
├── HAIR_BACK
│
├── HAIR_SIDE
│
├── HAIR_FRONT
│
├── HAIR_ACCESSORIES
│
├── CLOTHING
│
├── ACCESSORIES
│
├── ARMS
│
├── HANDS
│
├── LEGS
│
└── EFFECTS

Gunakan nama layer yang konsisten dan mudah dipahami.

# ======================== 13. HIDDEN ART / BACKFILL

Saat sebuah bagian bergerak, area yang sebelumnya tertutup harus memiliki artwork tambahan di belakangnya.

Contoh:

Jika rambut bergerak ke samping, wajah di belakang rambut harus tetap tersedia.

Jika kepala bergerak, leher dan bagian tubuh belakang harus memiliki artwork yang diperlukan.

Jika tangan bergerak, bagian pakaian yang tertutup tangan harus memiliki backfill.

Jangan meninggalkan lubang transparan ketika objek bergerak.

# ======================== 14. LIVE2D RIGGING

Setelah artwork selesai, buat rigging yang sesuai untuk Live2D Cubism.

Minimal parameter:

PARAM_ANGLE_X
PARAM_ANGLE_Y
PARAM_ANGLE_Z

PARAM_EYE_BALL_X
PARAM_EYE_BALL_Y

PARAM_EYE_L_OPEN
PARAM_EYE_R_OPEN

PARAM_BROW_L
PARAM_BROW_R

PARAM_MOUTH_OPEN_Y
PARAM_MOUTH_FORM

PARAM_BODY_ANGLE_X
PARAM_BODY_ANGLE_Y
PARAM_BODY_ANGLE_Z

PARAM_BREATH

PARAM_HAIR_SWAY

PARAM_CLOTH_SWAY

PARAM_ACCESSORY_SWAY

Tambahkan physics untuk:

- rambut panjang
- rambut samping
- pita
- rok
- kain transparan
- rantai
- anting
- aksesori kecil
- ornamen paus

Physics harus lembut dan natural.

Jangan membuat rambut bergerak berlebihan.

# ======================== 15. EXPRESSIONS

Buat expression terpisah:

DEFAULT
SMILE
HAPPY
SAD
ANGRY
SURPRISED
SHY
BLINK
WINK

Tetapi:

**DEFAULT = NEUTRAL CALM**

Jangan menjadikan smile sebagai ekspresi default.

# ======================== 16. VTUBER QUALITY

Karakter harus terlihat seperti model VTuber profesional, bukan ilustrasi anime biasa.

Prioritas:

1. Clean silhouette
2. Layer separation
3. Rigging-friendly design
4. Natural deformation
5. Consistent proportions
6. Detailed accessories
7. High-quality rendering
8. Natural physics
9. Clear facial tracking
10. Stable mouth tracking

# ======================== 17. OUTPUT YANG SAYA INGINKAN

Saya ingin output project yang terstruktur.

Target file:

1. Character artwork source
2. Layered PSD/compatible layered artwork
3. Texture assets jika diperlukan
4. Live2D Cubism project
5. Rigged model
6. Physics configuration
7. Expressions
8. Motion parameters
9. Model configuration
10. Preview/render untuk pengecekan

Jika lingkunganmu mampu membuat file native Live2D Cubism, buat file tersebut.

Jika lingkunganmu TIDAK dapat menghasilkan file native Live2D seperti .cmo3/.model3.json secara langsung, JANGAN berpura-pura bahwa model sudah selesai.

Dalam kondisi tersebut, buat sebanyak mungkin aset produksi yang benar-benar dapat digunakan, terutama layered artwork yang terstruktur, dan berikan instruksi teknis paling singkat untuk menyelesaikan tahap yang tidak dapat dilakukan secara otomatis.

# ======================== 18. QUALITY CONTROL

Sebelum menyatakan selesai, lakukan pengecekan:

- Apakah wajah tetap natural?
- Apakah default expression neutral?
- Apakah mulut tertutup?
- Apakah karakter full body?
- Apakah rambut benar-benar panjang?
- Apakah identitas blue whale terlihat?
- Apakah warna dominan light blue + white?
- Apakah aksesori cukup banyak?
- Apakah aksesori tidak berantakan?
- Apakah layer terpisah?
- Apakah bagian tersembunyi memiliki backfill?
- Apakah mata siap tracking?
- Apakah mulut siap lip-sync?
- Apakah rambut siap physics?
- Apakah pakaian siap physics?
- Apakah karakter cocok untuk Live2D?

Jika ada bagian yang tidak memenuhi standar, perbaiki sebelum melanjutkan.

# ======================== 19. ATURAN PENTING

Jangan mengubah identitas dasar karakter tanpa alasan.

Jangan membuat ekspresi default tersenyum.

Jangan membuat karakter terlihat seperti kostum paus.

Jangan mengurangi jumlah aksesori hanya karena desain kompleks.

Jangan membuat rambut pendek.

Jangan membuat warna dominan gelap.

Jangan menggunakan pose dramatis.

Jangan flatten semua artwork menjadi satu gambar jika targetnya adalah Live2D.

Jangan mengatakan "siap dipasang" apabila file native yang diperlukan belum benar-benar tersedia.

Kerjakan proyek secara bertahap dan prioritaskan kualitas produksi daripada sekadar menghasilkan gambar yang terlihat bagus.

Mulai dari desain final karakter berdasarkan reference image yang saya berikan, kemudian lanjutkan ke struktur layer dan persiapan Live2D.