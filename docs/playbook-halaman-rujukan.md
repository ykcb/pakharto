# Playbook Halaman Rujukan — Panduan Operasional Konten

Dokumen ini adalah pedoman operasional pembuatan, penulisan, dan verifikasi halaman di Wiki Orde Baru. Berlaku sejak halaman pertama dan tidak boleh diubah tanpa tinjauan tata kelola.

---

## 1. Skema Frontmatter (Kontrak Data)

Semua halaman konten wajib menggunakan struktur YAML frontmatter berikut:

```yaml
---
title: "Judul Halaman Baku"
description: "Penjelasan ringkas 1–2 kalimat: definisi + signifikansi sejarah."
date: 1966-03-11 # Tanggal kejadian/berlakunya konsep (YYYY-MM-DD)
updated: 2026-11-02 # Tanggal revisi artikel (YYYY-MM-DD)
last_updated: "2026-11-02"
entity_type: topik # aktor | peristiwa | organisasi | regulasi | lokasi | topik | pelajaran
entity_id: "slug-halaman-baku"
aliases:
  - "Varian Nama 1"
  - "Singkatan"
tags: [konsep, orde-baru] # HANYA dari daftar canonical tags
kategori: konsep # OPSIONAL, label topik internal — 6 halaman kategori dihapus 4 Nov 2026; navigasi pembaca lewat halaman hub
kategori_tambahan: [] # Opsional
risiko_editorial: sedang # rendah | sedang | tinggi
status: "" # Kosong, atau "stub" jika isi < 200 karakter
confidence: "high" # low | medium | high
sumber:
  - url: https://contoh-sumber-primer.go.id/dokumen.pdf
    judul: "Naskah Resmi Dokumen Sejarah"
    tanggal: 1966-03-11
relasi:
  - predikat: terkait_dengan # HANYA dari daftar 8 predikat terkontrol
    objek: "Soeharto"
    sumber: https://contoh-sumber-primer.go.id/dokumen.pdf # WAJIB per relasi
---
```

---

## 2. Predikat Relasi Terkontrol (Daftar Tertutup)

Hanya 8 predikat berikut yang diizinkan dalam field `relasi`:

1. `terlibat_dalam` — Keikutsertaan aktor/organisasi dalam peristiwa.
2. `menunjuk` — Penugasan, pengangkatan pejabat/menteri secara resmi.
3. `didukung_oleh` — Basis aliansi atau dukungan politik/militer terdokumentasi.
4. `menentang` — Oposisi, protes terbuka, kritik resmi, atau perlawanan.
5. `anggota_dari` — Keanggotaan aktor dalam kabinet, komite, atau partai/organisasi.
6. `memimpin` — Komando langsung, posisi ketua, menteri, atau presiden.
7. `terkait_dengan` — Kaitan faktual terdokumentasi yang belum memenuhi predikat spesifik di atas.
8. `menyebut` — Rujukan formal dalam pidato resmi atau dokumen negara.

*Catatan:* Setiap entri relasi wajib memiliki URL sumber primer/sekunder kredibel. Relasi tanpa sumber dilarang masuk frontmatter final dan wajib dimasukkan ke `proposals/`.

---

## 3. Template Halaman (Urutan Baku)

### 3.1 Hub (Living Document — Format Default)
- `> **Ringkasan:**` (2–3 kalimat)
- `## Apa pelajaran yang bisa kita ambil darinya?` (1–3 paragraf berbasis mekanisme kausal faktual)
- `## Fakta kunci` (Tabel kronologi ringkas / data pokok)
- `## Kronologi` (Subheading per tanggal `### YYYY-MM-DD`, bullet objektif)
- `## Aktor yang terlibat` (`[[Nama Aktor]] — peran 1 kalimat`)
- `## Sumber` (Tautan resmi berlabel media/lembaga + tanggal akses)
- `## Catatan presisi` (Perbedaan versi sumber, data belum terverifikasi, fakta yang sengaja disisihkan beserta alasannya)

### 3.2 Halaman Peristiwa (Milestone)
- Format sama dengan Hub, tanpa tabel fakta kunci jika tidak diperlukan.
- **Wajib mencantumkan taut balik:** `Bagian dari: [[Nama Hub Induk]]`.

### 3.3 Halaman Aktor
1. Definisi 1 kalimat ("X adalah...").
2. Infobox tabel (Nama, Masa Hidup, Jabatan Orde Baru, Afiliasi, Rekam Jejak).
3. `## Apa pelajaran yang bisa kita ambil darinya?`
4. Rekam jejak bertanggal.
5. Relasi wikilink (`[[Halaman Terkait]]`).
6. Sumber berlabel.

### 3.4 Halaman Konsep
1. Definisi 1–2 kalimat yang padat.
2. Dasar hukum / kemunculan historis.
3. Cara kerja konsep dalam praktik nyata Orde Baru (tautkan peristiwa).
4. `## Apa pelajaran yang bisa kita ambil darinya?`
5. Halaman yang merujuk konsep ini.
6. Sumber + Catatan presisi.

### 3.5 Halaman Pelajaran (Track Pelajaran — pola tiga lapis)
- `> **Disclaimer:**` (blok baku di bawah — wajib verbatim di setiap halaman Pelajaran)
- `> **Ringkasan:**` (2–3 kalimat: praktik yang dipelajari + relevansi kini + catatan jujur batas data)
- `## 1. Fakta: praktik era Orde Baru` (pelembagaan, skala, **termasuk fakta kritis** yang wajib dicatat)
- `## 2. Fakta: data masa kini` (tabel indikator + angka + sumber; sitasi primer diutamakan)
- `## 3. Apa yang bisa dipelajari anak muda? (INFERENSI — bukan fakta)` (setiap butir dilabeli inferensi + menunjuk nomor fakta sumbernya)
- `## 4. Batas data` (apa yang TIDAK bisa disimpulkan: korelasi≠kausalitas, scope populasi, hipotesis belum diuji)
- `## Sumber` (sumber primer diutamakan; sekunder ditandai; belum terverifikasi ditandai [perlu sumber primer])
- `## Catatan presisi` (status verifikasi angka, definisi istilah)

**Teks disclaimer baku (wajib verbatim):**
> **Disclaimer:** Halaman ini bagian dari track **"Pelajaran"** Wiki Soeharto — menggali apa yang bisa dipelajari generasi kini dari era Orde Baru. Isinya disusun tiga lapis: **Fakta** (data terverifikasi dengan sumber), **Inferensi** (pelajaran yang ditarik tim kurasi — dilabeli eksplisit, bukan fakta), dan **Batas data** (apa yang tidak bisa disimpulkan dari data). Inferensi adalah tafsir tim kurasi internal, bukan konsensus akademik dan bukan sikap resmi wiki terhadap Orde Baru.

---

## 4. Filter Bermakna (Uji Perubahan Nyata)

Sebelum entri atau halaman ditulis, ajukan pertanyaan penyaring:
> *"Apakah kabar atau peristiwa ini secara nyata mengubah keadaan, status hukum, aturan yang berlaku, kepemilikan modal, atau susunan lembaga kenegaraan?"*

- **Lolos:** Terbitnya Tap MPR/UU/Keppres, pembentukan/pembubaran lembaga, hasil resmi pemilu, akuisisi modal besar, penetapan status hukum pengadilan, pelantikan/pemberhentian pejabat resmi.
- **Tidak Lolos (Tahan/Singkirkan):** Wacana opini, desakan politik yang belum terwujud, komentar analis, perang pernyataan pejabat, gosip politik tanpa bukti dokumen resmi.
