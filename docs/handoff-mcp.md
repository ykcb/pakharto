# Prompt Handoff — Wiki Soeharto (pakharto.my.id)

Kamu adalah agen pembangun yang melanjutkan pekerjaan Wiki Soeharto di repo `/home/ubuntu/quartz`, branch `main`. Live site: `https://pakharto.my.id`.

## Aturan tetap
- Paket free, jangan kerjakan terlalu banyak sekaligus dalam satu turn.
- `content/sources/` SUDAH DIHAPUS atas perintah tegas user (6 Nov 2026, commit `fe232b49`) — arsip verbatim 2.697 halaman. JANGAN dipulihkan, JANGAN diindeks ulang. File tetap ada di riwayat git bila user meminta.
- `public/` adalah build output dan TIDAK dilacak git sejak batch 2 (7 Nov 2026). JANGAN `git add -f public/` — deploy membangunnya dari `content/` lewat `deploy.sh`.
- Halaman `/kategori/` SUDAH DIHAPUS (4 Nov 2026, commit `073e1384`). `kategori:` di frontmatter kini hanya label topik internal opsional; navigasi pembaca lewat halaman hub. JANGAN buat ulang halaman kategori.
- Schema frontmatter canonical §5 sudah dibeku di Fase 1; jangan ubah field seenaknya. PENGECUALIAN TERTUNDA (batch 3 audit 7 Nov 2026): sebagian halaman memakai relasi `type/target`, bukan `predikat/objek` — migrasi skema relasi belum diputuskan.
- Konten editorial baru lewat PR + merge manual user. Batch migrasi data boleh commit langsung ke main dengan pesan batch yang jelas.
- Jangan enable automerge.
- Python interpreter untuk tools: `/usr/bin/python3` (memiliki `fastmcp`, `yaml`, `sqlite3`). Jangan gunakan venv Hermes untuk script repo. Dependensi dipin di `scripts/requirements.txt`.
- Path repo/DB configurable via env `PAKHARTO_REPO` / `PAKHARTO_DB` (default `/home/ubuntu/quartz`).

## Status saat ini (per 7 Nov 2026, setelah batch 1 + batch 2 audit ChatGPT)
- **Kode tersedia:** MCP server 12 tools di `scripts/mcp/server.py` + `scripts/mcp/wiki_query.py` (FastMCP 4.1.5, stdio).
- **Database berhasil dibangun:** `scripts/indexer/wiki-fts5.db` (di-`.gitignore`) dibangun ATOMIK oleh `scripts/indexer/build-fts5.py` (DB sementara → verifikasi tabel + jumlah halaman → `os.replace`). DIBANGUN ULANG OTOMATIS di setiap `deploy.sh` (langkah 2/6). Isi per rebuild terakhir: ~1.129 halaman (1.135 Markdown minus file `index.md`/`_index.md` yang di-skip), tabel `pages` (FTS5), `entities`, `relations`, `meta`.
- **Test lulus:** `python3 scripts/mcp/server.py --test` — 12 tools dengan assertion nyata (search > 0 hasil, `relations_between` soeharto→Kopkamtib ketemu, `get_page` menolak traversal, `save_draft` anti-timpa + cleanup draft uji). Dijalankan otomatis di `deploy.sh` (langkah 3/6) dan di CI.
- **Service berjalan:** TIDAK ada service HTTP publik. MCP dipakai via stdio oleh Hermes dan oleh agen ini (konektor custom, SSH stdio, allowlist 12 tools). Mode streamable-http pernah terverifikasi handshake tapi TIDAK dipakai.
- **Endpoint dapat diakses:** stdio saja. Satu-satunya jalur tulis: `save_draft` → `proposals/<slug>.md` (frontmatter via `yaml.safe_dump`; slug yang sama jadi versi bertimestamp, tidak menimpa).
- **Deployment live tervalidasi:** `bash ~/quartz/deploy.sh` — 6 langkah: (1) generate `llms.txt`/`llms-full.txt` (fail-fast bila halaman CORE hilang), (2) rebuild FTS5, (3) MCP smoke test, (4) `npx quartz build` + guard (HTML hasil build harus ≥ jumlah Markdown), (5) copy assets, (6) `rsync --delete` ke `/var/www/pakharto.my.id/public/`. Terakhir sukses 7 Nov 2026 (commit batch 1 `6e3d9217`).
- **CI:** `.github/workflows/pakharto-ci.yml` (khusus repo ini, branch `main`) menguji generator llms, build FTS5, dan self-test MCP. Workflow upstream Quartz (`ci.yaml`) TIDAK berlaku di repo ini (hanya jalan untuk `jackyzha0/quartz` branch `v5`).
- **Koreksi faktual batch 1 (7 Nov 2026):** kronologi Soeharto (Supersemar 11 Mar 1966, Pejabat Presiden 12 Mar 1967, Presiden 27 Mar 1968) dan tabel Pemilu Orde Baru (6 pemilu, angka KPU 2 desimal) — live terverifikasi.
- **Taksonomi kanonikal (disamakan batch 2):** 6 slug dari frontmatter konten — `kekuasaan-dan-legitimasi`, `ekonomi-dan-kepemilikan`, `keamanan-dan-kebebasan`, `pembangunan-dan-kehidupan`, `krisis-dan-reformasi`, `konsep`. Dipakai serentak oleh `CANONICAL_CATEGORIES` di `wiki_query.py`, header `llms.txt`, dan generator `build_llms_txt.py`. Jangan inventarisasi slug baru tanpa mengubah ketiganya.

