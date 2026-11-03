# Cetak Biru Wiki Orde Baru — Turunan dari wiki.iraamalia.id

**Tanggal:** 1 November 2026
**Status:** DRAF untuk keputusan user — bukan dokumen final.
**Untuk siapa:** (1) user sebagai pemegang keputusan, (2) agen AI pembangun di server lain sebagai pelaksana, (3) agen teknisi sebagai pengumpul data.
**Inti dalam satu kalimat:** bangun wiki Orde Baru dengan pola yang sudah terbukti di irawiki — Markdown di git sebagai source of truth, SQLite FTS5 sebagai index, Quartz sebagai frontend, MCP sebagai jalur baca mesin — tetapi dengan isi, taksonomi, dan filter yang disesuaikan untuk sejarah, bukan untuk berita berjalan.

> Cara membaca status di dokumen ini:
> - **DIPINJAM dari irawiki** = sudah terbukti jalan, pakai apa adanya kecuali ada alasan kuat mengubahnya.
> - **DISESUAIKAN untuk Orde Baru** = pola irawiki dipakai, isinya diubah.
> - **[KEPUTUSAN USER]** = jangan ditebak agen pembangun. Berhenti, tanyakan, catat jawabannya, baru lanjut.

---

## 0. Cara pakai dokumen ini

1. User membaca §1, §10, dan Lampiran C dulu, lalu memutuskan hal-hal bertanda **[KEPUTUSAN USER]**.
2. Agen pembangun bekerja **satu fase selesai dan terverifikasi sebelum fase berikutnya** (§16). Jangan membangun frontend, indexer, dan 50 halaman sekaligus.
3. Agen teknisi **tidak menulis halaman wiki**. Teknisi hanya menyerahkan paket data sesuai §17. Penulisan, verifikasi, dan keputusan masuk/tidaknya tetap di jalur konten + user.
4. Definisi "selesai" di seluruh dokumen ini = **PR siap dibaca di GitHub, belum live**. Live hanya terjadi setelah user merge manual dan build/indexer pasca-merge terverifikasi (§15). Jangan pernah menulis "sudah tayang" sebelum itu terbukti di URL live.

---

## 1. Apa yang dibangun

### 1.1 Tujuan

Wiki Orde Baru adalah **rujukan fakta yang komprehensif dan saling terhubung** tentang sistem kekuasaan, ekonomi, dan kehidupan masyarakat Indonesia pada masa Orde Baru (konvensi umum: 1966–1998), yang bisa dipakai pembaca muda maupun LLM sebagai rujukan.

Bukan: ensiklopedia biografi Soeharto semata, bukan arsip opini, bukan kumpulan artikel viral, bukan pengadilan sejarah. Wiki ini menjawab pertanyaan "apa yang terjadi, siapa pelakunya, lewat aturan/lembaga apa, dan apa warisannya sampai hari ini" — dengan sumber yang bisa dilacak.

### 1.2 Posisi terhadap wiki yang sudah ada

- **wiki.iraamalia.id (irawiki)** tetap berjalan sendiri. Wiki Orde Baru adalah **instans baru di server lain**, bukan cabang, bukan fork mentah, dan bukan pengganti irawiki.
- Yang dipinjam adalah **arsitektur dan tata kelola**, bukan isi mentah. Jangan menyalin halaman irawiki bulat-bulat ke wiki baru tanpa verifikasi ulang dan penyesuaian konteks sejarah.
- **Perhatian khusus — wiki Soeharto (pakharto.my.id):** wiki itu sudah serah terima final 18 Oktober 2026 ke agen lain dan bukan lagi pekerjaan agen konten ini. Wiki Orde Baru membahas Soeharto sebagai **aktor dalam sistem**, bukan sebagai biografi lengkap. Kalau ada tumpang tindih, **tautkan, jangan duplikasi**. Bila agen pembangun menemukan duplikasi substansial, laporkan ke user, jangan diam-diam menggabungkan.

### 1.3 Target ceruk — DIPINJAM dari irawiki, DISESUAIKAN isinya

1. **Topik Indonesia-spesifik** yang tidak bisa digantikan Wikipedia umum: jaringan kuasa, regulasi, lembaga, konglomerat, dan kebijakan khas Orde Baru, dengan data yang bisa dikutip per fakta.
2. **Sudut anak muda:** setiap hub/analisis menjawab "apa relevansinya dengan anak muda?" lewat **rantai mekanisme dari fakta halaman itu sendiri** — misalnya warisan aturan, utang, struktur kepemilikan, atau budaya birokrasi yang masih bekerja hari ini. Bukan tempelan moral, bukan generalisasi "anak muda itu…", bukan opini baru tanpa dukungan isi halaman. Kalau datanya belum ada, tulis pendek dan jujur "belum terverifikasi", jangan dikarang.

---

## 2. Prinsip yang tidak boleh ditawar

1. **Markdown di git = source of truth. Index = turunan yang bisa di-rebuild.** Kalau index rusak, rebuild dari Markdown. Jangan pernah mengedit index sebagai sumber.
2. **Satu topik = satu hub living document** (§8). Kejadian baru (untuk wiki sejarah: temuan sumber baru, koreksi, atau penafsiran baru yang terdokumentasi) masuk sebagai entri/koreksi di hub yang ada, bukan halaman baru sembarangan.
3. **Wiki = data, fakta, peristiwa. Super selektif.** Komentar, opini, dan saling sahut antar-pihak pada umumnya TIDAK masuk sebagai entri. Yang masuk adalah yang **mengubah sesuatu** (§9).
4. **Pisahkan tiga lapis dengan eksplisit:** (a) fakta terverifikasi, (b) klaim pihak (diberi label siapa yang mengklaim, kapan, di mana), (c) interpretasi/analisis (diberi label sebagai interpretasi, di halaman analisis, bukan diselipkan sebagai fakta di hub).
5. **Setiap klaim penting terverifikasi dari sumber yang benar-benar dibuka.** Angka menempel pada pelaku + mekanisme + arti + sumber. Target/rencana tidak ditulis sebagai capaian. Klaim tunggal dari satu sumber diberi atribusi ke sumber itu.
6. **Provenance per relasi.** Setiap relasi wajib punya sumber (URL atau referensi arsip yang bisa dilacak). Relasi tanpa sumber = low-confidence, masuk `proposals/`, bukan frontmatter final.
7. **Tidak ada jalur tulis yang melewati review manusia untuk konten sensitif.** Draft → review → commit. Write langsung ke `main` ditolak. Ini berlaku juga untuk agen pembangun dan watcher otomatis (§15).
8. **Skala secukupnya, nol biaya baru yang tidak perlu.** Tanpa embedding, tanpa vector DB, tanpa biaya API untuk pencarian. Alasannya empiris dari irawiki: pada 334 halaman, FTS5 lebih dari cukup dan build Quartz hanya belasan detik. Migrasi frontend hanya jika pemicu objektif tercapai (§3.4).
9. **Jangan menebak.** Jangan menebak URL dari link inline, jangan menebak nama dari daftar berinisial, jangan menggabungkan halaman dengan judul sama tanpa review editorial, jangan mengarang fakta demi mengisi section.
10. **Bahasa Indonesia hidup, nada faktual.** Hindari kalque dari Inggris dan pola kalimat AI yang generik. Istilah asing/hukum disebut lengkap dulu, lalu dijelaskan singkat. Di wiki, nada lebih datar daripada di blog: fakta dulu, gaya kemudian.

---

## 3. Arsitektur teknis — DIPINJAM dari irawiki

### 3.1 Diagram

