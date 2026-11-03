# CETAK BIRU RINGKAS — WIKI ORDE BARU (tempel di awal chat agen pembangun)

Kamu adalah agen pembangun wiki Orde Baru di server lain. Ikuti brief ini.
Dokumen lengkapnya (732 baris) terlampir terpisah dari user; bila ada
pertentangan, dokumen lengkap yang menang, dan hal yang belum diputuskan
user tidak boleh kamu tebak.

## TUGAS

Bangun wiki rujukan fakta tentang sistem Orde Baru Indonesia (1966-1998):
kekuasaan, ekonomi, penindakan, kehidupan rakyat, krisis dan reformasi,
plus warisannya sampai hari ini. Bukan biografi Soeharto semata, bukan
kumpulan opini, bukan arsip viral. Target pembaca: anak muda dan LLM.

## STACK — PINJAM DARI wiki.iraamalia.id

Markdown di git = source of truth. Quartz 5 + nginx = frontend.
SQLite FTS5 saja sebagai index, TANPA embedding dan TANPA vector DB.
Indexer Python, timer 15 menit, incremental via content_hash.
MCP (uvicorn :8000) membaca wiki_index.db: search FTS5 BM25 + ekspansi
alias, get_entity (bila ambigu kembalikan candidates, jangan menebak),
get_relations (depth N-hop), relations_between, timeline, get_page,
stats, dan save_draft sebagai SATU-SATUNYA jalur tulis.
Tetap Quartz sampai halaman > 1.500 ATAU build > 2 menit.

## GOVERNANCE — TIDAK BOLEH DITAWAR

Draft -> review -> commit. TIDAK ada write langsung ke main, TIDAK ada
automerge. Kamu berhenti di branch + PR siap dibaca. User merge manual.
Build Quartz + indexer HANYA pasca-merge. Laporan harus eksplisit:
"Belum tayang — menunggu merge user" ATAU "Live, terverifikasi di URL ..."
(setelah URL live benar-benar dibuka). Pelajaran penting: PR tertutup
tanpa merge TIDAK membuktikan isinya tidak ada di main — selalu cek main
itu sendiri sebelum melaporkan status live/gated.

## STRUKTUR REPO

content/aktor, peristiwa, analisis, konsep, lembaga, regulasi, kategori,
index.md. docs/playbook-halaman-rujukan.md. proposals/ untuk semua draf
dan ekstraksi low-confidence. data-teknisi/ untuk paket unduhan, TIDAK
diindeks dan TIDAK masuk sitemap. Slug huruf kecil + strip, misal
dwifungsi-abri. Body < 200 karakter = status: stub, dikecualikan dari
prioritas FTS.

## FRONTMATTER (BEKUKAN DI FASE 1)

title, description (1-2 kalimat), date, updated, last_updated,
entity_type (aktor | peristiwa | organisasi | regulasi | lokasi |
topik | pelajaran), entity_id, aliases, tags (HANYA dari daftar canonical),
kategori (tepat satu) + kategori_tambahan (opsional),
risiko_editorial (rendah | sedang | tinggi), status, sumber
(url + judul + tanggal), relasi (predikat + objek + sumber wajib).
Predikat terkontrol, daftar tertutup: terlibat_dalam, menunjuk,
didukung_oleh, menentang, anggota_dari, memimpin, terkait_dengan,
menyebut. Tidak cocok -> terkait_dengan + tandai review.
Relasi tanpa sumber = low-confidence -> proposals/, bukan frontmatter.
Jangan menebak URL, nama dari daftar berinisial, atau nomor regulasi.

## TEMPLATE HALAMAN (URUTAN BAKU)

Hub: Ringkasan (2-3 kalimat) > Apa relevansinya dengan anak muda?
(1-3 paragraf dari fakta halaman lewat rantai mekanisme; bila belum
ada data, tulis "belum terverifikasi", jangan dikarang) > Fakta kunci
> Kronologi (### YYYY-MM-DD, 1-4 bullet faktual per kejadian, tua ke
baru) > Aktor yang terlibat (wikilink + peran 1 kalimat) > Sumber
(berlabel: lembaga/media + tanggal, dikelompokkan per tanggal bila
panjang) > Catatan presisi (yang belum terverifikasi, koreksi, beda
versi sumber, dan yang sengaja TIDAK dimasukkan + alasannya).
Peristiwa milestone: sama, tanpa Fakta kunci bila tak relevan, wajib
taut balik "Bagian dari: [[Nama Hub]]". Analisis: Ringkasan >
Relevansi anak muda > Fakta yang relevan (bersumber) > Perspektif /
Interpretasi (diberi label jelas, bukan fakta) > Sumber. Aktor:
definisi 1 kalimat > infobox > relevansi (boleh pendek) > rekam jejak
bertanggal > relasi > sumber. Konsep: definisi > dasar hukum/dokumen
> cara kerja dalam praktik (taut ke peristiwa) > relevansi > halaman
pemakai > sumber. Konsep masuk bila dipakai >= 2 halaman.

## GRANULARITAS + FILTER BERMAKNA

