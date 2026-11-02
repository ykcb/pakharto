# Backlog — Impor awal `content/sources/`

**Tanggal:** 2026-11-02
**Status:** DIBERHENTIKAN — bukan diabaikan.

## Ringkasan
Folder `content/sources/soehartolibrary-*.md` berisi ±1.000 file hasil import otomatis dari `soehartolibrary.id`. File ini **tetap diindeks** sesuai keputusan user, tetapi frontmatter-nya menggunakan schema importer kustom, bukan schema canonical §5.

## Yang harus dilakukan (tidak sekarang)
- Migrasi batch kecil (±50 file) ke schema canonical: `title`, `description`, `date`, `updated`, `last_updated`, `entity_type`, `entity_id`, `aliases`, `tags` (dari daftar canonical), `kategori`, `risiko_editorial`, `status`, `confidence`, `sumber` (object), `relasi` (jika ada).
- Backfill `entity_type` dari folder → untuk `sources/` hasilnya kemungkinan `sumber` atau `topik`, tapi perlu diputuskan karena bukan folder entity_type wiki utama.
- File dengan `tanggal_subjek` kosong ditandai `sumber_status: prosa` dan masuk backlog verifikasi tanggal.
- Body < 200 karakter → `status: stub`; dicekulkah ke prioritas FTS.
- Relasi dari wikilink diekstrak per batch kecil, low-confidence → `proposals/`.

## Alasan di-hold
- Jangan mengganti 1.000 file sekaligus tanpa batch kecil + verifikasi.
- Jangan menghapus prosa asli sebelum verifikasi.
- Fase 1Batch 1 adalah 5 halaman wiki, bukan 1.000 file sumber.

## Catatan
User memutuskan `content/sources/` tetap diindeks, tidak dipindah ke `data-teknisi/`.