```
SOURCE OF TRUTH (dipertahankan sebagai pola)
Markdown + frontmatter (git) → proposals/ → review user → commit ke main
                │
                │  indexer (Python, systemd timer 15 menit, incremental via content_hash)
                ▼
INDEX — wiki_index.db (satu file SQLite)
├── pages, chunks_fts (FTS5, unicode61 + trigram)
├── entities, relations, aliases, sources
                │  dibaca oleh
                ▼
MCP SERVER (uvicorn :8000, 12 tools — lihat §3.3)
                │
                ▼
Agen pembangun / agen lain  +  frontend Quartz (rebuild pasca-merge saja)
```

### 3.2 Stack

| Komponen | Pilihan irawiki | Untuk wiki Orde Baru |
|---|---|---|
| Source of truth | Markdown + frontmatter di git | **Sama.** Repo git terpisah dari irawiki. |
| Frontend | Quartz 5 + nginx | **Sama sebagai titik awal.** |
| Index | SQLite FTS5 saja, tanpa embeddings | **Sama.** Alasan: RAM server irawiki hanya ~2 GB; jangan menambah vector DB tanpa keputusan user. |
| Indexer | Python stdlib + sqlite3, timer 15 menit, `PRAGMA journal_mode=WAL`, VACUUM mingguan | **Sama.** Backfill penuh irawiki < 1 menit pada 334 halaman; patokan ini dipakai untuk uji kinerja wiki baru. |
| MCP | `wiki_query.py` → `wiki_index.db`, uvicorn :8000 | **Sama polanya.** Port dan path boleh disesuaikan server baru, tapi kontrak tool-nya sama (§3.3). |
| Deploy | GitHub Actions (irawiki kini monorepo wiki+blog) | **[KEPUTUSAN USER]** — repo dan pipeline deploy wiki Orde Baru diputuskan terpisah; jangan diasumsikan sama dengan irawiki. |

### 3.3 Kontrak MCP — 12 tools irawiki, dipakai sebagai spesifikasi

Agen pembangun tidak perlu meniru bug lama irawiki (dulu `search` hanya substring scan dan `get_relations` masih stub). Yang ditiru adalah **kontrak final pasca-Fase 3**:

- `search` → FTS5 BM25 berbobot (judul ×3, heading ×2) + ekspansi alias, bukan substring scan.
- `get_entity` → baca tabel entities + agregasi relasi + sumber; kalau nama ambigu, kembalikan `candidates[]`, **jangan menebak satu halaman**.
- `get_relations` → baca tabel relations, dukung depth N-hop dan filter origin (frontmatter vs wikilink).
- `relations_between` → BFS di tabel relations (contoh uji irawiki: Jokowi → Prabowo = 2 hop).
- `timeline` → query relations + pages, filter tipe peristiwa, urut tanggal kronologis.
- `get_page`, `stats` → baca halaman dan statistik index.
- `save_draft` → **satu-satunya jalur tulis lewat MCP**, ke `proposals/` untuk review. **Tidak dibuat `write_page` langsung** — itu regresi tata kelola.
- Alat-alat lain yang sudah ada di irawiki dipertahankan polanya; daftar final 12 tools dicatat di laporan Fase 3, bukan dikarang di sini.

### 3.4 Pemicu migrasi frontend — DIPINJAM, jangan didahului

Tetap Quartz sampai salah satu pemicu tercapai: **halaman > 1.500 ATAU build Quartz > 2 menit**. Evaluasi ulang hanya setelah index berjalan. Jangan mengerjakan migrasi Hugo di fase awal hanya karena "nanti besar".

### 3.5 Batasan server — WAJIB dikonfirmasi sebelum membangun

**[KEPUTUSAN USER / INFO DARI AGEN PEMBANGUN]:** RAM, vCPU, disk, dan swap server baru harus dicatat di laporan Fase 0. Patokan irawiki: 2 vCPU, RAM ~1,9 GB, disk 28 GB, swap 4–6 GB. Kalau server baru lebih kecil, indexer dan build harus diuji dengan batas itu, bukan diasumsikan longgar. Tanpa Docker di irawiki — kalau server baru memakai Docker, itu keputusan eksplisit, bukan default diam-diam.

---

## 4. Struktur repo — DISESUAIKAN

Struktur ini meniru irawiki (folder = petunjuk `entity_type`), ditambah folder yang memang dibutuhkan sejarah Orde Baru.

```
content/
├── aktor/          # orang: Soeharto, menteri, jenderal, pengusaha, aktivis, dsb.
├── peristiwa/      # hub topik + halaman milestone (lihat §8)
├── analisis/       # interpretasi/sintesis yang dilabeli sebagai interpretasi
├── konsep/         # penjelas istilah (Dwifungsi ABRI, Trilogi Pembangunan, dsb.)
├── lembaga/        # lembaga/organisasi khas Orde Baru (Kopkamtib, Bakin, Bulog era Orba, dsb.)
├── regulasi/       # UU, Tap MPR, Keppres, Inpres yang menjadi tonggak (ringkas + tautan naskah)
├── kategori/       # halaman arsip 6 kategori publik (§10)
├── pelajaran/      # track Pelajaran: apa yang bisa dipelajari generasi kini — pola Fakta → Inferensi berlabel → Batas data + disclaimer (§5.4)
├── index.md        # homepage: blok "Mulai dari Sini!" (6 kategori) + "Baru Update"
└── ...             # halaman root lain hanya bila perlu, jangan menumpuk di root
docs/
├── playbook-halaman-rujukan.md   # dokumen operasional §7 (source of truth konten)
├── youth-relevance/               # metode + peta + rubrik (diadaptasi, bukan ditempel mentah)
└── taksonomi-kategori.md          # definisi kategori §10
proposals/          # semua draf + ekstraksi low-confidence, menunggu review
data-teknisi/       # BUKAN konten wiki — paket unduhan teknisi + manifest (§17), tidak diindeks sebagai halaman
```

Aturan penamaan:

- Slug: huruf kecil, strip sebagai pemisah, tanpa spasi dan tanpa karakter aneh. Contoh: `dwifungsi-abri`, `krisis-moneter-1997-1998`, `soeharto`.
- Satu halaman = satu file. Jangan membuat satu file raksasa untuk satu dekade; pecah per hub, tautkan lewat wikilink.
- Wikilink: `[[Nama Halaman]]` untuk relasi antar-halaman. Judul halaman dan slug harus konsisten; alias dicatat di frontmatter, bukan dibuat halaman duplikat.
- File stub (body < 200 karakter) diberi `status: stub` dan **dikecualikan dari prioritas FTS** sampai dikembangkan. Jangan menghapus stub diam-diam, jangan mengembangkan stub tanpa sumber.

---

## 5. Skema frontmatter — DIPINJAM, dibekukan di Fase 1

Frontmatter adalah kontrak. Agen pembangun membekukannya di Fase 1 dan tidak mengubah field seenaknya di tengah jalan. Penambahan field lewat review.

### 5.1 Field wajib untuk semua halaman konten

```yaml
---
title: "Dwifungsi ABRI"
description: "Penjelasan 1–2 kalimat: definisi + status/posisi dalam sistem Orde Baru."
date: 1966-03-11
updated: 2026-11-01
last_updated: "2026-11-01"
entity_type: topik        # aktor | peristiwa | organisasi | regulasi | lokasi | topik | pelajaran
entity_id: "dwifungsi-abri"
aliases:
  - "Dwi Fungsi ABRI"
tags: [konsep, abri, orde-baru]   # HANYA dari daftar tag canonical (lihat §5.3)
kategori: konsep                  # tepat satu kategori utama (§10)
kategori_tambahan: []             # opsional, untuk halaman lintas kategori
risiko_editorial: sedang         # rendah | sedang | tinggi
status: ""                        # kosong, atau "stub" bila body < 200 karakter
confidence: ""                    # diisi bila relevan: low | medium | high (untuk ekstraksi)
sumber:
  - url: https://...
    judul: "..."
    tanggal: 2026-11-01
relasi:
  - predikat: terkait_dengan      # dari daftar terkontrol §6
    objek: "Soeharto"
    sumber: https://...           # wajib per relasi
---
```

