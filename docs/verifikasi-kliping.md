# Verifikasi Kliping Soeharto — Progres

Dokumen ini mencatat progres verifikasi 1.112 artikel kliping
(`content/perpustakaan-soeharto/`). Arti status:

- `unreviewed` — belum diperiksa sama sekali.
- `source_checked` — teks kliping cocok dengan artikel asli di
  soehartolibrary.id (dibuktikan mesin, lihat Fase 0). Klaim di dalam
  artikel BELUM dicek ke sumber kedua.
- `cross_checked` — klaim di dalam artikel sudah dicek ke sumber kedua
  (butuh pembacaan manusia/LLM, lihat Fase 1).
- `disputed` / `needs_review` — ada yang janggal, perlu tinjauan.

## Fase 0 — Cek otomatis terhadap sumber (SELESAI, 7 Nov 2026)

- Skrip: `scripts/verify_kliping_sources.py` (cek per artikel, resumable).
- Metode: teks asli diambil dari WordPress REST API soehartolibrary.id
  (`/wp-json/wp/v2/posts?slug=...`; slug numerik dicoba sebagai ID);
  bila API kosong, fallback unduh halaman sumber langsung. Perbandingan:
  containment kata (berapa % kata kliping yang ada di teks sumber).
- Ambang: match ≥ 0,85; review 0,70–0,85; mismatch < 0,70.
- Hasil: **1.112/1.112 match**, 0 review, 0 mismatch, 0 not_found,
  0 dead_link, 0 error. Metode: api 1.107, api-id 5.
- Distribusi containment: minimum 0,883; persentil-1 0,901; median 0,978.
  Skor terendah (0,88–0,90) semuanya artikel pendek (74–83 kata) yang
  klipingnya ~9 kata LEBIH PANJANG dari sumber — kata-kata judul/heading
  yang dihitung sebagai isi kliping, bukan perbedaan isi. Bukan mismatch.
- Laporan mentah: `/home/ubuntu/kliping-verify.jsonl` (di server, di luar repo).
- Diterapkan: semua 1.112 kliping `status` + `verification_status` =
  `source_checked` (commit menyusul di bawah).

## Fase 1 — Baca manusia/LLM per batch

Per batch: baca isi artikel, cek klaim ke sumber kedua
(`cross_checked` atau `disputed`), dan ekstrak relasi `menyebut` ke
entitas wiki yang disebut di isi artikel (maks ~5 per artikel; hanya
entitas yang sudah punya halaman). Satu kali baca menghasilkan dua hal.

### Pilot 1968 (SELESAI, 7 Nov 2026, commit `14af0df6`, live)

- **Pembaca: rizky sendiri, 82 artikel dibaca penuh** — atas perintah
  user ("silakan, anda saja yang membaca"), bukan Hermes. Protokol:
  baca penuh + cek konsistensi internal (hari vs tanggal, judul vs H1,
  tanggal filename/frontmatter/isi) + spot-check web untuk klaim yang
  bisa dicek. Definisi ini dinyatakan apa adanya: `cross_checked` di
  sini berarti sudah dibaca penuh dan dicek konsistensinya, BUKAN
  verifikasi silang tiap klaim ke sumber kedua yang independen.
- **Hasil: 84 `cross_checked`, 8 `needs_review`, 0 `disputed`.**
  (84 = 82 pilot + 2 dari 10 perbaikan tanggal-perpustakaan di bawah.)
