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

### Batch 1973 (SELESAI, 7 Nov 2026, commit `2df83ac8`, live)

- **Pembaca: 5 subagen baca paralel** (17/17/16/16/15 artikel tiap
  chunk), baca penuh dgn protokol pilot/batch 1971; rizky menggabungkan
  putusan + memverifikasi langsung 6 fix ke file aslinya.
- **Hasil: 81 artikel; 81 `cross_checked`, 0 `needs_review`,
  0 `disputed`.** Kumulatif Fase 1: **606 `cross_checked`,
  17 `needs_review`.**
- **6 perbaikan date/title:** 00209 (1973-03-20 → 1973-03-14, date
  saja; judul/H1 sudah "1973-03-14 ... Bantu 'Lumbung Paceklik'";
  isi "RABU, 14 Maret 1973"; nama file/entity_id menyebut UU APBN
  padahal isinya bantuan paceklik — TIDAK diganti); 00210
  (1973-03-20 → 1973-03-23, date saja; judul/H1 sudah "1973-03-23
  ... Diambil Sumpah"; pelantikan jabatan kedua 23 Mar 1973,
  Tap MPR IX/MPR/1973); 00365 (tanggal publikasi 2017-08-28 →
  1973-04-07 + title; isi "SABTU, 7 April 1973"; normalisasi
  "1973-04-7"); 00814 (1973-07-09 → 1973-07-19 + title; isi "KAMIS,
  9 Juli 1973" padahal 9 Jul = Senin — yang salah angka tanggal, bukan
  kata hari; hmsoeharto.id + sejarah PT Semen Padang: rehabilitasi
  Indarung I diresmikan 19 Jul 1973); 00818 (tanggal publikasi
  2013-07-28 → 1973-08-18 + title; isi "di Istana Negara pada tanggal
  18-8-1973"; normalisasi "1973-8-18"); 01042 (tanggal invalid
  1973-18-22 → 1973-08-22 + title; transposisi 08→18; isi "RABU,
  22 AGUSTUS 1973"; footnote hal. 44–45 berurutan dgn tetangga).
  Salah satu dari 2 tanggal invalid yang dikenal sejak Fase 0 kini
  terpecahkan dari isi artikel sendiri.
- **2 selisih hari terselesaikan dgn jangkar, tanpa fix:** 00631
  (isi "KAMIS, 21 Mei 1973" padahal 21 Mei = Senin — PP 24/1973 +
  PP 25/1973 ditetapkan/diundangkan 21 Mei 1973; HNSI resmi berdiri
  dan diresmikan 21 Mei 1973; footnote hal. 21 berurutan) dan 01889
  (isi "RABU, 5 OKTOBER 1973" padahal 5 Okt = Jumat — Hari ABRI
  selalu 5 Oktober; amanat Hari ABRI ke-28; footnote hal. 57 sama
  dgn 01888 tgl 1 Okt).
- **14 relasi `menyebut` baru** (total 112), semuanya
  ekonomi-orde-baru: 00211 (UU 3/1973 APBN 1973/1974), 00365
  (kebijakan PMA + Repelita II), 00369 (65% kredit investasi ke
  ekonomi lemah + turunkan suku bunga), 00625 (penyederhanaan
  prosedur PMA/PMDN berlaku 1 Jun 1973 + komitmen IGGI US$876,6
  juta), 00627 (kebijakan stok beras nasional: 10% dari kebutuhan
  14,8 juta ton/tahun), 00637 (pembentukan BKPM, Keppres 70/1973,
  ketua Barli Halim), 00803 (larangan ekspor jagung + ubi-ubian),
  00817 (rice estate dibuka bagi modal swasta/asing), 01033 (kurs
  rupiah tetap Rp415/US$ + lanjutkan impor beras), 01039 (pidato
  kenegaraan 16 Agu: anggaran berimbang, perpajakan, Repelita II),
  01055 (PP 12/1973: tunjangan kerja minimum Rp1.750→Rp2.000,
  penghasilan terendah PNS Rp4.300), 01385 (batas minimum pajak
  kekayaan Rp3,8 jt → Rp14 jt, tarif 5 permil), 01386 (4 masalah
  musim tanam + target produksi 15,36 juta ton), 01399 (komitmen
  investasi Mitsui US$1 milyar jangka panjang). 00636 (instruksi
  tertibkan spekulan beras) + 01889 (Dwifungsi ABRI) ditolak setelah
  penilaian ulang koordinator: instruksi singkat satu paragraf /
  istilah tidak muncul eksplisit.
- **Indeks tidak berubah:** seksi 1973 = **81**; semua seksi cocok
  header vs aktual, 0 tautan salah seksi.
- **Spot-check terkonfirmasi:** pelantikan jabatan kedua 23 Mar 1973
  (Tap MPR IX/MPR/1973); PLTA Riam Kanan diresmikan 30 Apr 1973
  (berganti nama PLTA Ir. P. M. Noor 19 Jan 1980); kunjungan resmi
  pertama Lee Kuan Yew 25 Mei 1973 (tiba 25 Mei, 19 tembakan meriam;
  tabur bunga di makam Usman-Harun, Kalibata, 28 Mei); pemugaran
  Candi Borobudur kedua dimulai 10 Agu 1973, selesai 23 Feb 1983;
  kerusuhan Bandung 5 Agu 1973 (pemicu pemukulan kusir gerobak Asep
  Tosin; kerusakan 1.535 rumah/toko, 129 mobil, 169 motor); HUT RI
  ke-28 (ordinal benar); Perang Yom Kippur mulai 6 Okt 1973 (Resolusi
  DK PBB 338 tgl 22 Okt, perang berakhir 26 Okt — konsisten dgn
  seruan 13 Okt dan syukur gencatan senjata 27 Okt); PDI
  dideklarasikan 10/11 Jan 1973 (ketua umum pertama Mohammad
  Isnaeni); Idul Fitri 1 Syawal 1393H = Sabtu 27 Okt 1973; HNSI
  berdiri 21 Mei 1973; PP 24/1973 + PP 25/1973 ditetapkan 21 Mei 1973.
- **Selisih sumber dicatat, bukan fix:** 00211 — naskah UU 3/1973
  sebenarnya disahkan 14 Mar 1973 dgn total Rp862,4 miliar
  (pembangunan Rp344,1 M), sedangkan artikel mencatat 20 Mar /
  Rp867,4 M (pembangunan Rp349,1 M); isi konsisten internal.
  00637 — buku resmi BKPM menyebut pembentukan 26 Mei 1973
  berdasarkan Keppres 20/1973, berbeda dgn kliping (Keppres
  70/1973, 29 Mei). 01052 — isi menyebut KTT Non-Blok Aljazair
  "5-8 September" padahal aktual 5–9 Sep 1973 (selisih pada
  pernyataan rencana ke depan). 00806 + 01888 dibaca ulang (sudah
  `cross_checked` di batch 1970/1971) dan dikonfirmasi; 01888 BUKAN
  duplikat 01805 (upacara 1 Okt 1971). Nama file 01037 sempat
  tertulis 08-13 di brief, yang benar 08-10 (file di disk +
  `batch1973.json` sudah benar; merge tidak terganggu).
- Keputusan baca tersimpan di `workspace/goals/wiki-soeharto/hidden_files/batch1973_decisions.py`
  (di VM, bukan repo); skrip terapan `apply_batch1973.py` + skrip gabung
  `merge_batch1973.py` di folder yang sama.

### Batch 1974 (SELESAI, 7 Nov 2026, commit `fa3a9045`, live)

- **Pembaca: 5 subagen baca paralel** (17/17/17/16/15 artikel tiap
  chunk), baca penuh dgn protokol pilot; rizky menggabungkan putusan
  + memverifikasi langsung 2 fix ke file aslinya.
- **Hasil: 82 artikel; 82 `cross_checked`, 0 `needs_review`,
  0 `disputed`.** Kumulatif Fase 1: **688 `cross_checked`,
  17 `needs_review`.**
- **2 perbaikan date/title:** 00840 (1974-11-20 → 1974-07-20 +
  title; isi "SABTU, 20 Juli 1974", 20 Jul 1974 memang Sabtu;
  footnote hal. 138, halaman yg sama dgn 00836 tgl 17 Jul dan satu
  halaman sebelum 00841 tgl 22 Jul; PP 29/1974 ttg Perum Perumnas
  ditetapkan 18 Jul 1974) dan 01431 (tanggal publikasi 2017-08-23
  → 1974-09-09 + title; normalisasi "1974-09-9"; isi "SELASA,
  9 SEPTEMBER 1974" padahal 9 Sep 1974 = Senin — kata hari salah,
  dibuktikan 01404 yg menulis "SENIN, 9 SEPTEMBER 1974" +
  `date -d`; footnote 01431 hal. 284 adalah anomali kutipan,
  jauh dari urutan tetangga hal. 158–160).
- **17 relasi `menyebut` baru** (total 129): 14 ekonomi-orde-baru,
  1 kopkamtib, 2 malari-1974. Ekonomi: 00214 (4 keputusan sidang
  Dewan Stabilisasi Ekonomi: Tanjung Priok, impor Pelita II,
  Pusri II+III → 1 juta ton urea), 00221 (UU No. 2/1974 APBN
  1974/1975), 00234 (pembebasan bea masuk bibit hewan unggul +
  KIK/KMKP Rp5,8 milyar), 00384 (lima langkah menekan inflasi:
  stok nasional, pengawasan harga, kelancaran pelabuhan, kredit
  12%→15% di atas Rp100 juta, cadangan wajib 30% atas pinjaman
  LN), 00387 (pembentukan Irjenbang, Keppres 25/1974), 00819
  (instruksi ke BKPM realisasikan industri kimia pencelupan
  Jakarta + semen Cilacap), 00821 (keputusan re-ekspor
  sedan/station wagon), 00832 (pembebasan pajak docking/reparasi
  galangan dalam negeri), 00840 (pembentukan tiga badan pengelola
  perumahan rakyat), 01059 (laporan moneter 1973/1974: inflasi
  47% → 5,6% Apr–Jul 1974, kebijaksanaan 9 April 1974), 01061
  (arah kebijakan industri pupuk: lanjutkan Pusri III, total
  1 juta ton), 01063 (peraturan pembatasan pekerja asing di
  minyak + tekstil, kerangka Keppres), 01424 (sidang Kesra:
  kredit tanpa bunga PNS gol. I Rp3,3 milyar, 6.000 SD Inpres,
  Inpres No. 5/1974 — 10.500 sarana kesehatan + 3.935 tenaga
  kesehatan Rp5.128.342.220), 01907 (laporan BKPM: 759 proyek
  PMA 1968–1974 senilai US$3.796 milyar). Kopkamtib: 00220
  (refungsionalisasi Kopkamtib: fungsi diserahkan ke
  departemen/lembaga). Malari-1974: 00389 (sikap pemerintah:
  peristiwa 15-16 Jan belum selesai + uraian Bakin soal latar
  belakang) dan 00822 (rencana pengadilan subversi pelaku Malari
  dalam 2-3 bulan). Bakin DITOLAK di keduanya (Yoga Sugama hanya
  pelapor/pemegang jabatan). 01063 DITERIMA sedangkan 01423
  (peraturan tenaga asing "akan dikeluarkan" tanpa isi) DITOLAK:
  01063 menguraikan isi kebijakannya (sektor, bentuk Keppres,
  kriteria jabatan), 01423 hanya mengumumkan penerbitan.
  01914 glosarium DITOLAK: "Dwifungsi ABRI" hanya analogi satu
  kalimat untuk RSGS, bukan pembahasan substansial.
- **Indeks tidak berubah:** seksi 1974 = **82**; semua seksi cocok
  header vs aktual, 0 tautan salah seksi.
- **Spot-check terkonfirmasi:** kunjungan Ratu Elizabeth II
  18–22 Mar 1974 (pertama monarki Inggris di Indonesia); Kenneth
  Rush Deputi Menlu AS 1973–1974; Pusri II diresmikan 8 Agu 1974
  (380.000 ton urea + 218.400 ton amonia/tahun); Keppres 25/1974
  Irjenbang 22 Apr 1974; Malari 15-16 Jan 1974 (775 ditangkap;
  Hariman Siregar divonis 6,5 tahun 21 Des 1974; sidang dimulai
  1 Agu 1974, dalam jendela 2-3 bulan yg disebut 3 Jul); SK
  Mendag 25/KP/I/1974 soal impor sedan (22 Jan 1974); Perum
  Perumnas didirikan 18 Jul 1974 (PP 29/1974); inflasi 1973/1974
  47,40% + program stabilisasi 9 April 1974 (Sejarah BI;
  Wikileaks); kunjungan Birma 26–29 Agu + Singapura 29–31 Agu
  1974 (pertama Soeharto ke Singapura); pertemuan Whitlam–
  Soeharto 6 Sep 1974 di Wonosobo (soal Timor Portugis, dokumen
  NAA); kunjungan Shah Iran 1–2 Okt 1974 (pertama kepala negara
  Iran di Indonesia); kunjungan Raja Boudewijn + Ratu Fabiola
  21 Okt–2 Nov 1974 (13 hari); Idul Fitri 1 Syawal 1394H =
  17 Okt 1974; Hari ABRI ke-29 + HUT Golkar ke-10 (ordinal
  benar).
- **Selisih sumber dicatat, bukan fix:** 00222 — Wikipedia
  mencatat masa jabatan Pangkopkamtib Soemitro berakhir 2 Mar
  1974, sedangkan artikel mencatat Keppres pengabulan 15 Mar
  (tanggal Keppres formal per buku sumber). 01907 — angka 759
  proyek / US$3.796 milyar tidak terkonfirmasi dari sumber luar.
  01916 — Halilov disebut "Ketua Presidium Soviet Tertinggi"
  padahal jabatan itu di Azerbaijan (ketua Presidium Uni Soviet
  adalah Podgorny). 00819 (tanpa tanggal di nama file) FM date
  1974-07-01 BENAR (isi "SENIN, 1 JULI 1974"; aritmetika PNS
  57.485 cocok). 01402 tanpa slug di nama file (entity_id hanya
  "1974-09-05") — dicatat, nama file tidak diganti.
- Keputusan baca tersimpan di `workspace/goals/wiki-soeharto/hidden_files/batch1974_decisions.py`
  (di VM, bukan repo); skrip terapan `apply_batch1974.py` + skrip gabung
  `merge_batch1974.py` di folder yang sama. Pelajaran merge: skrip
  gabung mencari pola `"file": {` dgn spasi setelah titik dua — hasil
  chunk 4 ditulis tanpa spasi (`":{`), jadi dinormalisasi dulu
  (`re.sub(r'("[^"]*\.md"):\{', ...)`) sebelum merge.

### Batch 1975 (SELESAI, 7 Nov 2026, commit `522a14c9`)

- **Pembaca: 5 subagen baca paralel** (19/19/18/18/17 artikel tiap
  chunk), baca penuh dgn protokol pilot/batch 1974; rizky menggabungkan
  putusan + memverifikasi langsung 7 fix + 00407 ke file aslinya.
- **Hasil: 91 artikel; 91 `cross_checked`, 0 `needs_review`,
  0 `disputed`.** Kumulatif Fase 1: **779 `cross_checked`,
  17 `needs_review`.**
- **7 perbaikan date/title:** 00248 (1975-02-15 → 1975-03-15 + title;
  isi "SABTU, 15 MARET 1975" di dua tempat; footnote hal. 224–225 di
  antara 00247 12 Mar hal. 224 dan 00249 18 Mar hal. 225; 15 Feb 1975
  juga Sabtu, jadi kata hari tidak membedakan — jangkarnya urutan
  footnote + isi); 00559 (1975-05-22 → 1970-05-22 + title; isi
  "JUM'AT, 22 MEI 1970", 22 Mei 1970 memang Jumat; footnote mengutip
  volume buku 1968–1973 hal. 227; hmsoeharto.id memuat entri yg sama
  persis di bawah "JUMAT, 22 MEI 1970"; pindah seksi 1970); 01091
  (1975-08-26 → 1975-08-30, date saja; judul/H1 sudah "1975-08-30
  ..."; isi "SABTU, 30 AGUSTUS 1975"); 01102 (1975-08-04 → 1976-08-04,
  date saja; judul/H1 sudah "1976-08-04 ..."; isi "RABU, 04 AGUSTUS
  1976"; footnote hal. 383; halaman arsip soehartolibrary.id
  "1976-08-04 ..."); 01103 (1975-08-05 → 1976-08-05 + title; judul
  lama "1976-08-06" juga salah tanggal; isi "KAMIS, 05 AGUSTUS 1976";
  footnote hal. 383–384); 01104 (1975-08-07 → 1976-08-07, date saja;
  judul/H1 sudah "1976-08-07 ..."; isi "SABTU, 07 AGUSTUS 1976";
  footnote hal. 384; halaman arsip soehartolibrary.id "1976-08-07
  ..."); 01448 (tanggal invalid 1975-19-17 → 1975-09-17 + title;
  isi "RABU, 17 SEPTEMBER 1975"; transposisi 09→19, pola sama dgn
  01042 batch 1973 (08→18); Keppres No. 34 Tahun 1975 ttg Penertiban
  Peningkatan Keuangan Pertamina ditetapkan + berlaku 17 Sep 1975;
  footnote hal. 286, halaman yg sama dgn 01449 18 Sep dan setelah
  01447 16 Sep hal. 285). **Kedua tanggal invalid yg dikenal sejak
  Fase 0 kini terpecahkan.**
- **1 selisih hari diputuskan `cross_checked` tanpa fix:** 00407 (isi
  "SABTU, 14 April 1975" padahal 14 Apr 1975 = Senin — tanggal dinilai
  benar, kata hari salah ketik; jangkar footnote hal. 237 tepat di
  antara 00395 12 Apr hal. 236–237 dan 00408 15 Apr hal. 237–238;
  Sabtu terdekat tersingkir: 12 Apr sudah ditempati 00395, 19 Apr akan
  menuntut footnote ~238–239).
- **7 relasi `menyebut` baru** (total 136): 6 ekonomi-orde-baru, 1
  glosarium (Stabilitas Nasional di 00254 — istilah disebut eksplisit
  sbg tema sub-judul "(Pers Yang Bebas dan Bertanggung Jawab Perkokoh
  Stabilitas Nasional)" + paragraf peran pers dlm memperkuatnya).
  Ekonomi: 00408 (laporan moneter berangka + target semen 5.570.000
  ton akhir 1977 + instruksi Krakatau Steel 500.000 ton/tahun),
  00855 (penandatanganan persetujuan proyek Asahan: Jepang US$833
  juta + Indonesia 10%), 00858 (laporan hasil ekonomi kunjungan luar
  negeri berangka: Yugoslavia, Kanada, AS, Jepang), 01090 (instruksi
  tataniaga kopra via BUUD/KUD + persetujuan Laos pakai setengah
  bantuan US$1 juta utk beli beras Muangthai), 01432 (persetujuan
  penanaman modal Masyarakat Eropa utk pabrik makanan ternak kedelai
  dgn syarat transmigrasi + tenaga kerja), 01967 (keputusan moneter:
  kurs rupiah tetap Rp415/US$1). KKN DITOLAK di 00241 (penyelewengan
  subsidi desa memang ada, tapi istilah KKN anakronistis — Reformasi
  1998); bakin DITOLAK di 00240/01081/01086 (pejabat pelapor/peserta
  saja, lembaga tidak dibahas); ekonomi DITOLAK di 00409 (arah
  kebijakan fiskal sbg prinsip umum tanpa keputusan/angka/tenggat).
- **Indeks diperbarui:** seksi 1970 = **135**, seksi 1975 = **87**,
  seksi 1976 = **75**. Selisih indeks 91 vs 88 (prep) TERPECAHKAN:
  3 file (01102–01104) berjudul 1976 dan duduk di seksi 1976 —
  setelah fix FM date ke 1976 mereka tetap di 1976; 00559 pindah ke
  1970, jadi 1975 = 87. 4 tautan di 1976 (00257, 00258, 00260, 00421)
  punya frontmatter date tahun publikasi (2014/2017) — header 1976
  dikoreksi 71→75 agar cocok dgn jumlah tautan aktual (skrip apply
  menghitung dari frontmatter date, bukan nama file; seperti batch
  1970/1971); keempatnya menunggu batch 1976.
- **Spot-check terkonfirmasi:** TMII diresmikan 20 Apr 1975;
  kunjungan tidak resmi ke Australia 3–5 Apr 1975 (Townsville,
  Whitlam); Krakatau Steel tahap I 500.000 ton/tahun (Keppres
  30/1975, 27 Agu 1975; pabrik besi beton + besi profil diresmikan
  27 Jul 1977); kunjungan Kanada 2–4 Jul 1975 + kredit $200 juta;
  pertemuan Camp David dgn Presiden Ford 5 Jul 1975; proyek Asahan
  7 Jul 1975 (master agreement ditandatangani di Tokyo; Inalum
  didirikan 6 Jan 1976); KTT ASEAN pertama 23–24 Feb 1976 di Bali
  (Deklarasi Kesepakatan ASEAN + Traktat Persahabatan dan Kerja
  Sama); kudeta UDT 11 Agu 1975 + serangan balasan Fretilin 20 Agu +
  Gubernur Pires ke Atauro 26 Agu; Keppres 34/1975 Pertamina
  17 Sep 1975; petisi integrasi UDT ditandatangani 7 Sep 1975;
  Idul Fitri 1 Syawal 1395H = Senin 6 Okt 1975; HUT ABRI ke-30
  5 Okt 1975.
- **Selisih sumber dicatat, bukan fix:** angka Asahan berbeda framing
  antar-artikel — 00855 (Jepang US$833 juta), 00858 (US$870 juta,
  30% saham/70% pinjaman), kabel Deplu AS (total US$844,59 juta);
  01103 angka 12.000 KK (perencanaan saat keputusan Agu 1976) vs
  total 12.525 KK terdampak / 10.350 KK ikut transmigrasi; 00249
  pertemuan Daud Beureueh 18 Mar 1975 tidak terkonfirmasi dari
  sumber luar (dicatat, bukan inkonsistensi internal); 00392
  keyakinan Lon Nol pasukan pemerintah bertahan — Phnom Penh jatuh
  ke Khmer Merah 17 Apr 1975, 12 hari sesudah pertemuan ini (dicatat,
  bukan inkonsistensi internal).
- Keputusan baca tersimpan di `workspace/goals/wiki-soeharto/hidden_files/batch1975_decisions.py`
  (di VM, bukan repo); skrip terapan `apply_batch1975.py` + skrip gabung
  `merge_batch1975.py` di folder yang sama. Pelajaran merge: hasil
  chunk 2 & 3 batch 1975 ditulis satu baris tanpa newline (`wc -l`
  = 0) — itu bukan file kosong; dan format `":{` tanpa spasi tetap
  dinormalisasi dulu sebelum merge.

### Batch 1976 (SELESAI, 7 Nov 2026, commit `ae9b33f3`, live)

- **Pembaca: 5 subagen baca paralel** (15 artikel tiap chunk), baca
  penuh dgn protokol pilot/batch 1975; rizky menggabungkan putusan +
  memverifikasi langsung 4 fix + 00265 ke file aslinya.
- **Hasil: 75 artikel; 75 `cross_checked`, 0 `needs_review`,
  0 `disputed`.** Kumulatif Fase 1: **854 `cross_checked`,
  17 `needs_review`.**
- **4 perbaikan date/title — keempatnya tanggal frontmatter =
  tanggal publikasi perpustakaan, tanggal benar dari isi + hari +
  footnote:** 00257 (2014-03-21 → 1976-03-03 + title; isi "RABU,
  3 MARET 1976", 3 Mar 1976 memang Rabu; footnote hal. 343–344;
  pemberhentian Ibnu Sutowo + pengangkatan Piet Haryono, Keppres
  29/M + 30/M/1976; judul "1976-03-3" dinormalisasi ke "1976-03-03");
  00258 (2014-03-22 → 1976-03-04 + title; isi "KAMIS, 4 MARET
  1976"; footnote hal. 344); 00260 (2014-03-22 → 1976-03-08 +
  title; isi "SENIN, 8 MARET 1976"; footnote hal. 344); 00421
  (2017-08-28 → 1976-04-06 + title; isi "SELASA, 6 April 1976";
  footnote hal. 353; Keppres 14/1976 Pedoman Pelaksanaan APBN
  TA 1976/1977; judul "1976-4-6" dinormalisasi ke "1976-04-06").
  **Dengan ini keempat tautan ber-FM-date 2014/2017 di seksi 1976
  sudah terpecahkan** — tidak ada lagi straggler tanggal publikasi
  di seksi 1976; header 1976 = 75 tautan aktual, tanpa koreksi manual.
- **1 selisih hari diputuskan `cross_checked` tanpa fix:** 00265 (isi
  "JUM'AT, 22 MARET 1976" dgn apostrof keriting, padahal 22 Mar 1976
  = Senin — tanggal dinilai benar, kata hari salah ketik; jangkar
  footnote hal. 347–348 tepat di antara 00264 20 Mar hal. 347 dan
  00266 25 Mar hal. 348; 00266 menyebut Inpres "telah ditetapkan
  beberapa hari yang lalu", 22→25 Mar = 3 hari, pas; Jumat terdekat
  tersingkir: 19 Mar ditempati 00263, 26 Mar akan menuntut footnote
  setelah 00266). 01456 hari ditulis "SEUASA" (typo OCR utk SELASA,
  7 Sep 1976 memang Selasa) — tanpa fix. 01123 judul FM berspasi
  ganda ("1976-08-17  Presiden") vs H1 spasi tunggal — dicatat,
  tidak diperbaiki (bukan judul terlipat).
- **13 relasi `menyebut` baru** (total 149: ekonomi 105, kopkamtib 4,
  glosarium 12, pemilu 9): 10 ekonomi-orde-baru — 00265 (Inpres
  berangka: pasar Rp20 M, reboisasi Rp16 M/200.000 ha, SD Rp53,8 M,
  kesehatan Rp20 M, desa Rp19,8 M, kabupaten Rp62,4 M, provinsi
  Rp61,5 M), 00269 (PP 11/1976 ekspor-impor-devisa), 00421 (Keppres
  14/1976: kewajiban perpajakan + larangan 6 pengeluaran APBN),
  00424 (tuntutan ke Caltex/Stanvac US$1 per barel ekspor + tenggat
  besok pagi), 00871 (kredit 100 motor diesel 30–100 PK utk Pelra),
  01453 + 01454 (instruksi hadapi kemarau: padat karya + lumbung
  paceklik + benih utk musim tanam 1 Okt), 01456 (keputusan sidang
  Dewan Stabilisasi Ekonomi: cegah penurunan produksi padi 1976/1977
  — sarana produksi tepat waktu, tanggulangi penunggakan kredit
  Bimas, keringanan pengembalian kredit), 01477 (keputusan harga
  berangka: pupuk Rp80→70/kg; gabah Rp67,50→70/kg desa,
  Rp68,50→71/kg BUUD/KUD; penyaluran Bimas via BUUD/KUD), 01986
  (sidang Dewan Stabilisasi Ekonomi: instruksi dropping beras Bulog,
  program padat karya musim paceklik, persetujuan standarisasi
  komoditi ekspor); 1 kopkamtib — 00264 (Kopkamtib subjek artikel:
  diperintah menindak penyelundup, melaporkan tindakannya, dinilai
  kinerjanya — preseden 00220 batch 1974); 1 glosarium — 00423
  (Demokrasi Pancasila disebut eksplisit + dibahas satu paragraf
  penuh: hak hidup parpol/Golkar di dalamnya); 1 pemilu — 00884
  (Keppres 34/1976, 6 syarat anggota MPR/DPR/DPRD diuraikan lengkap).
  Ekonomi DITOLAK di 00259 (pelengkapan direksi Pertamina =
  personalia), 00266 (arahan umum pelaksanaan Inpres), 00268
  (anjuran umum soal pajak), 00425 (pelantikan + pidato kesulitan
  Pertamina), 00868 (konsep Jabodetabek BELUM diputuskan), 01474
  (instruksi umum memperlancar jalur pangan — substansinya di 01456),
  01481 (hanya "dibicarakan"), 01977 (persetujuan Puspitek satu
  paragraf dlm artikel dua topik), 01982 (peresmian + amanat umum
  PMA), 01985 (pertemuan kehormatan IMF), 01987 (pasar modal hanya
  "sedang disiapkan"); orde-baru DITOLAK di 00432/01116/01123
  ("semenjak Orde Baru"/"sebelum Orde Baru"/"masa awal Orde Baru"
  hanya klausa penanda waktu); glosarium DITOLAK di 00281
  ("stabilitas nasional" satu klausa dlm kalimat daftar manfaat
  wadah konsultasi) dan 01979 ("Dwifungsi ABRI" tidak muncul
  eksplisit — amanat soal kepeloporan ABRI + Semangat 45); bakin +
  kopkamtib DITOLAK di 01474 (Yoga Sugama + Sudomo hanya pejabat
  yg dipanggil); pemilu DITOLAK di 00260 (keputusan bulan Pemilu Mei
  1977 satu paragraf) dan 00426/00429 (amanat/laporan umum soal
  Pemilu mendatang).
- **Indeks diperbarui:** seksi 1976 = **75** (71 ber-FM-date 1976 +
  4 ekstra yg kini ber-FM-date 1976; tanpa perpindahan tahun keluar).
  01102–01104 (pindah tahun dari batch 1975) dibaca ulang di batch
  ini, tanggal 1976 dikonfirmasi, tanpa fix baru — alias FM +
  `sumber.judul` 01103 masih menulis "1976-08-06..." (sisa judul
  lama, dicatat, tidak diperbaiki). 00866 (tanpa tanggal di nama
  file) dikonfirmasi FM date 1976-07-01 benar.
- **Temuan lain:** 01453/01454 DUPLIKAT impor — isi identik
  kata-per-kata (pertemuan Cendana 2 Sep 1976 ttg kemarau); beda
  hanya typo ("menginstruksilqm"/"oieh" di 01454), tag, Views 98 vs
  113, slug/entity_id bersufiks -2; isi TIDAK diubah, nama file
  TIDAK diganti, keduanya tetap cross_checked masing-masing.
  Rangkaian konsisten lintas artikel: pembenahan Pertamina (00257
  pemberhentian 3 Mar → 00259 pelengkapan direksi 6 Mar → 00425
  pelantikan Piet Haryono 15 Apr); Inpres (00265 ditetapkan 22 Mar
  → 00266 pelaksanaan 25 Mar); kerukunan antar umat beragama (00260
  Badan Konsultasi 8 Mar → 00281 wadah konsultasi 12 Mar);
  transmigrasi Wonogiri (01103 keputusan 12.000 KK Agu 1976 →
  01986 rencana pemberangkatan 500 KK ke Sitiung 26 Okt); Sawito
  (01482 dokumen Sawito 29 Sep → 01979 "Gerakan Sawito" 5 Okt);
  kebijakan pangan/kekeringan (01453/01454 instruksi 2 Sep → 01456
  keputusan sidang 7 Sep → 01474 tindak lanjut 8 Sep). Anomali
  urutan footnote dicatat tanpa fix: 00263 (19 Mar) hal. 349 vs
  00264 (20 Mar) hal. 347 — halaman buku tidak sepenuhnya
  kronologis di situ. Selisih sumber dicatat, bukan fix: 01480
  nomor surat edaran "B-3/ Pres/9/1976" vs kesaksian Sudharmono
  "B-33/Pres/9/76"; halaman pidato soehartolibrary.id memakai
  slug/tanggal 19 April 1976 utk pelantikan Piet Haryono, sedangkan
  kliping + hmsoeharto.id menulis 15 April 1976.
- **Spot-check terkonfirmasi:** pemberhentian Ibnu Sutowo 3 Mar 1976
  (Keppres 29/M + 30/M; kabel Deplu AS 1976JAKART03020; Wikipedia);
  KTT ASEAN pertama 23–24 Feb 1976 di Bali; Keppres 14/1976 (daftar
  6 larangan pengeluaran APBN cocok persis); PP 11/1976 (ditetapkan
  31 Mar 1976, berlaku 1 Apr 1976, ubah Pasal 3 PP 16/1970 — JDIH
  BPK); pelantikan Piet Haryono 15 Apr 1976 (hmsoeharto.id;
  Wikipedia: Dirut 3 Mar 1976–15 Apr 1981); sidang tahunan ADB
  ke-9, April 1976; gempa Irian Jaya 26 Jun 1976 (M7.1, 422 tewas +
  5.000+ hilang, 6 desa hancur — Wikipedia id; ISC 713087); Palapa
  A1 diluncurkan 8 Jul 1976, SKSD Palapa diresmikan 16 Agu 1976
  (Soeharto cabut keris sbg saklar); UU 7/1976 Timor Timur
  ditandatangani 17 Jul 1976 (provinsi ke-27); MTQ ke-9 Samarinda
  1976 (189 peserta, 26 provinsi); IPTN diresmikan 23 Agu 1976
  (didirikan 26 Apr 1976, dirut BJ Habibie); Kilang Cilacap mulai
  beroperasi 24 Agu 1976; KTT Non-Blok V Colombo 16–19 Agu 1976
  (81 negara, Deklarasi Kolombo; Inpres 14/1976); Nuzulul Quran
  17 Ramadan 1396H = 11 Sep 1976; Keppres 43/1976 Puspitek
  (ditetapkan + berlaku 1 Okt 1976 — JDIH BPK); kunjungan resmi
  pertama PM Malcolm Fraser 7–11 Okt 1976 (komunike DFAT 10 Okt
  1976); surat edaran anti-perlakuan-istimewa keluarga Presiden
  B-3/Pres/9/1976 (kesaksian Sudharmono, soehartolibrary.id).
- Keputusan baca tersimpan di `workspace/goals/wiki-soeharto/hidden_files/batch1976_decisions.py`
  (di VM, bukan repo); skrip terapan `apply_batch1976.py` + skrip gabung
  `merge_batch1976.py` di folder yang sama.

### Batch 1977 (SELESAI, 7 Nov 2026, commit `7b8ddd84`, live)

- **Pembaca: 2 subagen baca paralel** (16 + 15 artikel), baca penuh
  dgn protokol pilot/batch 1976; rizky menggabungkan putusan +
  memverifikasi langsung 1 fix ke file aslinya.
- **Hasil: 31 artikel; 31 `cross_checked`, 0 `needs_review`,
  0 `disputed`.** Kumulatif Fase 1: **885 `cross_checked`,
  17 `needs_review`.**
- **1 perbaikan date/title:** 00516 (1977-04-14 → 1977-04-13 +
  title; isi + description menulis "RABU, 13 April 1977" di dua
  tempat, "14 April 1977" 0 kali; 13 Apr 1977 memang Rabu, 14 Apr
  = Kamis; footnote hal. 479–480 tepat di antara 00515 12 Apr hal.
  479 dan 00517 19 Apr hal. 480–481; sumber luar utk 13 vs 14 Apr
  tidak ditemukan — fix berdasarkan bukti internal isi).
- **5 relasi `menyebut` baru** (total 154: ekonomi 109, pemilu 10):
  4 ekonomi-orde-baru — 00507 (Inpres 6/1977: kredit pembangunan/
  pemugaran pasar, dana Rp25 milyar, bunga 0%), 00512 (pengesahan
  Keppres atas Persetujuan Tarif Preferensi ASEAN, kontur isi
  diuraikan — preseden 01063), 00515 (sidang Dewan Stabilisasi
  Ekonomi: inflasi Maret 0,06%, petunjuk harga beras, instruksi
  program konkret kopi), 01529 (instruksi tata niaga garam rakyat:
  floor price + ceiling price, PN Garam beli di bawah floor price /
  jual di atas ceiling price — mekanisme konkret sbg subjek utama);
  1 pemilu-orde-baru — 01483 (Keppres 49/1977: Panitia Pemeriksa
  Keanggotaan MPR/DPR 15→17 orang, berlaku surut 3 Agu 1977).
  Ekonomi DITOLAK di 00519 (persetujuan PT NGK Busi + PT Inoue
  Rubber hanya satu kalimat dlm artikel dua topik — preseden
  01977/00851), 01483 (Sensus Konstruksi = sensus statistik;
  pengawasan pekerja asing hanya penekanan), 01494 (Operasi Tertib
  = penertiban aparatur/anti-pungli), 01495 (laporan kunjungan +
  laporan harga, tanpa keputusan), 01496 (bantahan Ali Wardhana
  soal kurs — Rp415 hanya konteks kurs berlaku), 01499 (rencana
  modal Kuwait di kilang Batam masih pembicaraan mendatang),
  01527/01533 (pemberian/laporan bantuan), 01535 (instruksi umum
  beri prioritas perhatian tanpa mekanisme/angka); glosarium
  DITOLAK di 00508 ("stabilitas nasional" satu klausa dlm pidato
  persatuan-kesatuan) dan 01530 (satu klausa dlm pernyataan Isnaeni
  di paragraf terakhir); orde-baru + kopkamtib DITOLAK di 01494
  ("Orde Baru" tidak muncul eksplisit di isi, hanya di tag; Kepala
  Staf Kopkamtib hanya salah satu dari banyak penerima Inpres
  9/1977); kopkamtib DITOLAK di 01525 (Sudomo hanya pejabat yg
  berkomentar soal aksi mahasiswa); pemilu DITOLAK di 01498
  (pergantian personalia pasca-Pemilu 1977).
- **Indeks diperbarui:** seksi 1977 = **31** (tanpa perpindahan
  tahun; 00516 hanya geser dalam seksi 1977).
- **Temuan lain:** 00510 nama file "residen-soeharto" (huruf P
  hilang) — typo nama file, tidak diganti. 01525 aksi 8 mahasiswa
  duduki DPR (Sep 1977) TIDAK terkonfirmasi dari sumber luar
  (pencarian web tidak menemukan) — dicatat, bukan inkonsistensi
  internal (artikel konsisten: hari + tanggal + footnote).
  "Periode 1977/1983" di 01530 (kutipan Isnaeni) vs masa jabatan
  MPR 1978–1983 — dicatat, bukan fix. Urutan footnote: 00513
  (10 Apr) hal. 479 lalu 00514 (11 Apr) hal. 478–479 — entri buku
  berbagi halaman yg sama, bukan inkonsistensi tanggal.
- **Spot-check terkonfirmasi:** KTT ASEAN ke-2 Kuala Lumpur 4–5
  Agu 1977 (bertepatan HUT ke-10 ASEAN); Persetujuan Tarif
  Preferensi ASEAN ditandatangani Manila 24 Feb 1977 (asean.org);
  Keppres 49/1977 (ditetapkan 1 Sep 1977, berlaku surut 3 Agu 1977,
  Panitia Pemeriksaan 15→17 orang — JDIH BPK); sidang anti-apartheid
  Lagos 22–26 Agu 1977 (UN A/CONF.91/9); kurs Rp415/US$ berlaku
  sejak 1971 sampai devaluasi 15 Nov 1978 ke Rp625; Keppres 36/1977
  Team Koordinasi Peningkatan Ekspor ke Timur Tengah (ditetapkan
  20 Jul 1977 — JDIH BPK); Idul Fitri 1 Syawal 1397H = 15 Sep 1977.
- Keputusan baca tersimpan di `workspace/goals/wiki-soeharto/hidden_files/batch1977_decisions.py`
  (di VM, bukan repo); skrip terapan `apply_batch1977.py` + skrip gabung
  `merge_batch1977.py` di folder yang sama.

### Batch 1978 (SELESAI, 7 Nov 2026, commit `de033e26`, live)

- **Pembaca: 1 subagen** (17 artikel), baca penuh dgn protokol
  pilot/batch 1977; rizky menggabungkan putusan + memverifikasi
  sendiri needs_review 01675 ke file aslinya + pencarian web.
- **Hasil: 17 artikel; 16 `cross_checked`, 1 `needs_review`,
  0 `disputed`, 0 fix, 0 relasi `menyebut` baru.** Kumulatif Fase 1:
  **901 `cross_checked`, 18 `needs_review`.** FTS tidak berubah
  (total 1.382 relasi, 154 menyebut).
- **1 `needs_review`: 01675** (resmikan Pabrik Gula Gunung Madu) —
  isi "SENIN, 24 SEPTEMBER 1978" padahal 24 Sep 1978 = Minggu;
  footnote mengutip buku "Jejak Langkah Pak Harto 29 Maret 1978 –
  11 Maret 1983" hal. 206–207, lompatan besar dari tetangga Sep 1978
  (hal. 61–67 dlm buku yg sama); Wikipedia id menulis pabrik
  diresmikan Soeharto "pada tahun 1979" (musim giling pertama Mei
  1978, kapasitas 4.000 TCD — pabrik sudah beroperasi sebelum Sep
  1978, peresmian 1979 masuk akal); Senin terdekat tersingkir: 18 Sep
  ditempati 01591 (Jakarta), 25 Sep ditempati 01596 (pelantikan
  Kapolri pagi di Istana Negara — peresmian di Lampung pagi yg sama
  tidak mungkin). Tanggal benar tidak dapat ditentukan dari isi
  artikel sendiri → **tidak ada fix**; file tetap di seksi 1978
  sampai tanggal benarnya ditentukan.
- **Relasi `menyebut`: tidak ada yg diterima.** Ekonomi DITOLAK di
  01597 (pidato Pelita III hanya arahan umum perencanaan — angka
  31%→27% adalah proyeksi, bukan keputusan; larangan kunjungi
  steambath/kasino = pendisiplinan internal ABRI; kesepakatan landas
  kontinen hanya disebut sbg hasil pembicaraan), 01622 (instruksi
  umum kembangkan geothermal tanpa mekanisme/angka/proyek
  bernama/tenggat), 01588 (pembukaan pameran ternak + 5 arahan umum),
  01586 (pembahasan ekonomi tidak diuraikan), 01592 (peresmian LNG
  Arun, angka hanya konteks proyek). Glosarium DITOLAK di 01597
  ("Dwifungsi ABRI" tidak muncul eksplisit).
- **Indeks diperbarui:** seksi 1978 = **17** (tanpa perpindahan
  tahun, tanpa fix).
- **Temuan lain:** 01586 selisih hitung isi — "melantik enam orang
  Duta Besar" tapi hanya 5 nama disebut (dicatat, bukan fix). Ordinal
  benar: Hari Pramuka ke-17 (14 Agu 1961 → 1978). 1 Syawal 1398H =
  4 Sep 1978 konsisten dgn 1 Syawal 1397H = 15 Sep 1977. Rangkaian
  kunjungan Pham Van Dong konsisten lintas 3 artikel (tiba 20 Sep
  16.00 → pembicaraan 21–22 Sep → pulang 23 Sep 11.00). Selisih
  sumber dicatat, bukan fix: 01596 pelantikan Kapolri Awaluddin
  Djamin — kliping menulis SENIN 25 Sep 1978 (konsisten internal
  penuh), sedangkan Wikipedia id/kadin.co.id/tokoh.id/en.wikipedia
  sepakat 26 Sep 1978 (tepat di hari ulang tahunnya ke-51; Widodo
  left office 24 Sep 1978); 01598 pelantikan Habibie Ketua BPPT —
  kliping menulis KAMIS 28 Sep 1978, sedangkan buku BRIN (2018) +
  technologyindonesia.id menulis Habibie dilantik sbg Menristek
  sekaligus Ketua BPPT 23 Agu 1978. Catatan: PLTP Kamojang unit 1
  baru beroperasi 1982 — "akan segera berfungsi" di 01622 (1978)
  adalah pernyataan saat itu, bukan inkonsistensi internal.
- **Pelajaran proses (AGENTS.md):** brief subagen batch ini sempat
  memakai 15 nama file yg DITEBAK dari tampilan prep yg terpotong
  (52 karakter) — subagen menemukan file aslinya sendiri di server
  dan kunci putusannya cocok persis dgn `/tmp/batch1978.json`.
  Ke depan: SELALU scp batch JSON dulu dan cetak nama file LENGKAP
  sebelum menulis brief.
- **Spot-check terkonfirmasi:** Kilang LNG Arun diresmikan 19 Sep
  1978 (Wikipedia id Arun NGL; ekspor kondensat pertama ke Jepang
  14 Okt 1977); Konferensi TCDC Buenos Aires 30 Agu–12 Sep 1978;
  kunjungan Pham Van Dong — konteks tur regional terkonfirmasi
  sebagian (tiba Bangkok 6 Sep 1978, kunjungan 5 hari ke Thailand,
  kabel Deplu AS 1978BANGKO25726).
- Keputusan baca tersimpan di `workspace/goals/wiki-soeharto/hidden_files/batch1978_decisions.py`
  (di VM, bukan repo); skrip terapan `apply_batch1978.py` + skrip gabung
  `merge_batch1978.py` di folder yang sama.

### Batch 1979 (SELESAI, 7 Nov 2026, commit `3a42f920`, live)

- **Pembaca: 1 subagen** (15 artikel), baca penuh dgn protokol
  pilot/batch 1978; rizky menggabungkan putusan + memverifikasi
  sendiri relasi 01671 dan jangkar 01675 ke file aslinya.
- **Hasil: 15 artikel; 15 `cross_checked`, 0 `needs_review`,
  0 `disputed`, 0 fix di dalam batch, 1 relasi `menyebut` baru**
  (01671 → glosarium Trilogi Pembangunan; total 155, FTS 1.383).
  Kumulatif Fase 1: **917 `cross_checked`, 17 `needs_review`**
  (01675 keluar dari needs_review — lihat koreksi di bawah).
- **Koreksi 01675 (needs_review batch 1978 → cross_checked,
  1978-09-24 → 1979-09-24, pindah seksi 1978 → 1979):** jangkar
  footnote batch ini membuktikan hal. 206 dlm buku "Jejak Langkah
  29 Mar 1978–11 Mar 1983" adalah Sep 1979 — 01672 (19 Sep), 01673
  (21 Sep), 01674 (22 Sep) semua hal. 206; 01676 (27 Sep) hal. 208.
  01675 mengutip hal. 206–207 → jatuh 23–24 Sep 1979; kata hari
  "SENIN" mengunci 24 Sep 1979 (23 Sep = Minggu; 17 Sep = Senin
  tapi sudah ditempati 01668 hal. 204–205); Wikipedia id menulis
  pabrik Gunung Madu diresmikan Soeharto "pada tahun 1979". Tiga
  jangkar konvergen ke **1979-09-24** — satu-satunya tanggal yg
  konsisten dgn semuanya (preseden jangkar kronologi antar-artikel).
  Title FM + H1 ikut diperbaiki. Seksi 1978 = 16, seksi 1979 = 16.
- **Relasi `menyebut`: 1 diterima.** 01671 → glosarium (Soeharto
  "menguraikan secara terperinci" Trilogi Pembangunan di Wisma Duta,
  Singapura). Ekonomi DITOLAK di 01625 (sidang Ekuin soal inflasi +
  Semen Cibinong 2,4 jt ton — instruksi umum tanpa kontur kebijakan),
  01626 (instruksi efisiensi + inflasi 13,94% Apr–Agu 1979 — angka
  hanya konteks), 01627 (harapan BUUD/KUD efektif + Inpres 2/1978
  hanya dirujuk). Glosarium DITOLAK di 01672 ("stabilitas nasional"
  frasa generik satu kalimat; "Polkam" bukan konsep glosarium),
  01668 ("ketahanan nasional" bukan entri glosarium), 01666
  ("Tridharma" definisi Soeharto sendiri utk patung).
- **Indeks diperbarui:** seksi 1978 = **16**, seksi 1979 = **16**.
- **Temuan lain:** urutan footnote buku Sep 1979 monoton naik
  sempurna (hal. 201 → 208); semua kata hari cocok dgn tanggalnya;
  judul FM = H1 di semua artikel. Rangkaian kunjungan Singapura
  konsisten lintas 01668 (tiba 17 Sep) → 01671 (pulang 18 Sep);
  rangkaian Islam Jamaah konsisten 01628 (10 Sep) → 01629 (12 Sep).
  Typo isi dicatat saja: "Lee Kwan Yew" (01668, 01671), "Gubemur"
  (01668). Ordinal Hari Pramuka ke-18 benar (1961→1979, konsisten
  dgn ke-17 di 1978).
- **Spot-check terkonfirmasi:** kunjungan Wapres Mondale ke RRC —
  tiba Beijing 25 Agu 1979 (01624); SEA Games X dibuka Soeharto
  21 Sep 1979 di Senayan (01673); gempa Yapen 12 Sep 1979 (M7,5–7,9,
  115 korban, kerusakan Serui) — "baru-baru ini" tepat 10 hari
  sebelum pertemuan 22 Sep (01674).
- Keputusan baca tersimpan di `workspace/goals/wiki-soeharto/hidden_files/batch1979_decisions.py`
  (di VM, bukan repo); skrip terapan `apply_batch1979.py` + skrip gabung
  `merge_batch1979.py` di folder yang sama.

### Batch berikutnya (BELUM MULAI)

- Urutan batch: 1949–1967 (7),
  1995–1998 (4), tanpa tanggal (176, terakhir).
- Yang ikut dikerjakan di batch baca:
  **184 judul frontmatter terpotong**
  (hitung ulang 7 Nov 2026; angka lama 81 sudah tidak berlaku).
  Kedua tanggal invalid yg dikenal sejak Fase 0 sudah terpecahkan
  (01042 di batch 1973, 01448 di batch 1975).
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