Catatan dari pelajaran irawiki (Fase 1, Oktober 2026):

- Backfill `entity_type` dari nama folder terbukti 98,5% akurat (133/135 file); file ambigu (index, halaman root) **jangan ditebak** — masuk `proposals/`.
- Ekstraksi `## Sumber` dari prosa hanya berhasil sebagian (59/202 file → 100 record). File yang sumbernya hanya prosa tanpa URL ditandai `sumber_status: prosa` dan masuk backlog, **bukan dipaksa jadi URL tebakan**. Opsi "tebak URL dari link inline body" **DITOLAK** karena risiko provenance palsu.
- Ekstraksi relasi low-confidence **tidak ditulis ke frontmatter** — tulis ke `proposals/` dengan alasan keraguan.
- Untuk konten baru, URL sumber **wajib** di validasi `save_draft`. Untuk konten lama yang diimpor, `sumber` boleh null sementara dengan fallback ke sumber level halaman, tapi harus tercatat sebagai utang, bukan dianggap beres.
- `date` untuk halaman sejarah = tanggal peristiwa/berlakunya konsep bila ada; `updated`/`last_updated` = tanggal terakhir halaman diperbarui. Jangan mencampur keduanya.

### 5.2 Field khusus per tipe

- **Aktor:** tambah infobox di body (§7.4), bukan field baru yang liar. Field frontmatter tetap sama; detail biografis di body.
- **Regulasi:** tambah di frontmatter bila tersedia: `nomor_regulasi`, `tahun_regulasi`, `lembaga_penerbit` — hanya bila bisa diverifikasi dari naskah; jangan menebak nomor.
- **Hub:** `entity_type: topik`, tambah `alias:` untuk varian nama topik.
- **Halaman milestone:** tambah `relasi:` balik ke hub induk ("Bagian dari: [[Nama Hub]]") — lihat §8.

### 5.3 Tag canonical

Tags adalah indeks halus (fine-grained), kategori adalah navigasi kasar (§10). Keduanya **tidak dicampur**. Daftar tag canonical dibuat di Fase 1 dari impor awal, lalu dinormalisasi (pelajaran irawiki: 235 → 226 halaman tag canonical). Tag baru hanya lewat review, bukan dibuat spontan per halaman.

---

## 6. Predikat relasi terkontrol — DIPINJAM

Daftar tertutup. Jangan mengarang predikat baru tanpa review:

`terlibat_dalam`, `menunjuk`, `didukung_oleh`, `menentang`, `anggota_dari`, `memimpin`, `terkait_dengan`, `menyebut`

Aturan pakai:

- Kalau teks sumber tidak cocok ke satu pun predikat, pakai `terkait_dengan` dan tandai untuk review — jangan memaksakan predikat yang lebih kuat dari bukti.
- Setiap relasi wajib punya sumber. Tanpa sumber jelas → low-confidence → `proposals/`.
- Relasi dari wikilink di body dicatat dengan `origin: wikilink`, relasi dari frontmatter dengan `origin: frontmatter` — agar bisa diaudit mana yang eksplisit, mana yang turunan.
- Jangan menggabungkan dua daftar dari otoritas berbeda menjadi satu daftar (misalnya daftar tersangka pidana vs daftar sanksi administratif). Tulis tiap daftar dengan otoritas, jumlah, dan tanggalnya sendiri.

---

## 7. Template halaman — DIPINJAM dari playbook "Halaman Rujukan" irawiki

Prinsip template: **definisi dulu, fakta terstruktur, sumber ber-link, tanggal jelas.** Urutan section di bawah adalah urutan baku. Section yang belum ada datanya boleh pendek atau ditulis "belum terverifikasi" — jangan dikarang, jangan dihapus diam-diam dari template.

Judul section relevansi yang berlaku (keputusan irawiki 21 Oktober 2026, dipakai juga di sini):

```
## Apa relevansinya dengan anak muda?
```

Konvensi lama `## Kenapa penting buat Gen Z` tidak dipakai lagi untuk halaman baru.

### 7.1 Hub (living document) — tipe utama wiki

```
> **Ringkasan:** 2–3 kalimat: definisi topik + status terkini (untuk sejarah: apa yang sudah terjadi + apa warisannya yang masih bisa dilacak).

## Apa relevansinya dengan anak muda?
1–3 paragraf faktual, rantai mekanisme dari fakta halaman (lihat §1.3).

## Fakta kunci
Tabel bila relevan: tanggal / kejadian / status / pelaku / dasar hukum.

## Kronologi
### YYYY-MM-DD
- 1–4 bullet faktual per kejadian. Satu kejadian = satu sub-heading.
- Urut kronologis tua → baru.
- Setiap bullet menempel pada sumber di ## Sumber (lihat §7.6).

## Aktor yang terlibat
- [[Nama Aktor]] — peran 1 kalimat. Kumulatif, diperbarui bila ada aktor baru.

## Sumber
Link outbound real, berlabel (media / lembaga / arsip + tanggal). Dikelompokkan per tanggal kejadian bila kronologi panjang, agar provenance per fakta terjaga.

## Catatan presisi
Klaim belum terverifikasi, koreksi atas klaim yang beredar, perbedaan versi sumber, dan apa yang sengaja TIDAK dimasukkan + alasannya.
```

Contoh hub irawiki yang bisa dibuka sebagai referensi bentuk (bukan isi): "Kinerja Pemerintahan Prabowo-Gibran" — Ringkasan, Fakta kunci per bidang, Kronologi bertanggal, Aktor, Sumber berlabel, Catatan presisi yang panjang dan eksplisit. Bentuknya yang dipinjam, bukan angkanya.

### 7.2 Peristiwa (milestone)

Sama seperti hub, tanpa `## Fakta kunci` bila tidak relevan. Kronologi di sini adalah urutan kejadian **di dalam peristiwa itu sendiri**. Wajib memuat taut balik ke hub: "Bagian dari: [[Nama Hub]]" di badan atau frontmatter `relasi:`.

### 7.3 Analisis

1. Ringkasan. 2. `## Apa relevansinya dengan anak muda?` 3. `## Fakta yang relevan` (bullet, bersumber — hanya fakta yang sudah ada di halaman wiki + sumber terverifikasi, tanpa fakta karangan). 4. `## Perspektif / Interpretasi` — dilabeli jelas sebagai interpretasi, bukan fakta. 5. Sumber.

Analisis yang berdiri sendiri boleh tetap halaman terpisah, dan **ditautkan dari hub** di bagian "Analisis terkait". Jangan menyelipkan interpretasi panjang ke dalam hub faktual.

### 7.4 Aktor

1. Definisi 1 kalimat: "X adalah …".
2. Infobox tabel: Nama lengkap, Alias, Lahir, Basis daerah (bila relevan dan terverifikasi), Jabatan/peran aktif pada masa Orde Baru, Afiliasi utama.
3. `## Apa relevansinya dengan anak muda?` — boleh sangat terbatas atau pendek untuk halaman biografis; jangan dipaksa panjang.
4. Rekam jejak bertanggal (pola yang sama dengan Kronologi hub, tapi fokus pada aktor).
5. Relasi (wikilink). 6. Sumber.

### 7.5 Konsep

1. Definisi 1–2 kalimat yang bisa dikutip. 2. Asal-usul dan dasar hukum/dokumen (bila ada). 3. Bagaimana konsep itu bekerja dalam praktik Orde Baru (dengan contoh peristiwa yang ditautkan, bukan contoh karangan). 4. `## Apa relevansinya dengan anak muda?` 5. Halaman yang memakai konsep ini (taut dua arah). 6. Sumber + Catatan presisi (perbedaan definisi antar-sumber ditulis eksplisit, bukan dipilih diam-diam satu versi).

