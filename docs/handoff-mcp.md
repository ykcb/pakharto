# Prompt Handoff — Wiki Soeharto (pakharto.my.id)

Kamu adalah agen pembangun yang melanjutkan pekerjaan Wiki Soeharto di repo `/home/ubuntu/quartz`, branch `main`. Live site: `https://pakharto.my.id`.

## Aturan tetap
- Paket free, jangan kerjakan terlalu banyak sekaligus dalam satu turn.
- `content/sources/` tetap diindeks (keputusan user).
- `public/` di-force-add karena di-gitignore Quartz.
- Schema frontmatter canonical §5 sudah dibeku di Fase 1; jangan ubah field seenaknya.
- Migrasi batch kecil (40 file/batch) dengan commit per batch.
- Konten editorial baru lewat PR + merge manual user. Batch migrasi data boleh commit langsung ke main dengan pesan batch yang jelas.
- Jangan enable automerge.
- Python interpreter untuk tools: `/usr/bin/python3` (memiliki `fastmcp`, `yaml`, `sqlite3`). Jangan gunakan venv Hermes untuk script repo.

## Status saat ini (per 2 Nov 2026)
- **Fase 0 + partial Fase 1 selesai.**
- **Batch migrasi `content/sources/soehartolibrary-*.md`**: 2,697 file sudah di-migrasi ke schema canonical §5 dalam 67 batch (batch 1–66 = 40 file, batch 67 = 17 file sisa). Commit terakhir batch sources: `08f5d99c`.
- **Batch 1 hub conceptual pages selesai** (commit `d741f080`):
  - `content/hub/orde-baru.md`
  - `content/hub/pemilu-orde-baru.md`
  - `content/peristiwa/transisi-1965-1967.md`
  - `content/konsep/dwifungsi-abri.md`
  - `content/konsep/demokrasi-pancasila.md`
  - `content/konsep/trilogi-pembangunan.md`
  - `content/konsep/stabilitas-nasional.md`
  - `content/aktor/soeharto.md` diperkaya relasi sistemik
- **Indexer SQLite FTS5 sudah dibuat** (commit `7924e6c2`, di-rebase ke `8c88497f`):
  - Script: `scripts/indexer/build-fts5.py`
  - DB: `scripts/indexer/wiki-fts5.db` (di-`.gitignore`)
  - Verifikasi: 2,714 file masuk, 0 error
  - Tabel: `pages` (FTS5), `entities`, `relations`, `meta`
  - Kolom FTS: title, description, body; kolom lain: entity_type, entity_id, kategori, tags, content_hash
  - Relasi diekstrak dari frontmatter `relasi[]` + wikilink `[[Target]]` di body
  - Tokenizer: `porter unicode61`

## Yang BELUM dikerjakan
1. **MCP server** — 12 tools sesuai kontrak §3.3 cetak biru:
   - `search` → FTS5 BM25 berbobot (judul ×3, heading ×2) + ekspansi alias
   - `get_entity` → baca entities + relasi + sumber; nama ambigu → kembalikan `candidates[]`, jangan menebak satu halaman
   - `get_relations` → relations table, depth N-hop, filter origin (frontmatter vs wikilink)
   - `relations_between` → BFS relations table
   - `timeline` → query relations + pages, filter tipe peristiwa, urut tanggal
   - `get_page`, `stats`
   - `save_draft` → satu-satunya jalur tulis, ke `proposals/` untuk review
   - Kontrak 12 tools irawiki dipakai spesifikasi; lihat referensi di bawah
2. **Sitemap + JSON-LD + llms-full.txt**
3. **8 poin [KEPUTUSAN USER]** di Lampiran C cetak biru — belum dijawab
4. **Batch 2 & 3 konten** (setelah Batch 1 terverifikasi)

## Langkah berikutnya yang disarankan
1. **MCP server** — bangun `wiki_query.py` + wrapper FastMCP/uvicorn di `scripts/mcp/`
2. Verifikasi query MCP hijau (search, get_entity, get_relations, relations_between, timeline, get_page, stats)
3. Sitemap + JSON-LD + llms-full.txt
4. Tanyakan 8 poin keputusan user di Lampiran C

## Referensi teknis
- Schema DB: FTS5 `pages` + `entities` + `relations` + `meta` (lihat `scripts/indexer/build-fts5.py` terbaru)
- DB path: `scripts/indexer/wiki-fts5.db`
- Server specs: 2 vCPU, ~2 GB RAM (sama dengan irawiki)
- Frontmatter schema: lihat `content/aktor/soeharto.md` atau `content/hub/orde-baru.md` sebagai contoh
- Predikat terkontrol: `terlibat_dalam`, `menunjuk`, `didukung_oleh`, `menentang`, `anggota_dari`, `memimpin`, `terkait_dengan`, `menyebut`
- Kategori canonical 6 slug: `kekuasaan-dan-legitimasi`, `ekonomi-dan-pembangunan`, `keamanan-dan-keadilan`, `kesejahteraan-dan-kemasyarakatan`, `budaya-dan-ideologi`, `transisi-dan-konstitusi`
- Jangan inventarisasi kategori baru untuk hub/concept pages; pakai yang ada.

## Catatan penting
- Jangan pakai `Path.glob('**/*.md')` untuk rekursi; pakai `Path.rglob('*.md')`.
- `_index.md` dan `index.md` di-skip dari indexer.
- `public/` di-gitignore Quartz; pakai `git add -f public/<file>`.
- Setiap kali push: `git fetch origin && git rebase origin/main && git push origin main` (remote bisa advance kapan saja).
- File `cetak-biru-wiki-orde-baru.md` terletak di `/home/ubuntu/.hermes/cache/documents/doc_09444ab6facd_cetak-biru-wiki-orde-baru.md`.

## Pertemuan singkat
Agen sebelumnya sudah menyelesaikan:
- Semua 2,697 file `soehartolibrary-*.md` dimigrasi ke schema canonical §5
- 7 halaman Batch 1 dibuat + 1 aktor diperkaya
- Indexer SQLite FTS5 + entities + relations siap dipakai

Sekarang giliran **MCP server**. Lanjutkan dari situ.