- **8 `needs_review`:** 7 selisih nama hari vs tanggal (00307, 00309,
  00735, 00897, 00898, 00899 — kemungkinan salah ketik hari di buku
  sumber; 00309 juga mengutip Instruksi 37/U/IN/6/**1976** padahal yang
  benar **1967**), 1 Pepera disebut "tahun ini" di 1968 (00913 —
  Pepera dilaksanakan 1969), 1 "HUT RRI ke-22" (01137 — RRI berdiri
  11 Sep 1945, jadi 1968 = ke-23).
- **19 perbaikan date/title:** 2 tanggal salah tahun (00523 → 1968-05-03,
  00659 → 1968-06-27); 2 pindah batch 1969 (01165 → 1969-09-03, 01166 →
  1969-09-06); 5 koreksi tanggal (00639 judul saja, 00734 → 1968-07-03,
  00914 → 1968-08-20, 01680 → 1968-10-01, 01681 → 1968-10-05); 10
  tanggal frontmatter = tanggal publikasi perpustakaan 2013–2017,
  bukan tanggal peristiwa (00310 → 1968-04-09; 00282, 00317, 00318,
  00319, 00327, 00535, 00939, 00940, 00455 → tanggal peristiwa 1969).
  Satu anomali dicatat tanpa mengubah isi: 00940 kata hari "SABTU"
  salah (17 Agu 1969 = Minggu); 00939 tanggal pidato 16 Agu 1969
  (H1 lama "17-08-1969" merujuk konteks HUT).
- **15 relasi `menyebut` baru** (hanya bila frasa konsep disebut
  eksplisit; label generik seperti "Stabilitas" dan istilah anakronistis
  seperti KKN untuk 1968 ditolak). Total relasi MCP: 1.228 → 1.243.
- **Indeks diperbarui:** seksi 1968 = **81** kliping, seksi 1969 =
  **132** kliping; semua seksi lain hitungannya cocok.
- **Spot-check terkonfirmasi OK:** Inpres 12/1968, Tim Ekonomi Keppres
  195/1968 (8 orang), kenaikan BBM 25 Apr 1968, eksekusi Usman–Harun
  17 Okt 1968, UU 6/1968 PMDN disahkan 3 Jul 1968.
- Keputusan baca tersimpan di `workspace/goals/wiki-soeharto/hidden_files/pilot1968_decisions.py`
  (di VM, bukan repo); skrip terapan `apply_pilot1968.py` di folder yang sama.

### Batch 1969 (SELESAI, 7 Nov 2026, commit `8a14a546`, live)

- **Pembaca: 5 subagen baca paralel** (23–25 artikel tiap chunk), masing-masing
  baca penuh dgn protokol yg sama seperti pilot; rizky menggabungkan
  putusan, memverifikasi langsung 4 klaim fix ke file aslinya, dan
  memeriksa konsistensi hitungan. 9 artikel yg sudah diputuskan di pilot
  (tanggal-perpustakaan 1969) dibawa putusannya; 01165/01166 disalin
  verbatim dari pilot.
- **Hasil: 132 artikel; 129 `cross_checked`, 3 `needs_review`,
  0 `disputed`.** Kumulatif Fase 1: **202 `cross_checked`,
  11 `needs_review`.**
- **3 `needs_review` baru:** 00015 (isi "SENIN, 8 JANUARI 1969" padahal
  8 Jan 1969 = Rabu), 00936 (isi "SABTU, 11 AGUSTUS 1969" padahal 11 Agu
  1969 = Senin), 01710 (isi mengutip "Keppres No. 132 tahun 1969" —
  Keppres 132 itu 24 Agu 1967; yg bertanggal 1969 adalah Keppres 79/1969).
- **15 perbaikan date/title:** 00312 pindah ke 1968 (isi + description
  "KAMIS, 11 APRIL 1968", footnote hal. 10 buku Jejak Langkah; 11 Apr
  1968 memang Kamis); 00756 → 24 Jul 1969 (isi "KAMIS, 24 Juli 1969",
  konsisten dgn kunjungan Nixon 27 Jul); 00682 + 00950 perbaikan judul
  (spasi ganda dari judul terlipat); 11 dibawa dari pilot (9
  tanggal-perpustakaan + 01165/01166).
- **20 relasi `menyebut` baru** (total 35). Kriteria ketat dipertahankan:
  sebagian besar kandidat mesin ditolak — "stabilisasi ekonomi" sbg nama
  dewan ≠ "Stabilitas Nasional"; "ketahanan nasional" bukan entri
  glosarium (hanya 4 konsep); Pelita belum ada halaman entitasnya.
- **Indeks diperbarui:** seksi 1968 = **82** kliping, seksi 1969 =
  **131** kliping; semua seksi lain hitungannya cocok.
- **Spot-check terkonfirmasi:** Keppres 19/1969 (Kopkamtib, JDIH BKPM),
  Keppres 22/1969 (haji, JDIH BPK), kunjungan Nixon 27–28 Jul 1969
  (history.state.gov; kunjungan pertama Presiden AS ke Indonesia),
  kunjungan Indira Gandhi 28 Jun–3 Jul 1969, UU 5/1969 (5 Jul 1969),
  Pepera 14 Jul–2 Agu 1969, ACC 7 negara, Hari Koperasi ke-22,
  pembakaran Al-Aqsa 21 Agu 1969, kunjungan Irian Barat Sep 1969
  (UU 12/1969).
- Keputusan baca tersimpan di `workspace/goals/wiki-soeharto/hidden_files/batch1969_decisions.py`
  (di VM, bukan repo); skrip terapan `apply_batch1969.py` di folder yang sama.

### Batch 1970 (SELESAI, 7 Nov 2026, commit `5de03265`, live)

- **Pembaca: 5 subagen baca paralel** (27 artikel tiap chunk), baca penuh
  dgn protokol pilot/batch 1969; rizky menggabungkan putusan,
  memverifikasi langsung 3 fix + jangkar 00761/00767 ke file aslinya.
- **Hasil: 135 artikel; 130 `cross_checked`, 5 `needs_review`,
  0 `disputed`.** Kumulatif Fase 1: **332 `cross_checked`,
  16 `needs_review`.**
- **5 `needs_review` baru:** 00036 (isi "JUM'AT, 1 JANUARI 1970"
  padahal 1 Jan 1970 = Kamis), 00078 (isi "KAMIS, 4 PEBRUARI" padahal
  4 Feb 1970 = Rabu), 00079 (isi "SABTU, 6 PEBRUARI" padahal 6 Feb
  1970 = Jumat, DITAMBAH isi menyebut Presiden "bersembahyang Ied" di
  Masjid Istiqlal padahal Idul Adha 1389H jatuh Senin 16 Feb 1970 —
  kemungkinan artikel salah tanggal atau salah kutip peristiwa),
  00553 (isi "SABTU, 12 MEI 1970" padahal 12 Mei 1970 = Selasa),
  00971 (judul + isi "HUT Kemerdekaan RI ke-23" padahal 17 Agu 1970
  adalah HUT ke-25 — terkonfirmasi arsip peringatan 25 tahun).
- **3 perbaikan date/title:** 00806 pindah ke 1973 (isi: "Keppres No.
  27/1973" + "tahun anggaran 1973/1974"; JDIH BPK: Keppres 27/1973
  ditetapkan 7 Jul 1973, dan 7 Jul 1973 memang Sabtu — cocok dgn
  "SABTU, 7 Juli" di isi); 00162 + 00763 perbaikan judul (spasi
  ganda dari judul terlipat, cocok H1).
- **20 relasi `menyebut` baru** (total 55): 13 ekonomi-orde-baru,
  3 orde-baru-1966-1998, 2 glosarium (Stabilitas Nasional di 00043,
  Dwifungsi ABRI di 01760), 1 kopkamtib (00074), 1 pemilu-orde-baru
  (00560, SK 43/1970 peserta Pemilu).
- **KKN ditolak di 12+ artikel:** halaman `konsep/kkn.md` dibaca
  langsung (chunk 4) — KKN = istilah politik Reformasi 1998 (TAP MPR
  XI/1998, UU 28/1999) ttg jaringan patronase/monopoli/kroni 1990-an,
  anakronistis utk artikel 1970 soal Komisi Empat / TPK / open house
  pelaporan korupsi (korupsi sbg delik biasa + pembenahan administratif).
- **2 selisih hari diputuskan `cross_checked` dgn jangkar kronologi
  antar-artikel** (bukan `needs_review`): 00761 (isi "RABU 4 Jul" —
  tanggal 4 Jul didukung 00762: Presiden di Bandung pagi Minggu 5 Jul
  setelah penutupan kongres PGRI "tadi malam" = Sabtu 4 Jul) dan
  00767 (isi "SABTU 20 Jul" — tanggal 20 Jul didukung laporan
  mahasiswa Sabtu 18 Jul di 00766 + 00768: Presiden tiba di Yogyakarta
  "kemarin sore" = Senin 20 Jul). Pada keduanya yg salah kata hari di
  buku sumber, bukan tanggalnya — tidak ada fix.
- **Indeks diperbarui:** seksi 1970 = **134**, seksi 1973 = **80**,
  Tanpa tanggal = **176**. Perbaikan sampingan: 01036 (1973-08-17,
  keturunan Cina) selama ini salah tempat di "Tanpa tanggal" — pindah
  ke 1973. 2 tautan di 1973 (00365, 00818) punya frontmatter date tahun
  publikasi (2017/2013) — bagian dari masalah 170 tanggal publikasi,
  tetap di 1973 berdasarkan tahun di nama file; header 1973 dikoreksi
  78→80 agar cocok dgn jumlah tautan aktual (skrip apply menghitung
  dari frontmatter date, bukan nama file).
- **Spot-check terkonfirmasi:** Keppres 12/1970 (Komisi Empat, ketua
  Wilopo, penasihat Hatta; dibubarkan Keppres 50/1970 16 Jul 1970),
  Perpu 24/1960 → UU 3/1971, Idul Adha 1389H = Senin 16 Feb 1970,
  kunjungan Malaysia/Thailand Mar 1970, kurs tunggal Apr 1970
  (Rp378/US$, NBER), Keppres 24/1970 + UU 5/1970 (APBN 1970/1971),
  kunjungan AS 24 Mei–4 Jun 1970 (American Presidency Project, Nixon
  Library), Raja Faisal 10–11 Jun 1970, wafat Bung Karno 21 Jun 1970
  pukul 07.00, Wanhankamnas Keppres 51/1970 (1 Agu 1970; peresmian +
  pelantikan Sekjen 10 Okt 1970), KTT Non-Blok Lusaka 8–10 Sep 1970
  (54 anggota), kerusuhan Wassenaar 31 Agu 1970 (33 pemuda Maluku,
  polisi Moolenaar tewas).
- Keputusan baca tersimpan di `workspace/goals/wiki-soeharto/hidden_files/batch1970_decisions.py`
  (di VM, bukan repo); skrip terapan `apply_batch1970.py` + skrip gabung
  `merge_batch1970.py` di folder yang sama (gabung menormalisasi koma
  tiap entri — pelajaran dari merge 1969 yg gagal karena koma hilang).

### Batch 1971 (SELESAI, 7 Nov 2026, commit `15d0003b`, live)

- **Pembaca: 5 subagen baca paralel** (22/22/22/21/21 artikel tiap
  chunk), baca penuh dgn protokol pilot/batch 1970; rizky menggabungkan
  putusan, memverifikasi langsung 12 fix + 00711 ke file aslinya.
- **Hasil: 108 artikel; 107 `cross_checked`, 1 `needs_review`,
  0 `disputed`.** Kumulatif Fase 1: **439 `cross_checked`,
  17 `needs_review`.**
- **1 `needs_review` baru:** 00711 (isi "SABTU, 14 Juni 1971" padahal
  14 Jun 1971 = Senin; tanggal 14 Jun konsisten di filename/frontmatter/
  H1/isi, kemungkinan salah ketik hari di buku sumber; konteks kunjungan
  Dirjen UNESCO René Maheu Juni 1971 terkonfirmasi, tapi penyerahan
  medali emas tanggal 14 Juni tidak terkonfirmasi dari sumber luar —
  medali UNESCO ke Soeharto yg terdokumentasi justru Avicenna Medal
  Juni 1993).
- **12 perbaikan date/title:** 00116 pindah ke 1972 — seluruh lawatan
  Australia–Selandia Baru–Filipina terjadi Feb 1972, bukan 1971
  (isi "MINGGU 06 PEBRUARI", 6 Feb 1972 = Minggu; disambut PM William
  McMahon yg baru jadi PM 10 Mar 1971; terkonfirmasi PM Transcripts
  Australia, Getty, Workers Press, Joint Communiqué Filipina);
  01370 + 01371 pindah ke 1972 (isi "8/9 SEPTEMBER 1972", judul/H1/
  alias sudah 1972; footnote hal. 469); 01888 pindah ke 1973 (isi
  "SENIN, 1 OKTOBER 1973"; footnote volume buku 1973–1978 hal. 57 —
  BUKAN duplikat 01805, upacara 1 Okt 1971); 00174 (date publikasi
  2017-08-29 → 1971-03-01), 00567 (2014-03-22 → 1971-05-03), 00582
  (2017-08-25 → 1971-05-07), 01325 (2017-08-22 → 1971-09-01) — keempat
  tanggal peristiwa dibuktikan isi (hari cocok `date -d`); 00982
  1971-08-08 → 1971-08-09 (judul/H1 sudah 1971-08-09); 01336
  1971-07-23 → 1971-09-23 (isi "KAMIS, 23 SEPTEMBER 1971", jangkar
  footnote hal. 368 = halaman yg sama dgn artikel 21 Sep 1971);
  00340 + 00989 perbaikan judul (spasi ganda, cocok H1).
- **34 relasi `menyebut` baru** (total 89): 20 ekonomi-orde-baru,
  7 pemilu-orde-baru, 4 orde-baru-1966-1998, 3 glosarium (Dwifungsi
  ABRI di 00113 + 01814, Demokrasi Pancasila di 01329). 2 selisih hari
  diputuskan `cross_checked` dgn jangkar: 00113 (isi "KAMIS 22 Feb"
  padahal 22 Feb 1971 = Senin — halaman arsip soehartolibrary.id utk
  artikel yg sama menulis "SENIN, 22 FEBRUARI 1971", tanggal benar)
  dan 00116 (terselesaikan lewat fix tahun, lihat atas).
- **Indeks diperbarui:** seksi 1971 = **104**, seksi 1972 = **85**,
  seksi 1973 = **81**. 2 tautan di 1973 (00365, 00818) masih punya
  frontmatter date tahun publikasi (2017/2013) — skrip apply menghitung
  dari frontmatter date, bukan nama file, jadi header 1973 dikoreksi
  79→81 agar cocok dgn jumlah tautan aktual (seperti batch 1970).
- **Spot-check terkonfirmasi:** Pemilu 3 Jul 1971 (Golkar 62,80% /
  236 kursi, hasil resmi 7 Agu 1971 — Wikipedia, Library of Congress);
  APBN 1971/1972 Rp585.210.385.500 berimbang (UU 5/1971, DPR);
  devaluasi rupiah Rp378→Rp415 pada 23 Agu 1971 (Kemenkeu Media
  Keuangan; pemicu Nixon Shock 15 Agu 1971); reshuffle kabinet
  9 Sep 1971 (Keppres 64/1971; dilantik 11 Sep); kunjungan Ratu
  Juliana 26 Agu–5 Sep 1971 (pertama Kepala Negara Belanda);
  penggunaan kembali nama TNI 5 Okt 1971; Keppres 74/1971 Batam
  (26 Okt 1971, cikal bakal Otorita Batam); IGGI 1971 (Rotterdam
  15–16 Des 1970, proyeksi US$640 juta); krisis mata uang Eropa
  Mei 1971 (Bundesbank berhenti intervensi 5 Mei, mark mengambang
  10 Mei).
- Keputusan baca tersimpan di `workspace/goals/wiki-soeharto/hidden_files/batch1971_decisions.py`
  (di VM, bukan repo); skrip terapan `apply_batch1971.py` + skrip gabung
  `merge_batch1971.py` di folder yang sama. Pelajaran apply: assert
  sinkron H1 harus tahan fix judul-saja (tanpa kunci `date`) — sudah
  diperbaiki di skrip ini.

### Batch 1972 (SELESAI, 7 Nov 2026, commit `3c23363f`, live)

- **Pembaca: 5 subagen baca paralel** (18/18/17/17/16 artikel tiap
  chunk), baca penuh dgn protokol pilot/batch 1971; rizky menggabungkan
  putusan (tanpa fix, jadi tanpa verifikasi file tambahan).
- **Hasil: 86 artikel; 86 `cross_checked`, 0 `needs_review`,
  0 `disputed`.** Kumulatif Fase 1: **525 `cross_checked`,
  17 `needs_review`.**
- **Tanpa perbaikan date/title.** 1 selisih hari terselesaikan dgn
  jangkar: 00727 (isi "SABTU, 05 Juni 1972" padahal 5 Jun 1972 =
  Senin — hmsoeharto.id menulis entri yg sama "SENIN, 5 JUNI 1972";
  Keppres 43/1972 ttg pengesahan itu ditetapkan 30 Mei 1972).
  00733 (ekstra): nama file + entity_id berawalan "1972" padahal
  peristiwa Hari Bhayangkara 1 Jul 1968 — FM date 1968-07-01 SUDAH
  benar (isi "SENIN, 01 Juli 1968", 1 Jul 1968 memang Senin) dan
  tautannya SUDAH di seksi 1968; tidak ada fix, tidak ada pemindahan
  tautan. 00116 + 01370 + 01371 dibaca ulang (sudah cross_checked di
  batch 1971) dan dikonfirmasi.
- **9 relasi `menyebut` baru** (total 98): 8 ekonomi-orde-baru
  (00187 SK 9/1972 cabut sumbangan wajib izin usaha daerah; 00195
  prinsip bantuan LN IGGI; 00200 + 00201 arah/klarifikasi kebijakan
  pelepasan ~50% saham perusahaan non-pribumi; 00202 pengaturan
  PMA/PMDN pribumi-nonpribumi; 00360 komitmen IGGI US$723,4 juta;
  00596 pinjaman Jepang US$200 juta + pinjaman lunak; 00600
  kesepakatan minyak 58 juta kiloliter/10 tahun + pinjaman ¥62
  milyar), 1 glosarium (Stabilitas Nasional di 01853, amanat HUT
  ABRI ke-27).
- **Indeks tidak berubah:** seksi 1972 = **85**; semua seksi cocok
  header vs aktual, 0 tautan salah seksi.
- **Spot-check terkonfirmasi:** pembajakan pesawat MNA 5 Apr 1972
  (MZ-171, pembajakan pertama di Indonesia); kunjungan Jepang 9–13
  Mei 1972 (PM Eisaku Sato, Kaisar Hirohito 12 Mei); IGGI 1972
  (sidang pledging 25–26 Apr, komitmen ~US$724 juta; pinjaman Jepang
  US$200 juta); kunjungan Nixon ke RRC 21–28 Feb 1972 (Shanghai
  Communiqué 28 Feb); Bintang RI Kelas I ke Hatta 15 Agu 1972;
  HUT RI ke-27 (ordinal benar); Museum Satria Mandala diresmikan
  5 Okt 1972; PPP dideklarasikan 5 Jan 1973 (artikel Sep 1972 masih
  menyebut KPP — nama file "ppp" anakronistis, tidak diganti);
  pelantikan anggota MPR 1 Okt 1972; Idul Fitri 1 Syawal 1392H =
  7 Nov 1972; Menlu AS William P. Rogers (1969–1973) + Menlu Inggris
  Alec Douglas-Home; Sicco Mansholt Presiden Komisi Eropa
  22 Mar 1972–5 Jan 1973.
- Keputusan baca tersimpan di `workspace/goals/wiki-soeharto/hidden_files/batch1972_decisions.py`
  (di VM, bukan repo); skrip terapan `apply_batch1972.py` + skrip gabung
  `merge_batch1972.py` di folder yang sama.

### Batch berikutnya (BELUM MULAI)

- Urutan batch: 1973 (81), 1974 (82),
  1975 (88), 1976 (75), 1977 (31), 1978 (17), 1979 (15), 1949–1967 (7),
  1995–1998 (4), tanpa tanggal (176, terakhir).
- Yang ikut dikerjakan di batch baca: 2 tanggal invalid
  (1973-18-22, 1975-19-17) dan **184 judul frontmatter terpotong**
  (hitung ulang 7 Nov 2026; angka lama 81 sudah tidak berlaku).
- Temuan pilot untuk batch berikutnya: **170 kliping ber-date tahun
  2013–2017** (tanggal publikasi perpustakaan, bukan peristiwa —
  perlu audit tanggal repo-wide); baris metadata WP bocor ke isi
  artikel Sep–Okt ("1 September 2013... Views Share on"); file 00733
  nama/entity_id berawalan "1972" padahal peristiwa 1968-07-01 (nama
  file tidak diganti — URL).

## Catatan

- `source_checked` TIDAK berarti klaim sejarahnya benar — hanya berarti
  dokumennya sesuai dengan sumber arsipnya. Jangan menaikkan ke
  `cross_checked` tanpa pembacaan.
- Relasi spesifik per kliping TIDAK dibuat dari judul — hanya dari isi
  yang dibaca, dengan predikat `menyebut`.
- Judul frontmatter bisa terlipat (plain scalar YAML multi-baris).
  Skrip yang mengedit judul dengan regex WAJIB mengganti baris judul
  beserta baris lanjutan berindentasi, atau YAML-nya rusak (terjadi
  pada 00734 saat pilot; diperbaiki sebelum commit).