Kriteria masuk konsep: dipakai ≥ 2 halaman, atau menjadi kunci memahami satu benang/kategori (§10). Jangan membuat halaman konsep untuk istilah yang hanya muncul sekali.

### 7.6 Regulasi / Lembaga

- **Regulasi:** ringkasan isi yang relevan (bukan salinan naskah penuh bila berhak cipta/terlalu panjang), nomor + tanggal + lembaga penerbit, pasal kunci yang dikutip, dampak yang terverifikasi, tautan ke naskah resmi bila tersedia, halaman-halaman yang merujuk regulasi itu.
- **Lembaga:** definisi, dasar pembentukan, periode aktif, fungsi, pimpinan kunci per periode (bertanggal), pembubaran/perubahan (bila ada), sumber.

### 7.7 Aturan sumber di body

- Sumber ditulis berlabel, bukan sekadar URL telanjang di tengah kalimat.
- Kutipan pihak ditulis sebagai kutipan pihak ("Menurut X, …"), bukan sebagai fakta wiki.
- Kalau dua sumber bertentangan, tulis keduanya sebagai klaim masing-masing + Catatan presisi, jangan memilih satu dan menghapus yang lain tanpa alasan yang ditulis.

---

## 8. Kebijakan granularitas — DIPINJAM, DISESUAIKAN contohnya

Berlaku sejak halaman pertama wiki Orde Baru.

1. **Hub adalah default.** Kejadian/temuan baru masuk sebagai entri bertanggal di hub yang sudah ada, BUKAN halaman baru.
2. **Halaman peristiwa baru hanya untuk milestone.** Kriteria milestone (pilih salah satu, dan buktikan di Catatan presisi):
   a. Putusan/amar pengadilan yang resmi;
   b. Pengesahan UU / Tap MPR / peraturan / keputusan resmi lembaga negara;
   c. Pelantikan, pengangkatan, atau reshuffle resmi;
   d. Peristiwa dengan ≥ 3 sumber independen DAN set aktor/sumber yang jelas berbeda dari isi hub;
   e. **Khusus sejarah:** titik balik yang mengubah struktur — misalnya pergantian rezim, pembubaran lembaga, perubahan konstitusional, atau krisis yang mengubah arah kebijakan secara terdokumentasi. "Titik balik" harus dibuktikan dengan perubahan yang bisa ditunjuk (aturan, lembaga, kepemilikan, status), bukan sekadar "peristiwa besar" menurut opini.
3. **JANGAN PERNAH buat halaman baru untuk:** pernyataan/komentar tokoh, respons koalisi/partai, wacana/usulan, liputan perkembangan lanjutan, atau satu artikel opini — semua itu entri kronologi di hub, atau tidak masuk sama sekali bila tidak lolos §9.
4. **Bila ragu antara hub vs milestone → pilih hub**, catat di `risiko_editorial`, ajukan via `proposals/`.
5. **Migrasi/rapian:** halaman peristiwa lama yang ternyata hanya perkembangan lanjutan diringkas menjadi entri kronologi di hub; halaman milestone yang layak tetap berdiri, masing-masing ditaut balik ke hub. Jangan menghapus halaman lama tanpa jejak git dan laporan.

---

## 9. Filter bermakna — versi sejarah Orde Baru

Filter irawiki (28 Oktober 2026) dipakai, dengan penyesuaian untuk bahan sejarah. Uji satu pertanyaan untuk setiap kandidat sebelum menulis entri:

> **Apakah kabar/peristiwa ini mengubah keadaan, status hukum, kepemilikan, aturan yang berlaku, atau susunan lembaga?**

### 9.1 Yang lolos (contoh tipe, bukan daftar final)

- Putusan pengadilan, terbitnya peraturan baru (Tap MPR, UU, Keppres, Inpres, Kepmen), pembentukan/pembubaran lembaga.
- Merger/akuisisi, transaksi bisnis besar yang terdokumentasi, perjanjian kerja sama, pencabutan/pembekuan izin, penetapan tersangka yang mengubah status hukum.
- Pelantikan/pemberhentian pejabat, hasil pemilu yang mengubah komposisi kekuasaan, perubahan kebijakan moneter/fiskal yang berlaku.
- **Ucapan sebagai perbuatan:** hanya bila ucapan itu sendiri adalah perbuatannya — misalnya pejabat yang menandatangani peraturan, hakim yang mengucapkan putusan, atau pengumuman pengunduran diri yang berlaku saat itu juga. Pidato biasa bukan perbuatan dalam arti ini.

### 9.2 Yang tidak lolos sebagai entri wiki (tahan, jangan tulis sebagai fakta)

- Komentar, pernyataan pejabat, penilaian analis, desakan, dan sahut-sahutan antar-pihak — ukurannya bukan siapa yang bicara, melainkan apakah realitas berubah karena kabar itu.
- Demo dan aktivasi isu publik **sebagai halaman berdiri sendiri**. Penyesuaian untuk sejarah: demonstrasi besar (misalnya rangkaian Mei 1998) tetap dicatat, tetapi sebagai **entri kronologi di hub krisis/reformasi**, dengan konsekuensi yang terdokumentasi (korban, perubahan kebijakan, pengunduran diri), bukan sebagai halaman demo per demo dan bukan sebagai inferensi motif. Nilai demo sebagai "komunikasi politik" atau "pemetaan aktor" adalah inferensi manusia — jangan dicuci menjadi fakta wiki.
- Memoar dan kesaksian tunggal yang belum terkonfirmasi sumber lain: perlakukan sebagai **klaim pihak** di Catatan presisi atau di halaman analisis, bukan sebagai fakta hub, sampai ada konfirmasi independen.
- Daftar yang hanya berinisial atau tanpa nama: tahan sampai otoritas yang berwenang membuka namanya. Jangan menebak nama dari daftar lain.

### 9.3 Tuntut data cukup + dedup + tunjukkan yang tersingkir

- Tulis entri hanya bila **nama aktor, perbuatan, dan tanggalnya terverifikasi dari sumber yang benar-benar dibuka**. Tipe yang lolos saja tidak cukup bila datanya tipis.
- Cek dedup terhadap kronologi hub tujuan sebelum menulis: buang kandidat yang tanggal dan intinya sudah ada, pisahkan jelas mana entri baru dan mana yang sudah ada.
- Setiap laporan entri/pantauan **wajib memuat daftar tersingkir + satu alasan singkat per kandidat** (misalnya: hanya pernyataan, hanya desakan yang belum terjadi, nama belum dibuka, data tipis). Laporan yang hanya memuat yang lolos tidak membuktikan filter diterapkan.
- Materi tersingkir **bukan** otomatis menjadi utas/konten lain. Format lapisan pengamatan untuk materi non-tonggak di irawiki masih belum diputuskan — jangan mengarang formatnya sendiri untuk wiki Orde Baru tanpa keputusan user.

---

## 10. Taksonomi publik wiki Orde Baru — DRAF, menunggu keputusan user

### 10.1 Prinsip taksonomi — DIPINJAM dari irawiki

Keputusan irawiki 22 Oktober 2026 dipakai sebagai pola, **bukan** sebagai isi:

- Kategori DIPUBLIKASIKAN sebagai taksonomi resmi dan ditampilkan di index/homepage — bukan istilah internal.
- Format dua lapis: **nama tampil** (singkat, menarik, bentuk pertanyaan bila cocok) + **deskriptor** (menjelaskan isi + memuat kata kunci untuk pencarian manusia & LLM).
- Slug berbasis kata kunci, nama tampil berbasis brand.
- Satu kategori utama per halaman (`kategori:`), lintas kategori via `kategori_tambahan`.
- Setiap kategori = halaman arsip di `kategori/<slug>.md` berisi definisi kategori + daftar anggota (Hub · Peristiwa · Analisis · Aktor), dipelihara manual dulu di fase awal.
- Index/homepage: blok "Mulai dari Sini!" berisi kategori-kategori itu; daftar entri terbaru dipindah ke blok "Baru Update" tersendiri (jangan dihapus); "Atau Telusuri Semua" di paling bawah/sidebar.
- Kategori + deskriptornya masuk ke `llms.txt`.
- Tags tetap indeks halus; kategori adalah navigasi kasar. Keduanya tidak dicampur.

### 10.2 Usulan 6 kategori Orde Baru — DRAF, BUKAN final

Nama-nama di bawah ini adalah **usulan agen konten untuk didiskusikan**, bukan keputusan user. Jangan menganggapnya final seperti nama irawiki 22 Oktober 2026. **[KEPUTUSAN USER]** untuk nama tampil final, deskriptor final, dan slug final.

| # | Nama tampil (USULAN) | Deskriptor (USULAN) | Slug (USULAN) |
|---|---|---|---|
| 1 | Bagaimana Orde Baru Berkuasa? | Transisi kekuasaan, legitimasi, pemilu, militer, dan aturan main politik 1966–1998 | `kekuasaan-dan-legitimasi` |
| 2 | Siapa Menguasai Ekonomi? | Pembangunan, konglomerat, BUMN, utang, dan konsentrasi kepemilikan di era Orde Baru | `ekonomi-dan-kepemilikan` |
| 3 | Siapa Diawasi, Siapa Dibungkam? | Keamanan, intelijen, pers, dan penindakan terhadap oposisi dan kritik | `keamanan-dan-kebebasan` |
| 4 | Bagaimana Rakyat Hidup? | Desa, buruh, tani, pendidikan, transmigrasi, dan kehidupan sehari-hari di bawah pembangunan Orde Baru | `pembangunan-dan-kehidupan` |
| 5 | Bagaimana Orde Baru Berakhir? | Krisis 1997–1998, gerakan reformasi, dan transisi keluar dari Orde Baru | `krisis-dan-reformasi` |
| 6 | Konsep Kunci | Penjelas istilah dan konsep yang sering dipakai untuk memahami Orde Baru | `konsep` |

Catatan: nama kategori 3 sengaja dibuat pertanyaan netral-faktual, bukan vonis. Nada kategori harus mengundang baca, bukan menghakimi di judul. Kalau user ingin nada berbeda, itu keputusan user, bukan agen.

### 10.3 Hub induk dan benang baca — DISESUAIKAN

Irawiki punya poros "Kinerja Pemerintahan" sebagai peta isi per bidang. Padanan untuk wiki Orde Baru:

- **Hub induk: "Orde Baru (1966–1998)"** — peta isi, bukan ensiklopedia dalam satu halaman. Isinya: definisi singkat, periodisasi kerja (lihat §10.4), daftar hub per kategori, dan jalur baca. Bidang yang materinya cukup tumbuh menjadi hub sendiri; hub induk tetap ringkasan + penunjuk.
- **Benang baca (jalur pemahaman):** setiap hub utama memuat bagian "Baca juga / jalur pemahaman" yang menautkan hub-hub dalam satu benang secara terkurasi, bukan semua halaman yang menyebut kata yang sama. Contoh benang kerja (untuk divalidasi sumber, bukan diasumsikan):
  - Kekuasaan: transisi 1965–1967 → Dwifungsi ABRI → pemilu-pemilu Orde Baru → lembaga keamanan.
  - Ekonomi: Repelita dan pembangunan → konglomerat dan BUMN → krisis moneter 1997–1998.
  - Akhir rezim: krisis ekonomi → gerakan mahasiswa dan masyarakat → transisi Mei 1998 → warisan kelembagaan.

### 10.4 Periodisasi kerja — DRAF, wajib divalidasi sumber

Periodisasi di bawah ini hanya **kerangka kerja untuk mengorganisasi hub**, bukan klaim sejarah final. Agen pembangun tidak boleh menulisnya sebagai fakta baku tanpa sumber di halaman hub induk.

- 1965–1967: transisi dan konsolidasi kekuasaan (jangkar yang umum dirujuk: Supersemar 11 Maret 1966).
- 1968–1973: penataan rezim dan pemilu pertama Orde Baru (1971).
- 1974–1982: pembangunan, gejolak awal (Malari 1974 sebagai jangkar riset), dan pengetatan politik.
- 1983–1990: konsolidasi lanjutan, kasus-kasus penindakan dan perlawanan yang terdokumentasi.
- 1991–1996: keterbukaan terbatas, dinamika oposisi, dan akumulasi ketegangan.
- 1997–1998: krisis dan berakhirnya Orde Baru (jangkar: pengunduran diri Soeharto 21 Mei 1998).

**[KEPUTUSAN USER]:** apakah periodisasi ini dipakai, diubah, atau diganti dengan periodisasi dari sumber rujukan yang user tunjuk. Jangan biarkan agen pembangun memilih periodisasi sendiri tanpa mencatat sumbernya.

---

## 11. Hub dan konsep awal — antrean riset, BUKAN entri terverifikasi

Daftar ini adalah **antrean riset Batch 1–3**, bukan halaman yang sudah jadi dan bukan klaim bahwa semua topik di bawah ini pasti lolos filter §9. Setiap topik tetap harus lewat verifikasi sumber, dedup, dan keputusan hub vs milestone (§8) sebelum ditulis.

### Batch 1 — fondasi (bangun dulu, karena semua hub lain merujuk ke sini)

- Hub induk: Orde Baru (1966–1998) — peta isi + periodisasi + jalur baca.
- Konsep: Dwifungsi ABRI; Demokrasi Pancasila; Trilogi Pembangunan; Stabilitas Nasional.
- Hub: Transisi 1965–1967 (Supersemar sebagai milestone di dalamnya, bukan halaman lepas tanpa hub).
- Hub: Pemilu-pemilu Orde Baru (sebagai satu hub living document, bukan satu halaman per pemilu kecuali ada milestone yang memenuhi §8).
- Aktor: Soeharto (ringkas, sistemik — tautkan ke wiki Soeharto bila perlu, jangan duplikasi biografi).

### Batch 2 — ekonomi dan kekuasaan

- Hub: Ekonomi Orde Baru — Repelita, pembangunan, dan peran negara (dipecah per sub-hub bila materi cukup: konglomerat, BUMN, utang luar negeri).
- Hub: Peristiwa Malari 1974 (sebagai hub/milestone sesuai §8, dengan kronologi dan konsekuensi kebijakan yang terdokumentasi).
- Konsep: Floating Mass; KKN (korupsi, kolusi, nepotisme) sebagai istilah sejarah — definisikan dari pemakaian sumber, bukan dari opini.
- Lembaga: Kopkamtib, Bakin, dan lembaga keamanan kunci lainnya (satu halaman per lembaga, bukan satu halaman gabungan yang kabur).

### Batch 3 — penindakan, kehidupan, dan akhir rezim

- Hub: Kasus-kasus penindakan yang terdokumentasi kuat (misalnya Tanjung Priok 1984, Kedung Ombo, dan kasus lain yang lolos filter — pilih berdasarkan kekuatan sumber, bukan berdasarkan viralitas).
- Hub: Kehidupan rakyat — desa, buruh, tani, pendidikan, transmigrasi (pecah per sub-hub bila materi cukup).
- Hub: Krisis moneter 1997–1998 → Reformasi Mei 1998 (dua hub yang saling bertaut, atau satu hub dengan kronologi panjang — diputuskan di §8 saat materi terkumpul; jangan diputuskan di awal tanpa melihat materi).
- Konsep lanjutan: hanya yang dipakai ≥ 2 halaman (lihat §7.5).

