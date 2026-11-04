# Panduan Sumber Primer untuk Tim Wiki — DRAF (untuk diskusi)

> Status: draf untuk didiskusikan user + tim kurasi. Belum final.

## 1. Hierarki sumber

1. **Primer** — dokumen negara (UU, Keppres, Inpres, Tap MPR), naskah pidato resmi, data statistik resmi (BPS, BI, Kemenkes), publikasi pemerintah, arsip soehartolibrary.id, buku karya pelaku sejarah.
2. **Sekunder kredibel** — jurnal akademik, buku sejarawan, laporan lembaga riset, liputan investigasi media bereputasi.
3. **Opini/publik** — artikel opini, blog, media sosial: hanya boleh dipakai sebagai *atribusi* ("menurut X"), tidak sebagai fakta.

## 2. Buku cetak: tiga lapis

Buku tidak direproduksi utuh ke wiki.

- **Lapis 1 — Raw source of truth.** File PDF / hasil OCR disimpan apa adanya sebagai arsip sumber. Tidak diedit, tidak diterbitkan sebagai artikel. Di sistem: masuk antrean file (`~/input-server/queue/files/`).
- **Lapis 2 — Kutipan terbatas.** Kutip seperlunya — satu-dua paragraf per klaim — dengan sitasi lengkap. Ini batas aman hak cipta.
- **Lapis 3 — Ringkasan per bagian.** Tulis ulang isi tiap bab/bagian dengan bahasa sendiri, lengkap dengan sitasi. Bukan parafrasa tipis (sekadar ganti kata), melainkan ringkasan substansi.

## 3. Format sitasi

- **Buku:** Nama Penulis. (Tahun). *Judul Buku*. Penerbit, Kota. hlm. xx–yy.
- **Dokumen/arsip:** Nama lembaga. (Tanggal). "Judul dokumen". Nomor dokumen bila ada.
- **Data statistik:** BPS. (Tahun). *Nama Publikasi* (No. Publikasi xxxxx.xxxxx). + URL bila daring.
- **Artikel daring:** Penulis. (Tanggal). "Judul". *Nama Media*. URL. (tanggal akses)

## 4. Batas hak cipta (aturan keras)

- Jangan mengunggah atau menyalin bab utuh / buku utuh yang masih beredar.
- Dokumen pemerintah dan publikasi resmi lama umumnya aman direproduksi.
- Bila ragu: ringkas, jangan salin.

## 5. Standar verifikasi angka & klaim

- Angka wajib dilacak ke publikasi primer (contoh: klaim "data BPS" → wajib ke publikasi bps.go.id, bukan via berita).
- Yang belum terverifikasi ditandai `[perlu sumber primer]` — boleh masuk draf, tidak boleh jadi dasar inferensi kuat.
- Klaim yang kontestabel (penilaian, tuduhan, interpretasi) wajib diatribusikan: "menurut X", bukan suara wiki.

## 6. Alur kerja tim

1. Siapkan bahan: link / upload file (pdf, docx, txt, md, html) / tempel teks via halaman `/input`.
2. Untuk buku: upload PDF/OCR sebagai raw (Lapis 1), lalu tulis kutipan + ringkasan per bagian (Lapis 2–3).
3. Setiap kiriman diproses menjadi draf (`proposals/`) berstatus low-confidence — wajib review kurator sebelum terbit.
4. Merge ke konten utama tetap manual.