## Yang BELUM dikerjakan (batch 3 audit 7 Nov 2026)
1. **Skema relasi:** migrasikan 9 entri `type/target` ke `predikat/objek`; simpan target relasi sebagai `entity_id` kanonikal (saat ini target berupa teks judul, traversal hop-2 bisa gagal); ganti relasi generik `terkait_dengan → Soeharto` di 1.112 kliping dengan relasi spesifik.
2. **Metadata arsip:** 1.112 kliping masih `confidence: high` + `risiko_editorial: rendah` massal tanpa verifikasi silang; bedakan `source_type` dari `verification_status`.
3. **Sumber halaman fondasi:** mis. `peristiwa/malari-1974.md` — sumber belum menunjuk dokumen spesifik (URL/arsip).
4. **Sitemap + JSON-LD.**

## Langkah berikutnya yang disarankan
1. Batch 3 di atas, mulai dari skema relasi (keputusan user dulu soal bentuk kanonikal).
2. Uji tanya-jawab wiki via MCP (ditunda user sejak 2 Nov 2026).

## Referensi teknis
- Schema DB: FTS5 `pages` + `entities` + `relations` + `meta` (lihat `scripts/indexer/build-fts5.py` terbaru)
- DB path: `scripts/indexer/wiki-fts5.db` (dibangun ulang tiap deploy; jangan andalkan isi DB lama — DB 2 Nov 2026 masih berisi 2.726 halaman termasuk `sources/` yang sudah dihapus)
- Server specs: 2 vCPU, ~2 GB RAM (sama dengan irawiki)
- Frontmatter schema: lihat `content/aktor/soeharto.md` atau `content/hub/orde-baru.md` sebagai contoh
- Predikat terkontrol: `terlibat_dalam`, `menunjuk`, `didukung_oleh`, `menentang`, `anggota_dari`, `memimpin`, `terkait_dengan`, `menyebut`
- Kategori canonical 6 slug: `kekuasaan-dan-legitimasi`, `ekonomi-dan-kepemilikan`, `keamanan-dan-kebebasan`, `pembangunan-dan-kehidupan`, `krisis-dan-reformasi`, `konsep`
- Jangan inventarisasi kategori baru untuk hub/concept pages; pakai yang ada.

## Catatan penting
- Jangan pakai `Path.glob('**/*.md')` untuk rekursi; pakai `Path.rglob('*.md')`.
- `_index.md` dan `index.md` di-skip dari indexer.
- Setiap kali push: `git fetch origin && git rebase origin/main && git push origin main` (remote bisa advance kapan saja).
- File `cetak-biru-wiki-orde-baru.md` terletak di `/home/ubuntu/.hermes/cache/documents/doc_09444ab6facd_cetak-biru-wiki-orde-baru.md`.
- Riwayat: migrasi `content/sources/` 2.697 file (67 batch, 2026) LALU dihapus atas perintah user 6 Nov 2026 — lihat `MEMORY.md` agen, bukan dokumen ini, untuk keputusan penghapusan.