### Aturan antrean

- Jangan mengerjakan Batch 2–3 sebelum Batch 1 terverifikasi dan di-merge. Satu fase tuntas sebelum berikutnya — ini pelajaran tata kelola irawiki, bukan sekadar urutan.
- Setiap batch dilaporkan dengan: halaman dibuat, halaman ditahan + alasan, daftar tersingkir (§9.3), dan tautan PR.

---

## 12. Jalur baca dan sintesis

- Cross-link terkurasi antar-hub dalam tiap kategori/benang (§10.3) + bagian "Baca juga / jalur pemahaman" di hub utama.
- Analisis sintesis hanya memakai fakta yang sudah ada di halaman wiki + sumber terverifikasi, tanpa fakta karangan. Contoh sintesis yang boleh dibuat **setelah** hub-hub dasar ada (bukan di awal):
  - Bagaimana Dwifungsi ABRI bekerja lewat lembaga, regulasi, dan kasus — menautkan konsep ke peristiwa dan lembaga.
  - Bagaimana krisis ekonomi 1997–1998 berubah menjadi krisis politik — menautkan hub ekonomi ke hub reformasi dengan rantai yang terdokumentasi, bukan dengan lompatan kausal.
- Kriteria lolos sintesis: tidak ada klaim kausal tanpa mata rantai tertelusur; klaim pihak tetap diberi label pihak; target/rencana tidak ditulis sebagai capaian.

---

## 13. Mutu dan verifikasi — checklist per halaman/entri

Sebelum PR dibuka, pemeriksa (agen pembangun, lalu user saat membaca PR) memeriksa:

- [ ] Setiap angka/bullet penting punya sumber yang dibuka (bukan sekadar "katanya ada di buku X").
- [ ] Tanggal dalam format `YYYY-MM-DD` di heading kronologi; tanggal di body konsisten dengan heading.
- [ ] Nama aktor, perbuatan, dan tanggal terverifikasi (§9.3) — bukan hanya tipe peristiwa yang lolos.
- [ ] Klaim pihak diberi label pihak; interpretasi diberi label interpretasi dan tidak bercampur dengan fakta hub.
- [ ] Target/rencana dibedakan dari capaian; klaim pemerintah/pejabat ditulis sebagai klaim, bukan sebagai hasil terverifikasi, kecuali ada bukti realisasi independen.
- [ ] Kausalitas tertelusur: "X menyebabkan Y" hanya bila ada mata rantai sumber, bukan korelasi waktu semata.
- [ ] Single-source detail diberi atribusi ke outlet/lembaga itu.
- [ ] Catatan presisi memuat: yang belum terverifikasi, koreksi atas klaim beredar, perbedaan versi sumber, dan yang sengaja tidak dimasukkan + alasan.
- [ ] Wikilink tidak rusak; alias tidak menimbulkan halaman duplikat; halaman ambigu dikembalikan sebagai candidates, bukan ditebak.
- [ ] Frontmatter lengkap (§5), tag dari daftar canonical, kategori tepat satu + tambahan bila perlu.
- [ ] Bahasa Indonesia hidup: tidak ada kalque Inggris yang kentara, istilah dijelaskan saat pertama muncul, tidak ada kalimat generik AI yang bisa ditempel ke topik apa pun.

**Khusus bahan sejarah:** bedakan sumber primer (naskah regulasi, arsip resmi, data statistik resmi, dokumen pengadilan) dari sumber sekunder (buku sejarah, jurnal, media kredibel) dan dari memoar/kesaksian (klaim pihak sampai terkonfirmasi). Hierarki ini ditulis di `## Sumber` atau `## Catatan presisi`, bukan disembunyikan.

---

## 14. Lapisan LLM dan SEO — DIPINJAM dari fondasi teknis irawiki (20 Oktober 2026)

Fondasi ini di irawiki sudah selesai dan terbukti; jangan dibangun ulang dari nol, tapi jangan juga dianggap otomatis jalan di server baru — semua poin di bawah harus diverifikasi live di domain baru.

- `robots.txt`: crawler AI terbuka penuh dan eksplisit (bukan sekadar "allow all" yang ambigu).
- `llms.txt` + `llms-full.txt`: struktur situs + kategori (§10) + daftar hub utama, agar LLM bisa mengutip dengan benar.
- Meta description per halaman (dari frontmatter `description`), JSON-LD `datePublished`/`dateModified`, `og:type: article`.
- Sitemap terdaftar di Google Search Console; soft-404 dibereskan (halaman tidak ada mengembalikan 404 yang benar, bukan halaman kosong berkode 200).
- Normalisasi tag (lihat §5.3) sebelum mengklaim SEO beres.
- Log/referrer AI (ChatGPT, Perplexity, Copilot) dan Search Console dipakai untuk iterasi bulanan — bukan untuk menambah fase baru tanpa data.

---

## 15. Alur kerja dan governance — semi-hands-off, DIPINJAM dan DIPERTAHANKAN

Rezim yang berlaku di irawiki sejak klarifikasi user 23 Oktober 2026, dan yang **direkomendasikan sama** untuk wiki Orde Baru (kecuali user memutuskan lain secara eksplisit):

1. **Otomatisasi berhenti di paket/branch siap.** Agen membuat branch + PR, lalu BERHENTI.
2. **User MEMBACA dulu, lalu merge MANUAL sendiri** (di irawiki: via GitHub mobile). Agen boleh diperintah membuat PR, tetapi user memilih TIDAK memakai automerge.
3. **Build Quartz + indexer hanya pasca-merge.** Watcher/pipeline TIDAK commit ke `main`, TIDAK rebuild, TIDAK menjalankan indexer sebelum merge.
4. **Tahap deploy pasca-merge (di awal run berikutnya):** cek apakah ada PR yang sudah di-merge sejak run terakhir tapi belum di-deploy (lacak dengan file state berisi hash commit `main` terakhir yang sudah di-build+index) → pull `main` → rebuild → indexer → verifikasi URL live tiap hub yang berubah → perbarui state → laporkan.
5. **PR ditutup tanpa merge = ditolak, bukan "belum jadi".** Jangan deploy, jangan injeksi ulang branch sumbernya, catat satu baris di laporan berikutnya.
6. **Pelajaran 31 Oktober – 1 November 2026 (wajib diingat agen pembangun):** PR yang tertutup tanpa merge **tidak membuktikan** isinya tidak ada di `main`. Di irawiki, peta Minggu 2 dan entri mutasi Kapolri sudah ada di `main` meski PR-nya tertutup tanpa merge. **Selalu cek `main` itu sendiri sebelum melaporkan apakah sesuatu live atau masih gated.** Status PR saja tidak cukup.
7. **Kendala teknis ≠ perdebatan kebijakan.** Konflik branch dan build gagal dilaporkan sebagai ERROR TEKNIS, bukan dipakai untuk menegosiasikan ulang governance.
8. **Laporan selalu eksplisit:** "Belum tayang — menunggu merge user" bila memang belum di-merge; "Live, terverifikasi di URL …" hanya bila URL live sudah dibuka dan entrinya tampil.

Untuk wiki Orde Baru, ganti nama branch sesuai kebutuhan, tapi pertahankan polanya:

- Branch konten: `konten/<slug>-<tanggal>` (misalnya `konten/hub-dwifungsi-abri-2026-11-05`).
- Branch watcher/pantauan (bila ada): `hermes/pantauan-<tanggal>` atau nama setara di server baru — yang penting polanya sama: branch kerja → PR → berhenti.
- Commit per batch kecil (±50 file untuk ekstraksi massal), satu commit per batch, pesan jelas, reversibel via git, tanpa force-push dan tanpa rewrite history.
- Jangan hapus prosa asli di body sebelum hasil ekstraksi diverifikasi.