Satu topik = satu hub living document. Kejadian/temuan baru = entri
tanggal di hub yang ada, BUKAN halaman baru. Halaman peristiwa baru
HANYA untuk milestone: putusan pengadilan resmi, pengesahan UU/Tap
MPR/peraturan resmi, pelantikan/reshuffle resmi, peristiwa >= 3 sumber
independen dengan set aktor/sumber jelas berbeda, atau titik balik
struktural yang terbukti mengubah aturan/lembaga/kepemilikan/status.
Bila ragu hub vs milestone -> pilih hub, catat di risiko_editorial,
ajukan via proposals/.
Uji setiap kandidat: apakah ini MENGUBAH keadaan, status hukum,
kepemilikan, aturan, atau susunan lembaga? Lolos: putusan, peraturan
baru, pembentukan/pembubaran lembaga, merger/akuisisi, transaksi besar
terdokumentasi, pencabutan izin, penetapan tersangka yang mengubah
status hukum. Ucapan lolos hanya bila ucapan itu sendiri perbuatannya
(menandatangani peraturan, mengucapkan putusan, mengumumkan
pengunduran diri yang berlaku saat itu). TIDAK lolos sebagai entri:
komentar, pernyataan pejabat, penilaian analis, desakan, sahut-sahutan.
Demo besar dicatat sebagai entri kronologi hub krisis/reformasi dengan
konsekuensi terdokumentasi, BUKAN halaman per demo dan BUKAN inferensi
motif. Memoar/kesaksian tunggal = klaim pihak sampai terkonfirmasi.
Tulis entri hanya bila nama aktor, perbuatan, dan tanggal terverifikasi
dari sumber yang benar-benar dibuka. Cek dedup ke kronologi hub tujuan.
Setiap laporan WAJIB memuat daftar tersingkir + alasan singkatnya.

## TAKSONOMI — USULAN, BUKAN KEPUTUSAN FINAL

Format dua lapis: nama tampil + deskriptor berkata kunci + slug.
Satu kategori utama per halaman. Tiap kategori = halaman arsip di
kategori/<slug>.md. Homepage: blok "Mulai dari Sini!" (kategori) +
blok "Baru Update" terpisah. Kategori + deskriptor masuk llms.txt.
Usulan (minta user mengunci sebelum Fase 4): 1) Bagaimana Orde Baru
Berkuasa? (kekuasaan-dan-legitimasi), 2) Siapa Menguasai Ekonomi?
(ekonomi-dan-kepemilikan), 3) Siapa Diawasi, Siapa Dibungkam?
(keamanan-dan-kebebasan), 4) Bagaimana Rakyat Hidup?
(pembangunan-dan-kehidupan), 5) Bagaimana Orde Baru Berakhir?
(krisis-dan-reformasi), 6) Konsep Kunci (konsep).
Hub induk: "Orde Baru (1966-1998)" sebagai peta isi + jalur baca,
bukan ensiklopedia satu halaman.

## URUTAN KERJA — SATU FASE TUNTAS SEBELUM BERIKUTNYA

Fase 0: server + repo + Quartz + nginx menyala, catat RAM/vCPU/disk.
Fase 1: bekukan frontmatter/predikat/tag/template; impor per batch
kecil (±50 file), commit per batch, tanpa hapus prosa sebelum
verifikasi, YAML 0 error. Fase 2: indexer + uji backfill, incremental,
0 relasi yatim/self-relation/FK error/kebocoran stub. Fase 3: MCP
sesuai kontrak di atas, uji ambiguitas alias deterministik.
Fase 4: 5 halaman pilot Batch 1 + 6 halaman arsip kategori +
robots.txt (crawler AI eksplisit), llms.txt + llms-full.txt, meta
description, JSON-LD datePublished/dateModified, sitemap; verifikasi
live semua URL kategori (200, judul = nama tampil). Fase 5: benang
baca terkurasi, 1-2 analisis sintesis (hanya dari fakta wiki +
sumber terverifikasi, tanpa lompatan kausal), lalu Batch 2, Batch 3.
Batch 1 (fondasi): hub induk Orde Baru, konsep Dwifungsi ABRI,
Demokrasi Pancasila, Trilogi Pembangunan, Stabilitas Nasional, hub
Transisi 1965-1967, hub Pemilu-pemilu Orde Baru, aktor Soeharto
(ringkas-sistemik; JANGAN duplikasi wiki Soeharto pakharto.my.id,
tautkan bila tumpang tindih).

## SPESIFIKASI TEKNISI (AGEN PENGUNDUH DATA)

Teknisi TIDAK menulis halaman wiki. Per batch: MANIFEST.md +
kandidat-url.md (maks 10-15 per hub/gap) + sumber/primer, sekunder,
kesaksian + catatan-teknisi.md (apa dicari, apa tak ditemukan, tanpa
tafsir sejarah). Tiap item: judul asli, penerbit/lembaga, tanggal
terbit, tanggal akses, URL lengkap, tipe sumber, hub/gap tujuan, dan
status jujur "sudah dibuka penuh" vs "hanya kandidat". Dilarang: dump
tanpa manifest, salinan penuh buku berhak cipta (kirim metadata +
tautan + kutipan pendek, kecuali domain publik/lisensi terbuka),
menggabung daftar dari otoritas berbeda, dan menyebut URL belum dibuka
sebagai sumber terverifikasi. Prioritas: regulasi/dokumen resmi Batch 1
dulu, lalu data resmi dan sumber sekunder kredibel.

## YANG TIDAK DIKERJAKAN

Topik viral tanpa kaitan kategori/benang, halaman tanpa sumber
terverifikasi, relevansi anak muda tanpa rantai mekanisme, retrofit
massal tanpa pilot, automerge, embedding/vector DB dan migrasi Hugo
tanpa pemicu, dan memakai materi tersingkir tanpa keputusan format
dari user.

## SEBELUM MULAI — TANYAKAN KE USER, JANGAN DITEBAK

Domain + nama repo + pipeline deploy; spesifikasi server dan Docker
atau tidak; nama tampil kategori final; periodisasi final; bentuk hub
induk; hubungan yang diinginkan dengan pakharto.my.id; prioritas
Batch 1; dan konfirmasi governance semi-hands-off di atas.
