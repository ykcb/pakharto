# Prompt Handoff — Wiki Soeharto (pakharto.my.id)

Kamu adalah agen pembangun yang melanjutkan pekerjaan Wiki Soeharto di repo `/home/ubuntu/quartz`, branch `main`. Live site: `https://pakharto.my.id`.

## Aturan tetap
- Paket free, jangan kerjakan terlalu banyak sekaligus dalam satu turn.
- `content/sources/` SUDAH DIHAPUS atas perintah tegas user (6 Nov 2026, commit `fe232b49`) — arsip verbatim 2.697 halaman. JANGAN dipulihkan, JANGAN diindeks ulang. File tetap ada di riwayat git bila user meminta.
- `public/` adalah build output dan TIDAK dilacak git sejak batch 2 (7 Nov 2026). JANGAN `git add -f public/` — deploy membangunnya dari `content/` lewat `deploy.sh`.
- Halaman `/kategori/` SUDAH DIHAPUS (4 Nov 2026, commit `073e1384`). `kategori:` di frontmatter kini hanya label topik internal opsional; navigasi pembaca lewat halaman hub. JANGAN buat ulang halaman kategori.
- Schema frontmatter canonical §5 sudah dibeku di Fase 1; jangan ubah field seenaknya. Skema relasi kanonikal (batch 3, 7 Nov 2026): relasi ditulis `predikat`/`objek`/`sumber` — bentuk `type`/`target` DITOLAK validator. Predikat terkontrol ada di `scripts/validate_frontmatter.py` (`ALLOWED_PREDIKAT`); kliping memakai `dokumen_tentang`, bukan `terkait_dengan`.
- Konten editorial baru lewat PR + merge manual user. Batch migrasi data boleh commit langsung ke main dengan pesan batch yang jelas.
- Jangan enable automerge.
- Python interpreter untuk tools: `/usr/bin/python3` (memiliki `fastmcp`, `yaml`, `sqlite3`). Jangan gunakan venv Hermes untuk script repo. Dependensi dipin di `scripts/requirements.txt`.
- Path repo/DB configurable via env `PAKHARTO_REPO` / `PAKHARTO_DB` (default `/home/ubuntu/quartz`).

## Status saat ini (per 7 Nov 2026, setelah batch 1–3 audit ChatGPT)
- **Kode tersedia:** MCP server 12 tools di `scripts/mcp/server.py` + `scripts/mcp/wiki_query.py` (FastMCP 4.1.5, stdio).
- **Database berhasil dibangun:** `scripts/indexer/wiki-fts5.db` (di-`.gitignore`) dibangun ATOMIK oleh `scripts/indexer/build-fts5.py` (DB sementara → verifikasi tabel + jumlah halaman → `os.replace`). DIBANGUN ULANG OTOMATIS di setiap `deploy.sh` (langkah 3/7). Isi per rebuild terakhir: ~1.129 halaman (1.135 Markdown minus file `index.md`/`_index.md` yang di-skip), tabel `pages` (FTS5), `entities`, `relations`, `meta`.
- **Relasi kanonikal (batch 3):** indexer dua pass — target relasi/wikilink di-resolusi ke `entity_id` kanonikal (judul/alias/path), teks asli tersimpan di kolom `relations.target_label`. Target tanpa halaman (mis. konsep yang sudah digabung ke glosarium: Stabilitas Nasional, Demokrasi Pancasila, Trilogi Pembangunan, Dwifungsi ABRI, Transisi 1965–1967, Supersemar, Kabinet Pembangunan, Golkar, Petisi 50) tetap tersimpan sebagai teks dan tercatat unresolved di log build. Traversal multi-hop kini sampai (uji: `get_relations('soeharto', depth=2)` mengembalikan 55 relasi vs 13 di depth=1 — sebelum resolusi, hop ke-2 putus karena target berupa teks judul yang tidak cocok dengan `source_entity` apa pun).
- **Validator skema:** `scripts/validate_frontmatter.py` — menolak relasi `type`/`target`, predikat di luar kosakata, kategori bukan slug kanonikal, `entity_type` di luar vokabulari, dan enum `confidence`/`risiko_editorial`/`status`/`verification_status` yang tidak dikenal. Dijalankan di `deploy.sh` (langkah 2/7) dan CI.
- **Kliping (batch 3):** 1.112 artikel kini `entity_type: kliping` (bukan `topik`), `confidence: medium`, `risiko_editorial: sedang`, `status: unreviewed`, `verification_status: unreviewed`, relasi `dokumen_tentang → soeharto`. Isi kliping adalah arsip verbatim yang belum diverifikasi silang — JANGAN menaikkan confidence-nya secara massal tanpa verifikasi per artikel.
- **Test lulus:** `python3 scripts/mcp/server.py --test` — 12 tools dengan assertion nyata (search > 0 hasil, `relations_between` soeharto→Kopkamtib ketemu, `get_page` menolak traversal, `save_draft` anti-timpa + cleanup draft uji). Dijalankan otomatis di `deploy.sh` (langkah 4/7) dan di CI.
- **Service berjalan:** TIDAK ada service HTTP publik. MCP dipakai via stdio oleh Hermes dan oleh agen ini (konektor custom, SSH stdio, allowlist 12 tools). Mode streamable-http pernah terverifikasi handshake tapi TIDAK dipakai.
- **Endpoint dapat diakses:** stdio saja. Satu-satunya jalur tulis: `save_draft` → `proposals/<slug>.md` (frontmatter via `yaml.safe_dump`; slug yang sama jadi versi bertimestamp, tidak menimpa).
- **Deployment live tervalidasi:** `bash ~/quartz/deploy.sh` — 7 langkah: (1) generate `llms.txt`/`llms-full.txt` (fail-fast bila halaman CORE hilang), (2) validasi skema frontmatter, (3) rebuild FTS5, (4) MCP smoke test, (5) `npx quartz build` + guard (HTML hasil build harus ≥ jumlah Markdown), (6) copy assets, (7) `rsync --delete` ke `/var/www/pakharto.my.id/public/`. Terakhir sukses 7 Nov 2026 (batch 2).
- **Sitemap + JSON-LD (sudah ada, diverifikasi live 7 Nov 2026):** Quartz menghasilkan `sitemap.xml` otomatis (4.253 URL) dan JSON-LD per halaman (`HistoricalEvent`+`Article`, `BreadcrumbList`, author/publisher) — TIDAK perlu dibuat manual.
- **CI:** `.github/workflows/pakharto-ci.yml` (khusus repo ini, branch `main`) menguji generator llms, validator frontmatter, build FTS5, dan self-test MCP. Workflow upstream Quartz (`ci.yaml`) TIDAK berlaku di repo ini (hanya jalan untuk `jackyzha0/quartz` branch `v5`).
- **Koreksi faktual batch 1 (7 Nov 2026):** kronologi Soeharto (Supersemar 11 Mar 1966, Pejabat Presiden 12 Mar 1967, Presiden 27 Mar 1968) dan tabel Pemilu Orde Baru (6 pemilu, angka KPU 2 desimal) — live terverifikasi.
- **Malari (batch 3):** sumber spesifik (Heru Cahyono 1998 ISBN 979-416-549-2; Ramadhan K.H. 1994 ISBN 979-416-258-2 — tahunnya 1994, bukan 1998; Suwirta 2018 SUSURGALUR 6(1) hlm. 73–98; Tempo Edisi Khusus Malari 13 Jan 2014; Kompas 16 Jan 1974); vonis Hariman 6 tahun 6 bulan (21 Des 1974), bukan 6 tahun; angka korban dicantumkan sebagai rentang (luka 137–300, ditangkap 750–775) karena sumber berbeda; daftar 12 media dibredel tiga tahap + catatan variasi daftar antar sumber.
- **Taksonomi kanonikal (disamakan batch 2):** 6 slug dari frontmatter konten — `kekuasaan-dan-legitimasi`, `ekonomi-dan-kepemilikan`, `keamanan-dan-kebebasan`, `pembangunan-dan-kehidupan`, `krisis-dan-reformasi`, `konsep`. Dipakai serentak oleh `CANONICAL_CATEGORIES` di `wiki_query.py`, header `llms.txt`, dan generator `build_llms_txt.py`. Jangan inventarisasi slug baru tanpa mengubah ketiganya.
- **Vokabulari entity_type (batch 3):** `aktor`, `peristiwa`, `organisasi`, `pelajaran`, `konsep`, `topik`, `kliping`. Halaman hub tetap `topik`; 3 halaman konsep (KKN, Glosarium, Floating Mass) kini `konsep`.

