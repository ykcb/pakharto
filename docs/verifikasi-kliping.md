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

## Fase 1 — Baca manusia/LLM per batch (BELUM MULAI)

Per batch: baca isi artikel, cek klaim ke sumber kedua
(`cross_checked` atau `disputed`), dan ekstrak relasi `menyebut` ke
entitas wiki yang disebut di isi artikel (maks ~5 per artikel; hanya
entitas yang sudah punya halaman). Satu kali baca menghasilkan dua hal.

- Pilot: tahun 1968 (81 artikel) — Hermes membaca, rizky memeriksa
  sampel acak + menerapkan, tim wiki spot-check. Dari pilot diputuskan
  kecepatan batch berikutnya.
- Urutan batch: 1969 (132), 1970 (135), 1971 (106), 1972 (84), 1973 (78),
  1974 (82), 1975 (88), 1976 (75), 1977 (31), 1978 (17), 1979 (15),
  1949–1967 (7), 1995–1998 (4), tanpa tanggal (177, terakhir).
- Yang ikut dikerjakan di batch baca: 2 tanggal invalid
  (1973-18-22, 1975-19-17) dan 81 judul frontmatter terpotong
  (diketahui sejak 6 Nov 2026).

## Catatan

- `source_checked` TIDAK berarti klaim sejarahnya benar — hanya berarti
  dokumennya sesuai dengan sumber arsipnya. Jangan menaikkan ke
  `cross_checked` tanpa pembacaan.
- Relasi spesifik per kliping TIDAK dibuat dari judul — hanya dari isi
  yang dibaca, dengan predikat `menyebut`.