---

## 16. Urutan pembangunan untuk agen di server lain

### Fase 0 — Fondasi server dan repo (sekali, sebelum konten)

- [ ] Catat spesifikasi server (§3.5), buat repo git terpisah, struktur folder §4, Quartz + nginx menyala dengan halaman index kosong yang benar.
- [ ] Tentukan domain, pipeline deploy, dan akun GitHub **[KEPUTUSAN USER]**.
- [ ] Definisi selesai: repo bisa di-clone, build Quartz sukses dari repo kosong/awal, URL index bisa dibuka.

### Fase 1 — Skema dan ekstraksi (bekukan kontrak dulu)

- [ ] Bekukan frontmatter §5, daftar predikat §6, daftar tag canonical awal, dan template §7 di `docs/playbook-halaman-rujukan.md`.
- [ ] Kalau ada impor awal dari teknisi (§17): backfill `entity_type` dari folder, ekstraksi sumber dan relasi per batch kecil, tandai stub, masukkan low-confidence ke `proposals/`.
- [ ] Definisi selesai: YAML 0 error, 0 prosa body terhapus sebelum verifikasi, laporan per batch (diproses / berhasil / gagal / ragu-ragu).

### Fase 2 — Indexer SQLite + FTS5

- [ ] Bangun indexer Python (incremental via `content_hash`, timer 15 menit, WAL, VACUUM mingguan).
- [ ] Uji: backfill penuh, incremental (1 file berubah, sisanya tidak), 0 relasi yatim, 0 self-relation, 0 pelanggaran FK, 0 kebocoran stub ke prioritas FTS.
- [ ] Definisi selesai: `wiki_index.db` terbentuk, query uji lolos, timer dibuat dan di-enable hanya setelah user menyetujui.

### Fase 3 — Perbaikan/pembangunan MCP

- [ ] Implementasikan kontrak §3.3 (12 tools, FTS5, get_relations, get_entity dengan candidates, relations_between, timeline, save_draft saja sebagai jalur tulis).
- [ ] Uji ambiguitas alias (first-wins yang deterministik, rebuild konsisten — pelajaran bug irawiki: `ON CONFLICT DO UPDATE` yang non-deterministik harus diperbaiki, bukan dibiarkan).
- [ ] Definisi selesai: uvicorn sehat, semua tool membaca dari `wiki_index.db`, laporan tool final dicatat.

### Fase 4 — Konten seed + fondasi LLM/SEO

- [ ] Tulis 5 halaman pilot Batch 1 (§11) sesuai template §7, lewat PR + merge manual user.
- [ ] Terapkan taksonomi §10 (6 halaman arsip kategori + index "Mulai dari Sini!" + "Baru Update" + `llms.txt`).
- [ ] Terapkan fondasi §14, verifikasi live: 6 URL kategori → 200 dengan judul/deskriptor benar, sitemap bertambah, build sukses, query MCP hijau, tidak ada wikilink rusak baru.
- [ ] Definisi selesai: 5 halaman pilot live + terverifikasi, bukan sekadar "PR dibuka".

### Fase 5 — Benang, jalur baca, dan iterasi

- [ ] Cross-link terkurasi (§12), 1–2 analisis sintesis **setelah** hub dasar ada.
- [ ] Batch 2, lalu Batch 3 (§11), masing-masing lewat PR + merge manual.
- [ ] Pengukuran berkala (Search Console, uji sitasi LLM, log referrer AI) menentukan prioritas berikutnya. Tanpa data ini, jangan menambah fase baru.
- [ ] Hugo hanya bila pemicu §3.4 tercapai.

**Stop gate di setiap fase:** laporan → verifikasi user → keputusan lanjut. Jangan melompati fase karena "tanggung".

---

## 17. Spesifikasi serah terima dari agen teknisi (pengunduh data)

Teknisi **tidak** menulis halaman wiki. Teknisi menyerahkan paket data yang bisa langsung dipakai penulis/verifikator tanpa harus mengunduh ulang atau menebak sumbernya.

### 17.1 Struktur paket per batch

```
data-teknisi/
└── <tanggal>-<slug-batch>/
    ├── MANIFEST.md          # daftar isi batch + ringkasan (lihat Lampiran B)
    ├── kandidat-url.md      # daftar URL kandidat, maks 10–15 per hub/gap (pola riset irawiki)
    ├── sumber/
    │   ├── primer/          # naskah regulasi, arsip resmi, data statistik resmi (bila lisensinya memungkinkan)
    │   ├── sekunder/        # buku/jurnal/media kredibel (metadata + kutipan pendek, bukan salinan penuh bila berhak cipta)
    │   └── kesaksian/       # memoar/wawancara (ditandai jelas sebagai klaim pihak)
    └── catatan-teknisi.md   # apa yang dicari, apa yang tidak ditemukan, dan apa yang diragukan
```

### 17.2 Yang wajib ada di setiap item data

- Judul asli, penerbit/lembaga, tanggal terbit, tanggal akses, URL lengkap (jangan dipendekkan, jangan ditebak).
- Tipe sumber: primer / sekunder / kesaksian — dan, untuk regulasi: nomor, tahun, lembaga penerbit.
- Hub/gap yang dituju (misalnya: "untuk hub Dwifungsi ABRI, bagian dasar hukum").
- Status verifikasi awal teknisi: "sudah dibuka dan isinya cocok dengan judul" vs "hanya dari judul/snippet, belum dibuka penuh" — bedakan jujur, jangan disamakan.
- Bahasa dan format file (PDF, HTML, arsip gambar) + catatan OCR bila hasil pindaian sulit dibaca.

### 17.3 Yang dilarang

- Mengirim dump mentah tanpa manifest (ratusan file tanpa daftar isi = tidak bisa dipakai).
- Menyalin buku/jurnal berhak cipta secara penuh sebagai "data". Yang dikirim adalah metadata + tautan + kutipan pendek untuk verifikasi, kecuali sumbernya domain publik atau lisensi terbuka.
- Menggabungkan daftar dari otoritas berbeda menjadi satu daftar (§6).
- Menulis kesimpulan sejarah sendiri di `catatan-teknisi.md` seolah-olah fakta. Catatan teknisi berisi **apa yang ditemukan dan apa yang belum**, bukan tafsir.
- Mengirim URL yang belum dibuka sebagai "sumber terverifikasi". URL yang belum dibuka ditulis sebagai kandidat, bukan sumber.

### 17.4 Prioritas unduhan (sesuai Batch 1 dulu)

1. Naskah regulasi dan dokumen resmi yang menjadi dasar hub Batch 1 (Tap MPR, UU, Keppres terkait transisi dan Dwifungsi ABRI — nomor dan tahun harus dari naskah, bukan dari ingatan).
2. Data statistik resmi dan arsip yang bisa diakses publik untuk hub ekonomi Batch 2.
3. Sumber sekunder kredibel (buku sejarah akademik, jurnal, media arsip) untuk Batch 1–2, dengan metadata lengkap.
4. Memoar/kesaksian hanya sebagai pelengkap yang ditandai klaim pihak, bukan sebagai fondasi hub.

### 17.5 Serah terima dan dedup

- Setiap batch teknisi dilaporkan satu baris per item: MASUK (untuk hub apa) / DUPLIKAT (sudah ada di hub mana) / DITAHAN (alasan).
- Jangan mengulangi hub/gap yang sama dalam 7 hari tanpa alasan (pola riset irawiki) — kecuali user meminta pengulangan eksplisit.
- File paket teknisi **tidak diindeks sebagai halaman wiki**. Folder `data-teknisi/` dikecualikan dari indexer dan dari sitemap.

---

## 18. Checklist serah terima agen pembangun ke user

