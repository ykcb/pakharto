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

### Batch berikutnya (BELUM MULAI)

- Urutan batch: 1971 (106), 1972 (84), 1973 (80), 1974 (82),
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