## Yang BELUM dikerjakan
1. **Verifikasi silang isi kliping per artikel** (1.112 artikel masih `unreviewed`) — pekerjaan kurasi, bukan skrip; jangan diklaim selesai sebelum ada yang benar-benar membaca artikelnya.
2. **Relasi spesifik per kliping** — kliping hanya punya satu relasi dokumen (`dokumen_tentang → soeharto`); relasi ke aktor/peristiwa yang disebut di dalam isi artikel butuh pembacaan isi, bukan migrasi massal. Jangan difabrikasi dari judul.
3. **Target relasi yang belum teresolusi** (konsep gabungan ke glosarium dkk., lihat daftar di atas) — butuh halaman sendiri atau pemetaan eksplisit ke anchor glosarium; belum diputuskan.
4. **Uji tanya-jawab wiki via MCP** (ditunda user sejak 2 Nov 2026).

## Referensi teknis
- Schema DB: FTS5 `pages` + `entities` + `relations` (kolom `target_label` menyimpan teks asli target) + `meta` (lihat `scripts/indexer/build-fts5.py` terbaru)
- DB path: `scripts/indexer/wiki-fts5.db` (dibangun ulang tiap deploy; jangan andalkan isi DB lama — DB 2 Nov 2026 masih berisi 2.726 halaman termasuk `sources/` yang sudah dihapus)
- Server specs: 2 vCPU, ~2 GB RAM (sama dengan irawiki)
- Frontmatter schema: lihat `content/aktor/soeharto.md` atau `content/hub/orde-baru.md` sebagai contoh
- Predikat terkontrol: lihat `ALLOWED_PREDIKAT` di `scripts/validate_frontmatter.py`
- Kategori canonical 6 slug: `kekuasaan-dan-legitimasi`, `ekonomi-dan-kepemilikan`, `keamanan-dan-kebebasan`, `pembangunan-dan-kehidupan`, `krisis-dan-reformasi`, `konsep`
- Jangan inventarisasi kategori baru untuk hub/concept pages; pakai yang ada.

## Catatan penting
- Jangan pakai `Path.glob('**/*.md')` untuk rekursi; pakai `Path.rglob('*.md')`.
- `_index.md` dan `index.md` di-skip dari indexer.
- Setiap kali push: `git fetch origin && git rebase origin/main && git push origin main` (remote bisa advance kapan saja).
- File `cetak-biru-wiki-orde-baru.md` terletak di `/home/ubuntu/.hermes/cache/documents/doc_09444ab6facd_cetak-biru-wiki-orde-baru.md`.
- Riwayat: migrasi `content/sources/` 2.697 file (67 batch, 2026) LALU dihapus atas perintah user 6 Nov 2026 — lihat `MEMORY.md` agen, bukan dokumen ini, untuk keputusan penghapusan.