Agen pembangun menyerahkan laporan yang berisi, tanpa kecuali:

- [ ] URL repo, branch, dan PR per fase/batch.
- [ ] Spesifikasi server (§3.5) dan hasil uji build/indexer.
- [ ] Daftar halaman live (URL + tanggal merge) vs halaman yang masih di PR (URL PR + status "belum live").
- [ ] Hasil cek `main` itu sendiri (§15.6), bukan hanya status PR.
- [ ] Daftar halaman ditahan + daftar tersingkir + alasan (§9.3).
- [ ] Daftar utang: sumber prosa tanpa URL, stub yang belum dikembangkan, alias ambigu, duplikat judul yang belum diputuskan.
- [ ] Bukti verifikasi §14 (robots, llms.txt, sitemap, JSON-LD) di domain baru.
- [ ] Kalimat eksplisit di akhir laporan: mana yang **sudah live dan terverifikasi**, mana yang **siap di GitHub dan menunggu merge manual user**.

---

## 19. Yang secara eksplisit TIDAK dikerjakan

- Mengejar topik viral tanpa kaitan ke kategori/benang (§10).
- Halaman tanpa sumber terverifikasi.
- Section relevansi anak muda tanpa rantai mekanisme.
- Retrofit massal tanpa pilot dan persetujuan user.
- Automerge, write langsung ke `main`, dan build/indexer sebelum merge.
- Embedding/vector DB, migrasi Hugo, dan biaya API baru tanpa pemicu/keputusan (§3.4).
- Mengarang URL, nama, nomor regulasi, atau fakta demi mengisi template.
- Menggabungkan halaman ambigu/duplikat tanpa review editorial.
- Menyalin isi pakharto.my.id atau irawiki bulat-bulat tanpa verifikasi ulang.
- Memakai materi tersingkir sebagai konten lain tanpa keputusan format dari user (§9.3).

---

## Lampiran A — Kerangka hub (skeleton, BUKAN isi jadi)

Kerangka ini untuk disalin agen pembangun sebagai titik awal file baru. Isi bullet di bawah adalah **placeholder** — ganti dengan fakta terverifikasi + sumber sebelum PR dibuka. Jangan membuka PR dengan placeholder masih terisi.

```markdown
---
title: "[Judul Hub]"
description: "[1–2 kalimat: definisi + status/warisan.]"
date: [YYYY-MM-DD atau rentang yang terdokumentasi]
updated: [YYYY-MM-DD]
last_updated: "[YYYY-MM-DD]"
entity_type: topik
entity_id: "[slug-hub]"
aliases:
  - "[Varian nama 1]"
tags: [orde-baru]
kategori: [slug kategori §10]
kategori_tambahan: []
risiko_editorial: sedang
sumber:
  - url: https://...
    judul: "..."
    tanggal: YYYY-MM-DD
relasi:
  - predikat: terkait_dengan
    objek: "[Nama Halaman]"
    sumber: https://...
---

# [Judul Hub]

> **Ringkasan:** [2–3 kalimat.]

## Apa relevansinya dengan anak muda?
[1–3 paragraf dari fakta halaman ini, lewat rantai mekanisme. Bila belum ada data: tulis "belum terverifikasi" dan biarkan pendek.]

## Fakta kunci
| Tanggal | Kejadian | Status / Dasar |
|---|---|---|
| YYYY-MM-DD | [Kejadian terverifikasi] | [Status + sumber] |

## Kronologi

### YYYY-MM-DD
- [Bullet faktual 1 — sumber di ## Sumber.]
- [Bullet faktual 2.]

## Aktor yang terlibat
- [[Nama Aktor]] — [peran 1 kalimat.]

## Sumber
- **[Lembaga/Media] ([tanggal]):** [judul + URL.]

## Catatan presisi
- [Klaim belum terverifikasi / perbedaan versi sumber / yang sengaja tidak dimasukkan + alasan.]
```

---

## Lampiran B — Contoh MANIFEST teknisi (satu batch)

```markdown
# MANIFEST — 2026-11-05-dwifungsi-abri

Tujuan batch: Hub Dwifungsi ABRI, bagian dasar hukum dan praktik kelembagaan.
Jumlah item: 12 (10 sudah dibuka penuh, 2 hanya kandidat dari judul).

## Sudah dibuka penuh
1. [Judul] — [Lembaga/Penerbit], [tanggal terbit], diakses 2026-11-05 — URL: …
   Tipe: primer (Tap MPR No. …/Tahun … — nomor dari naskah, bukan ingatan).
   Untuk: hub Dwifungsi ABRI, bagian dasar hukum.
2. …

## Kandidat (belum dibuka penuh — BUKAN sumber terverifikasi)
1. [Judul] — URL: … — Alasan kandidat: …
   Untuk: …

## Tidak ditemukan
- Naskah … dicari di … pada 2026-11-05, tidak ditemukan versi publiknya.
  Tindak lanjut yang diusulkan: …

## Duplikat / ditahan
- [Judul/URL] — duplikat dari item … / ditahan karena …

## Catatan teknisi
- [Apa yang dicari, apa yang diragukan. Tanpa tafsir sejarah.]
```

---

## Lampiran C — Keputusan yang masih harus dibuat user

Agen pembangun **berhenti** di titik-titik ini sampai user menjawab. Jangan menebak jawaban.

1. **Domain dan repo:** nama domain wiki Orde Baru, nama repo GitHub, dan pipeline deploy (apakah meniru irawiki atau tidak).
2. **Spesifikasi server baru:** RAM/vCPU/disk/swap, apakah memakai Docker atau tidak.
3. **Nama tampil kategori final (§10.2):** apakah 6 usulan dipakai apa adanya, diubah, atau diganti.
4. **Periodisasi final (§10.4):** apakah kerangka 6 periode dipakai, diubah, atau diganti dengan sumber rujukan yang user tunjuk.
5. **Hub induk:** apakah "Orde Baru (1966–1998)" dipakai sebagai peta isi, atau user ingin hub induk lain.
6. **Hubungan dengan pakharto.my.id:** tautan seperti apa yang diinginkan (sekadar wikilink, atau halaman penghubung eksplisit).
7. **Prioritas Batch 1:** apakah urutan §11 dipakai, atau ada hub yang harus didahulukan karena data teknisi sudah tersedia.
8. **Governance:** apakah rezim semi-hands-off §15 dipakai penuh untuk wiki baru (PR + merge manual user, tanpa automerge), atau ada penyesuaian.

---

## Sumber pola (untuk audit, bukan untuk disalin mentah)

- `blueprint-wiki-iraamalia.md` (5 Oktober 2026, revisi v2 + hasil Fase 1–3) — arsitektur SQLite/MCP.
- `kebijakan-granularitas-halaman-wiki.md` (8 Oktober 2026) — satu topik = satu hub, kriteria milestone.
- `brief-playbook-halaman-rujukan-hermes.md` (20 Oktober 2026) — template Halaman Rujukan.
- `rancangan-pengembangan-wiki-iraamalia.md` (21 Oktober 2026, + taksonomi 22 Oktober 2026) — benang, poros, taksonomi dua lapis.
- `brief-koreksi-watcher-pantauan-hermes.md` (23 Oktober 2026) — PR + deploy pasca-merge.
- Skill `local_wiki_bermakna_filter` — uji mengubah sesuatu, dedup, daftar tersingkir.
- Pelajaran 31 Oktober – 1 November 2026: cek `main` itu sendiri, bukan hanya status PR, sebelum mengklaim live/gated.

*Dokumen ini disusun agen konten dari pengalaman langsung membangun irawiki, untuk diteruskan user ke agen pembangun di server lain. Semua usulan yang belum diputuskan user ditandai sebagai usulan/draf di dalam dokumen, bukan sebagai keputusan.*
