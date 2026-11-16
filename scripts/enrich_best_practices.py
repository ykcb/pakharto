#!/usr/bin/env python3
"""
Memetakan korpus primer ke 6 pilar Best Practices di content/pelajaran/
via tags dan relasi frontmatter, tanpa mengubah URL/nama file.

PERILAKU DEFAULT: DRY-RUN — hanya melaporkan, TIDAK menulis file apa pun.
Penulisan hanya terjadi dengan flag --apply yang eksplisit.

Revisi v3 (16 Nov 2026, disetujui user 14:06 WIB): mekanisme
pengecualian EXCLUDE_FILES/EXCLUDE_REASONS — 27 pasangan file-pilar
yang dikecualikan dari klasifikasi berdasarkan review per file atas
28 file berbukti terlemah (review-28-file-terlemah.md). Pasangan yang
dikecualikan tidak dihitung sebagai cocok, tidak menambah tag/relasi,
dan dilaporkan terpisah di seksi "excluded" laporan. Kosakata, aturan
AND, dan perilaku lain tidak berubah dari v2.

Revisi Batch 3B TERKOREKSI (16 Nov 2026, disetujui user) atas v1:
1. Kosakata: pola \\btransmigrasi\\b DIHAPUS dari pilar
   arsitektur-kb-dan-posyandu (keputusan editorial: transmigrasi adalah
   kebijakan mobilitas penduduk yang berbeda, bukan bagian arsitektur
   KB/Posyandu — sesuai draf pilar 4). Kosakata pilar lain tidak berubah.
2. Aturan pola-tunggal bentuk AND: satu pola cocok bila muncul >= 1x di
   judul/deskripsi DAN >= 2x di badan. Ambang >= 3x v1 diganti; ambang
   >= 4x TIDAK dipakai (terbukti tidak menyaring pengulangan retoris
   15x "tinggal landas" pada file 00004). TIDAK ada blacklist per file
   pada revisi ini (daftar pengecualian hasil review ditambahkan
   pada v3, lihat di atas).
3. Dukungan tags: flow-style satu baris: tag pilar disisipkan sebelum
   tanda `]` pada baris itu saja, tanpa menyentuh byte lain. Flow
   multi-baris tetap di-skip. relasi: flow-style tetap di-skip.

Perbaikan atas draf awal (Batch 2 refactoring, Nov 2026):
1. Strip boilerplate sebelum klasifikasi: tautan markdown ke
   soehartolibrary.id/tag/* (footer tag situs sumber — penyebab positif
   palsu), konstruksi gambar ![...](...), URL telanjang, dan baris yang
   hanya berisi tautan. Tautan non-tag disisakan teksnya, dibuang URL-nya
   (slug URL bukan prosa).
2. Pilar desentralisasi-anggaran-program-inpres: frasa "sd inpres" dan
   "sekolah dasar inpres" dihapus dulu dari teks pencarian agar dokumen
   SD Inpres tidak salah kena tag program-inpres.
3. Skor berbasis kemunculan: cocok bila >= 2 pola berbeda kena, ATAU satu
   pola muncul >= 1x di judul/deskripsi DAN >= 2x di badan (teks bersih).
   Bukti per kecocokan dilaporkan (pola -> jumlah kemunculan + lokasi
   judul/deskripsi/badan).
4. Semua skip dilaporkan: tanpa frontmatter, gagal parse YAML, gagal
   decode UTF-8 (dibaca errors="strict"; tidak pernah ditulis ulang
   dengan karakter pengganti), struktur frontmatter tak terduga.
5. Penyisipan BEDAH: hanya baris baru yang disisipkan ke dalam blok
   list tags:/relasi: yang ada (indentasi/gaya dipertahankan), atau kunci
   baru dibuat di akhir frontmatter bila belum ada; untuk tags:
   flow-style satu baris, tag baru disisipkan sebelum `]` pada baris itu
   saja. Seluruh byte lain tidak berubah — TIDAK ada safe_dump seluruh
   frontmatter. File dengan struktur tak terduga (flow-style multi-baris,
   relasi: flow-style, kunci ganda, tags/relasi bukan list) di-SKIP untuk
   penanganan manual. Setelah menulis, file di-parse ulang dan di-assert
   sama dengan semula + tambahan yang diniatkan saja; bila verifikasi
   gagal, byte semula dipulihkan.

Konvensi repo yang dipertahankan:
- REPO_DIR dari env PAKHARTO_REPO atau relatif terhadap lokasi file
  (pola portabilitas Batch 1, meniru scripts/submit_indexnow.py).
- Entri relasi memakai predikat dokumen_tentang + objek slug + sumber
  URL dokumen (konvensi 1.292 file yang sudah ada).
- Idempotent: tag/relasi yang sudah ada tidak ditambah dua kali.

Peringatan: relasi menunjuk ke content/pelajaran/<slug>.md. Skrip ini
hanya memperingatkan bila halaman pilar belum ada; JANGAN menjalankan
--apply atas korpus nyata sebelum keenam halaman pilar ditulis.

Contoh pakai:
  python3 scripts/enrich_best_practices.py                          # dry-run, lapor ke stdout
  python3 scripts/enrich_best_practices.py --report /tmp/lap.md     # dry-run + laporan Markdown
  python3 scripts/enrich_best_practices.py --folder otobiografi-soeharto --limit 20
  python3 scripts/enrich_best_practices.py --apply --report /tmp/lap.md
"""
import argparse
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

REPO_DIR = Path(os.environ.get("PAKHARTO_REPO") or Path(__file__).resolve().parent.parent)
CONTENT_DIR = REPO_DIR / "content"

TARGET_DIRS = [
    "perpustakaan-soeharto",
    "otobiografi-soeharto",
    "diantara-para-sahabat",
    "dalam-berita-jilid-1",
]

# Kosakata pilar + keyword: sama dengan draf awal, KECUALI satu perubahan
# editorial yang disetujui user 16 Nov 2026 (Batch 3B terkoreksi): pola
# \btransmigrasi\b DIHAPUS dari pilar arsitektur-kb-dan-posyandu, karena
# transmigrasi adalah kebijakan mobilitas penduduk yang berbeda, bukan
# bagian arsitektur KB/Posyandu (sesuai draf pilar 4). Jangan mengubah
# kosakata lain di sini — kosakata pilar adalah keputusan editorial.
PILAR_RULES = {
    "swasembada-pangan-dan-bulog": {
        "tag": "pilar/pangan-bulog",
        "keywords": [
            r"\bbulog\b", r"\bswasembada\b", r"\bbimas\b", r"\binmas\b",
            r"\brumus tani\b", r"\bpupuk\b", r"\bgabah\b", r"\bberas\b",
            r"\bintensifikasi\b", r"\bpanca usaha tani\b", r"\bkud\b"
        ],
    },
    "revolusi-sd-inpres-dan-wajib-belajar": {
        "tag": "pilar/sd-inpres",
        "keywords": [
            r"\bsd inpres\b", r"\bwajib belajar\b", r"\bbuta huruf\b",
            r"\bsekolah dasar\b", r"\bpendidikan dasar\b", r"\bgedung sd\b"
        ],
    },
    "stabilisasi-hiperinflasi-1966-1970": {
        "tag": "pilar/stabilisasi-ekonomi",
        "keywords": [
            r"\bhiperinflasi\b", r"\binflasi\b", r"\biggi\b", r"\bpma\b",
            r"\bpmdn\b", r"\banggaran berimbang\b", r"\brescheduling\b",
            r"\bstabilisasi ekonomi\b", r"\bpaket 3 oktober\b", r"\bdevaluasi\b"
        ],
    },
    "arsitektur-kb-dan-posyandu": {
        "tag": "pilar/kb-posyandu",
        "keywords": [
            r"\bkeluarga berencana\b", r"\bbkkbn\b", r"\bposyandu\b",
            r"\bpuskesmas\b", r"\bkependudukan\b",
            r"\bakseptor\b", r"\bdua anak cukup\b"
        ],
    },
    "teknokrasi-dan-disiplin-repelita": {
        "tag": "pilar/teknokrasi-repelita",
        "keywords": [
            r"\brepelita\b", r"\bpelita [ivx1-6]+\b", r"\btrilogi pembangunan\b",
            r"\bbappenas\b", r"\bgbhn\b", r"\btinggal landas\b"
        ],
    },
    "desentralisasi-anggaran-program-inpres": {
        "tag": "pilar/program-inpres",
        "keywords": [
            r"\binpres\b", r"\binstruksi presiden\b", r"\bbantuan desa\b",
            r"\bbandes\b", r"\bjalan desa\b", r"\bpenghijauan\b", r"\bpasar inpres\b"
        ],
    },
}

# Pilar yang frasa pesaingnya harus di-scrub sebelum klasifikasi, agar
# dokumen SD Inpres tidak salah kena tag program-inpres. Urutan: frasa
# terpanjang dulu supaya "sekolah dasar inpres" tidak tersisa "inpres".
INPRES_PILAR = "desentralisasi-anggaran-program-inpres"
INPRES_SCRUB = ("sekolah dasar inpres", "sd inpres")

MIN_DISTINCT_PATTERNS = 2
# Aturan pola-tunggal bentuk AND (Batch 3B terkoreksi, menggantikan ambang
# >= 3x v1): satu pola harus muncul di judul/deskripsi DAN berulang di
# badan. Ambang >= 4x sengaja TIDAK dipakai: pengulangan retoris 15x
# pada file 00004 lolos dari ambang berapa pun yang hanya menghitung
# badan; yang menyaringnya adalah syarat kemunculan di judul/deskripsi.
MIN_SINGLE_PATTERN_HEAD_HITS = 1
MIN_SINGLE_PATTERN_BODY_HITS = 2

# Daftar pengecualian v3 (keputusan user 16 Nov 2026, 14:06 WIB,
# atas review per file review-28-file-terlemah.md): pasangan
# (file, pilar) yang bukti keyword-nya dinilai bukan bahasan
# substantif pilar itu. Pasangan di sini TIDAK dihitung sebagai
# cocok — tidak menambah tag maupun relasi. File yang semua
# pasangannya dikecualikan menjadi no_match. Pasangan lain pada
# file yang sama tetap diproses normal. Jangan mengubah daftar
# ini tanpa keputusan user + review per file.
EXCLUDE_FILES = {
    ("diantara-para-sahabat/13-pikiran-modern-dalam-pribadi-jawa.md",
     "teknokrasi-dan-disiplin-repelita"),
    ("diantara-para-sahabat/36-mencintai-petani-dan-pertanian.md",
     "swasembada-pangan-dan-bulog"),
    ("diantara-para-sahabat/40-penuh-perhatian-terhadap-hukum-laut.md",
     "teknokrasi-dan-disiplin-repelita"),
    ("diantara-para-sahabat/44-tegas-dalam-pendirian-namun-luwes-dan-bijak.md",
     "desentralisasi-anggaran-program-inpres"),
    ("diantara-para-sahabat/63-kuat-pada-prinsip-rendah-hati-dalam-sifat.md",
     "swasembada-pangan-dan-bulog"),
    ("diantara-para-sahabat/63-kuat-pada-prinsip-rendah-hati-dalam-sifat.md",
     "teknokrasi-dan-disiplin-repelita"),
    ("diantara-para-sahabat/75-menghilangkan-dan-mencegah-penyelewengan.md",
     "teknokrasi-dan-disiplin-repelita"),
    ("diantara-para-sahabat/76-pemimpin-yang-penuh-pengertian.md",
     "teknokrasi-dan-disiplin-repelita"),
    ("diantara-para-sahabat/80-guru-bapak-dan-pemimpin-negara.md",
     "teknokrasi-dan-disiplin-repelita"),
    ("diantara-para-sahabat/82-rasa-kesetiakawanan-yang-kuat.md",
     "desentralisasi-anggaran-program-inpres"),
    ("otobiografi-soeharto/otobiografi-bab-073-mencerdaskan-kehidupan-bangsa.md",
     "teknokrasi-dan-disiplin-repelita"),
    ("otobiografi-soeharto/otobiografi-bab-094-hal-kekeluargaan-dan-monopoli.md",
     "stabilisasi-hiperinflasi-1966-1970"),
    ("otobiografi-soeharto/otobiografi-bab-101-saya-sebagai-elemen-angkatan45.md",
     "teknokrasi-dan-disiplin-repelita"),
    ("perpustakaan-soeharto/00004-presiden-soeharto-dan-misteri-kemelut-1998.md",
     "swasembada-pangan-dan-bulog"),
    ("perpustakaan-soeharto/00015-1969-01-08-sidang-kabinet-terbatas-presiden-soeharto-menerima-laporan-sejumlah-menteri.md",
     "swasembada-pangan-dan-bulog"),
    ("perpustakaan-soeharto/00018-1969-01-17-presiden-soeharto-menerima-yayasan-pangdam-se-jawa-dan-resmikan-gedung-yayasan-harapan-kita.md",
     "teknokrasi-dan-disiplin-repelita"),
    ("perpustakaan-soeharto/00038-1970-01-05-lakukan-tradisi-baru-presiden-soeharto-sampaikan-rapbn-di-hadapan-dpr-gr.md",
     "stabilisasi-hiperinflasi-1966-1970"),
    ("perpustakaan-soeharto/00136-1968-03-29-presiden-soeharto-menjamu-kaindaren-di-tokyo.md",
     "stabilisasi-hiperinflasi-1966-1970"),
    ("perpustakaan-soeharto/00144-program-pertanian-era-pak-harto.md",
     "teknokrasi-dan-disiplin-repelita"),
    ("perpustakaan-soeharto/00384-1974-04-09-presiden-soeharto-memimpin-sidang-dewan-stabilisasi-politik-dan-keamanan-nasional.md",
     "stabilisasi-hiperinflasi-1966-1970"),
    ("perpustakaan-soeharto/00384-1974-04-09-presiden-soeharto-memimpin-sidang-dewan-stabilisasi-politik-dan-keamanan-nasional.md",
     "swasembada-pangan-dan-bulog"),
    ("perpustakaan-soeharto/00387-1974-04-22-presiden-soeharto-bentuk-irjenbang.md",
     "desentralisasi-anggaran-program-inpres"),
    ("perpustakaan-soeharto/01080-1975-08-09-menuju-lampung-presiden-soeharto-resmikan-pabrik-sepeda.md",
     "swasembada-pangan-dan-bulog"),
    ("perpustakaan-soeharto/01104-1975-08-07-presiden-soeharto-resmikan-13-pabrik-di-salatiga-dan-dua-pabrik-di-gresik.md",
     "stabilisasi-hiperinflasi-1966-1970"),
    ("perpustakaan-soeharto/01677-menang-tanpa-ngasorake-bagian-2.md",
     "arsitektur-kb-dan-posyandu"),
    ("perpustakaan-soeharto/01677-menang-tanpa-ngasorake-bagian-2.md",
     "teknokrasi-dan-disiplin-repelita"),
    ("perpustakaan-soeharto/01980-bs-muljana-pak-harto-merencana-untuk-masa-kini-dan-masa-nanti-bagian-1.md",
     "teknokrasi-dan-disiplin-repelita"),
}
EXCLUDE_REASONS = {
    ("diantara-para-sahabat/13-pikiran-modern-dalam-pribadi-jawa.md",
     "teknokrasi-dan-disiplin-repelita"):
        "trilogi dalam daftar konsep; GBHN dalam anekdot Bank Dunia",
    ("diantara-para-sahabat/36-mencintai-petani-dan-pertanian.md",
     "swasembada-pangan-dan-bulog"):
        "swasembada/beras satu kalimat memoar (pidato Roma 1985); tanpa bahasan program",
    ("diantara-para-sahabat/40-penuh-perhatian-terhadap-hukum-laut.md",
     "teknokrasi-dan-disiplin-repelita"):
        "satu paragraf menyusun bab Repelita II dalam esai hukum laut ±20 KB; RAGU diputus KECUALIKAN oleh user",
    ("diantara-para-sahabat/44-tegas-dalam-pendirian-namun-luwes-dan-bijak.md",
     "desentralisasi-anggaran-program-inpres"):
        "jalan desa = anekdot Banpres; penghijauan = anekdot lapangan golf; bukan mekanisme Inpres",
    ("diantara-para-sahabat/63-kuat-pada-prinsip-rendah-hati-dalam-sifat.md",
     "swasembada-pangan-dan-bulog"):
        "bagian KUD substantif tapi berbingkai ekonomi koperasi, bukan program pangan; RAGU diputus KECUALIKAN oleh user",
    ("diantara-para-sahabat/63-kuat-pada-prinsip-rendah-hati-dalam-sifat.md",
     "teknokrasi-dan-disiplin-repelita"):
        "trilogi dalam analogi; GBHN soal asas tunggal; tanpa bahasan perencanaan",
    ("diantara-para-sahabat/75-menghilangkan-dan-mencegah-penyelewengan.md",
     "teknokrasi-dan-disiplin-repelita"):
        "Pelita sebagai penanda waktu; Bappenas = kehadiran Widjojo di rapat",
    ("diantara-para-sahabat/76-pemimpin-yang-penuh-pengertian.md",
     "teknokrasi-dan-disiplin-repelita"):
        "Bappenas = kontak pejabat; tinggal landas retoris soal listrik; esai nuklir",
    ("diantara-para-sahabat/80-guru-bapak-dan-pemimpin-negara.md",
     "teknokrasi-dan-disiplin-repelita"):
        "trilogi/GBHN satu kalimat bingkai tanpa uraian perencanaan",
    ("diantara-para-sahabat/82-rasa-kesetiakawanan-yang-kuat.md",
     "desentralisasi-anggaran-program-inpres"):
        "pasar inpres satu klausa observasi pedagang; bukan bahasan mekanisme Inpres",
    ("otobiografi-soeharto/otobiografi-bab-073-mencerdaskan-kehidupan-bangsa.md",
     "teknokrasi-dan-disiplin-repelita"):
        "Repelita IV penanda waktu; tinggal landas retoris soal iptek; bab pendidikan",
    ("otobiografi-soeharto/otobiografi-bab-094-hal-kekeluargaan-dan-monopoli.md",
     "stabilisasi-hiperinflasi-1966-1970"):
        "PMA/PMDN konteks 1987 (iklim investasi), bukan stabilisasi 1966-1970",
    ("otobiografi-soeharto/otobiografi-bab-101-saya-sebagai-elemen-angkatan45.md",
     "teknokrasi-dan-disiplin-repelita"):
        "Repelita V sekali; tinggal landas retoris; refleksi Angkatan '45",
    ("perpustakaan-soeharto/00004-presiden-soeharto-dan-misteri-kemelut-1998.md",
     "swasembada-pangan-dan-bulog"):
        "esai krisis 1998; swasembada/beras masing-masing 1x sepintas",
    ("perpustakaan-soeharto/00015-1969-01-08-sidang-kabinet-terbatas-presiden-soeharto-menerima-laporan-sejumlah-menteri.md",
     "swasembada-pangan-dan-bulog"):
        "satu klausa laporan Inmas/Bimas tanpa isi",
    ("perpustakaan-soeharto/00018-1969-01-17-presiden-soeharto-menerima-yayasan-pangdam-se-jawa-dan-resmikan-gedung-yayasan-harapan-kita.md",
     "teknokrasi-dan-disiplin-repelita"):
        "Repelita/tinggal landas hanya dalam resolusi rapat yang dikutip; dokumen tentang peresmian yayasan",
    ("perpustakaan-soeharto/00038-1970-01-05-lakukan-tradisi-baru-presiden-soeharto-sampaikan-rapbn-di-hadapan-dpr-gr.md",
     "stabilisasi-hiperinflasi-1966-1970"):
        "pidato RAPBN multi-topik; inflasi satu klausa pelaporan capaian",
    ("perpustakaan-soeharto/00136-1968-03-29-presiden-soeharto-menjamu-kaindaren-di-tokyo.md",
     "stabilisasi-hiperinflasi-1966-1970"):
        "pernyataan umum stabilisasi/inflasi dalam jamuan diplomatik, tanpa bahasan program",
    ("perpustakaan-soeharto/00144-program-pertanian-era-pak-harto.md",
     "teknokrasi-dan-disiplin-repelita"):
        "Repelita/Pelita I satu kalimat bingkai; dokumen tentang program pertanian",
    ("perpustakaan-soeharto/00384-1974-04-09-presiden-soeharto-memimpin-sidang-dewan-stabilisasi-politik-dan-keamanan-nasional.md",
     "stabilisasi-hiperinflasi-1966-1970"):
        "dokumen 1974, di luar cakupan periode pilar 1966–1970",
    ("perpustakaan-soeharto/00384-1974-04-09-presiden-soeharto-memimpin-sidang-dewan-stabilisasi-politik-dan-keamanan-nasional.md",
     "swasembada-pangan-dan-bulog"):
        "beras/pupuk hanya butir daftar stok nasional",
    ("perpustakaan-soeharto/00387-1974-04-22-presiden-soeharto-bentuk-irjenbang.md",
     "desentralisasi-anggaran-program-inpres"):
        "Inpres/bantuan desa hanya butir daftar proyek yang diawasi Irjenbang",
    ("perpustakaan-soeharto/01080-1975-08-09-menuju-lampung-presiden-soeharto-resmikan-pabrik-sepeda.md",
     "swasembada-pangan-dan-bulog"):
        "Bimas/intensifikasi cengkeh (bukan pangan pokok), disebut sepintas",
    ("perpustakaan-soeharto/01104-1975-08-07-presiden-soeharto-resmikan-13-pabrik-di-salatiga-dan-dua-pabrik-di-gresik.md",
     "stabilisasi-hiperinflasi-1966-1970"):
        "PMDN/PMA satu klausa pendanaan pabrik",
    ("perpustakaan-soeharto/01677-menang-tanpa-ngasorake-bagian-2.md",
     "arsitektur-kb-dan-posyandu"):
        "KB sekali soal tekanan penduduk; esai tentang aparatur/transportasi/lingkungan",
    ("perpustakaan-soeharto/01677-menang-tanpa-ngasorake-bagian-2.md",
     "teknokrasi-dan-disiplin-repelita"):
        "Bappenas = jabatan penulis; GBHN satu baris",
    ("perpustakaan-soeharto/01980-bs-muljana-pak-harto-merencana-untuk-masa-kini-dan-masa-nanti-bagian-1.md",
     "teknokrasi-dan-disiplin-repelita"):
        "Repelita I sekali historis; Bappenas hanya di catatan kaki jabatan penulis",
}
assert len(EXCLUDE_FILES) == 27 and set(EXCLUDE_REASONS) == EXCLUDE_FILES, \
    "daftar pengecualian v3 tidak konsisten (harus 27 pasangan)"

TAG_LINK_RE = re.compile(r"\[[^\]]*\]\(https?://soehartolibrary\.id/tag/[^)\s]*\)")
IMAGE_RE = re.compile(r"!\[[^\]]*\]\([^)\s]*\)")
MD_LINK_RE = re.compile(r"\[([^\]]*)\]\([^)\s]*\)")
BARE_URL_RE = re.compile(r"https?://\S+")
KEY_RE = re.compile(r"^([A-Za-z0-9_-]+):(.*)$")
ITEM_RE = re.compile(r"^(\s*)-(\s|$)")


class SkipFile(Exception):
    """File dilewati; alasan dicatat di laporan, bukan error fatal."""


# ---------------------------------------------------------------- boilerplate

def strip_boilerplate(body: str) -> str:
    """Buang boilerplate dari badan sebelum klasifikasi.

    (a) tautan markdown ke soehartolibrary.id/tag/* — footer tag situs
        sumber yang menempel di badan kliping;
    (b) konstruksi gambar ![...](...);
    (c) baris yang hanya berisi tautan (setelah tautan dibuang, sisanya
        hanya whitespace/tanda baca pemisah).
    Tautan non-tag disisakan teks tautannya (prosa), dibuang URL-nya,
    karena slug URL bukan prosa dan bisa mengandung kata kunci.
    """
    out = []
    for line in body.split("\n"):
        line = TAG_LINK_RE.sub(" ", line)
        line = IMAGE_RE.sub(" ", line)
        line = MD_LINK_RE.sub(r"\1", line)
        line = BARE_URL_RE.sub(" ", line)
        if line.strip(" \t,;|•·-–—:") == "":
            continue
        out.append(line)
    return "\n".join(out)


# ---------------------------------------------------------------- klasifikasi

def _scrub_inpres(text: str) -> str:
    for phrase in INPRES_SCRUB:
        text = text.replace(phrase, " ")
    return text


def classify(title: str, description: str, body_clean: str) -> dict:
    """Klasifikasi berbasis kemunculan.

    Mengembalikan {slug_pilar: {pola: {"count": n, "where": [...],
    "sections": {"judul": n, "deskripsi": n, "badan": n}}}} untuk pilar
    yang cocok: >= 2 pola berbeda kena, ATAU satu pola muncul >= 1x di
    judul/deskripsi DAN >= 2x di badan (teks bersih; scrub "sd inpres"
    untuk pilar program-inpres berlaku untuk semua lokasi hitungan).
    """
    sections = {
        "judul": title.lower(),
        "deskripsi": description.lower(),
        "badan": body_clean.lower(),
    }
    matched = {}
    for slug, cfg in PILAR_RULES.items():
        secs = sections
        if slug == INPRES_PILAR:
            secs = {name: _scrub_inpres(txt) for name, txt in sections.items()}
        evidence = {}
        for pat in cfg["keywords"]:
            counts = {}
            total = 0
            where = []
            for name, txt in secs.items():
                c = len(re.findall(pat, txt))
                counts[name] = c
                if c:
                    total += c
                    where.append(f"{name} x{c}")
            if total:
                evidence[pat] = {"count": total, "where": where,
                                 "sections": counts}
        distinct = len(evidence)
        single_ok = any(
            (ev["sections"]["judul"] + ev["sections"]["deskripsi"]
             >= MIN_SINGLE_PATTERN_HEAD_HITS)
            and ev["sections"]["badan"] >= MIN_SINGLE_PATTERN_BODY_HITS
            for ev in evidence.values()
        )
        if distinct >= MIN_DISTINCT_PATTERNS or single_ok:
            matched[slug] = evidence
    return matched


# ---------------------------------------------------------------- frontmatter

def _is_delimiter(line: str) -> bool:
    s = line.rstrip("\r\n")
    return s == "---" or (s.startswith("---") and s[3:].strip() == "")


def split_frontmatter(text: str) -> dict:
    """Pisahkan frontmatter dari badan, berbasis baris (byte-preserving).

    Mengembalikan dict lines/fm_lines/closing_idx/fm_text/body/eol.
    """
    lines = text.splitlines(keepends=True)
    if not lines or not _is_delimiter(lines[0]):
        raise SkipFile("tanpa frontmatter (baris pertama bukan ---)")
    eol = "\r\n" if lines[0].endswith("\r\n") else "\n"
    for i in range(1, len(lines)):
        if _is_delimiter(lines[i]):
            return {
                "lines": lines,
                "fm_lines": lines[1:i],
                "closing_idx": i,
                "fm_text": "".join(lines[1:i]),
                "body": "".join(lines[i + 1:]),
                "eol": eol,
            }
    raise SkipFile("tanpa frontmatter (penutup --- tidak ditemukan)")


def scan_keys(fm_lines) -> list:
    """Daftar kunci top-level frontmatter: [(kunci, idx_baris, sisa_baris)].

    Kunci ganda -> SkipFile (yaml.safe_load diam-diam memakai yang
    terakhir; penulisan bedah tidak boleh menebak-nebak).
    """
    keys = []
    seen = set()
    for idx, raw in enumerate(fm_lines):
        m = KEY_RE.match(raw.rstrip("\r\n"))
        if m:
            key = m.group(1)
            if key in seen:
                raise SkipFile(f"kunci ganda di frontmatter: {key}")
            seen.add(key)
            keys.append((key, idx, m.group(2)))
    return keys


def _value_empty_or_comment(value_part: str) -> bool:
    v = value_part.strip()
    return v == "" or v.startswith("#")


def _block_end(keys, pos, fm_len) -> int:
    return keys[pos + 1][1] if pos + 1 < len(keys) else fm_len


def _detect_list_indent(fm_lines) -> str:
    for raw in fm_lines:
        m = ITEM_RE.match(raw.rstrip("\r\n"))
        if m:
            return m.group(1)
    return ""


def _validate_parsed(fm: dict):
    if not isinstance(fm, dict):
        raise SkipFile("frontmatter bukan mapping")
    tags = fm.get("tags")
    if tags is not None and (not isinstance(tags, list)
                             or any(isinstance(t, (dict, list)) for t in tags)):
        raise SkipFile("kunci tags: bukan list skalar")
    relasi = fm.get("relasi")
    if relasi is not None and (not isinstance(relasi, list)
                               or any(not isinstance(r, dict) for r in relasi)):
        raise SkipFile("kunci relasi: bukan list mapping")


def _find_flow_close(value_text: str):
    """Indeks ']' yang menutup daftar flow pada teks ini, atau None.

    Pemindaian sadar-kutip: tanda kurung di dalam string ber-kutip
    (tunggal/ganda) diabaikan. Tanda # yang didahului spasi/tab memulai
    komentar — tidak ada penutup sesudahnya. None berarti daftar tidak
    tertutup pada baris ini (flow multi-baris) atau tidak ada daftar.
    """
    depth = 0
    started = False
    in_single = False
    in_double = False
    i = 0
    while i < len(value_text):
        ch = value_text[i]
        if in_single:
            if ch == "'":
                if i + 1 < len(value_text) and value_text[i + 1] == "'":
                    i += 2
                    continue
                in_single = False
            i += 1
            continue
        if in_double:
            if ch == "\\":
                i += 2
                continue
            if ch == '"':
                in_double = False
            i += 1
            continue
        if ch == "'":
            in_single = True
        elif ch == '"':
            in_double = True
        elif ch == "#" and (i == 0 or value_text[i - 1] in " \t"):
            break
        elif ch == "[":
            depth += 1
            started = True
        elif ch == "]":
            depth -= 1
            if started and depth == 0:
                return i
        i += 1
    return None


def _plan_tags_flow(fm_lines, idx, value_part, new_tags):
    """Rencana sisipan untuk tags: flow-style satu baris.

    Mengembalikan (idx, [baris_baru], "replace"): tag pilar disisipkan
    tepat sebelum ']' penutup, tanpa mengubah byte lain pada baris itu
    (spasi di dalam kurung dan komentar trailing dipertahankan; akhiran
    baris asli dipertahankan). Daftar kosong (tags: []) tidak memakai
    koma di depan. Flow yang tidak tertutup pada baris ini (multi-baris)
    di-SKIP, tidak ditebak.
    """
    raw = fm_lines[idx]
    body = raw.rstrip("\r\n")
    ending = raw[len(body):]
    if not value_part.strip().startswith("["):
        raise SkipFile("kunci tags: bukan block list maupun flow list")
    close = _find_flow_close(value_part)
    if close is None:
        raise SkipFile("kunci tags: flow list tidak tertutup pada baris ini "
                       "(multi-baris, perlu penanganan manual)")
    open_idx = value_part.index("[")
    inner = value_part[open_idx + 1:close]
    sep = "" if inner.strip() == "" else ", "
    insertion = sep + ", ".join(new_tags)
    at = len(body) - len(value_part) + close
    new_line = body[:at] + insertion + body[at:] + ending
    return (idx, [new_line], "replace")


def plan_tags_insert(fm_lines, keys, new_tags, eol):
    """Rencana sisipan tag: (indeks_baris, [baris], jenis).

    Jenis "insert": sisipkan baris baru pada indeks tersebut — di akhir
    blok list tags: yang ada (indentasi dipertahankan), atau kunci tags:
    baru di akhir frontmatter bila belum ada. Jenis "replace": ganti
    baris pada indeks tersebut dengan satu baris baru — khusus tags:
    flow-style satu baris, tag disisipkan sebelum ']' pada baris itu.
    """
    pos = next((i for i, (k, _, _) in enumerate(keys) if k == "tags"), None)
    if pos is None:
        lines = ["tags:" + eol] + ["- " + t + eol for t in new_tags]
        return (len(fm_lines), lines, "insert")
    _, idx, value_part = keys[pos]
    if not _value_empty_or_comment(value_part):
        return _plan_tags_flow(fm_lines, idx, value_part, new_tags)
    end = _block_end(keys, pos, len(fm_lines))
    indent = None
    last = None
    for j in range(idx + 1, end):
        raw = fm_lines[j].rstrip("\r\n")
        if raw.strip() == "" or raw.lstrip().startswith("#"):
            continue
        m = ITEM_RE.match(raw)
        if m and indent is None:
            indent = m.group(1)
        last = j
    if indent is None:
        indent = _detect_list_indent(fm_lines)
    insert_at = (last + 1) if last is not None else idx + 1
    return (insert_at, [f"{indent}- {t}{eol}" for t in new_tags], "insert")


def _relasi_entry_lines(entry, item_indent, cont_indent, eol):
    lines = [f"{item_indent}- predikat: {entry['predikat']}{eol}",
             f"{cont_indent}objek: {entry['objek']}{eol}"]
    if entry.get("sumber"):
        lines.append(f"{cont_indent}sumber: {entry['sumber']}{eol}")
    return lines


def plan_relasi_insert(fm_lines, keys, new_entries, eol):
    """Rencana sisipan entri relasi: (indeks_baris, [baris_baru], "insert").

    Menyisip di akhir blok list relasi: yang ada (indentasi item dan
    lanjutan dipertahankan), atau membuat kunci relasi: baru di akhir
    frontmatter bila belum ada. relasi: flow-style TETAP di-skip seperti
    v1 (tidak diubah pada revisi ini).
    """
    pos = next((i for i, (k, _, _) in enumerate(keys) if k == "relasi"), None)
    if pos is None:
        lines = ["relasi:" + eol]
        for e in new_entries:
            lines.extend(_relasi_entry_lines(e, "", "  ", eol))
        return (len(fm_lines), lines, "insert")
    _, idx, value_part = keys[pos]
    if not _value_empty_or_comment(value_part):
        raise SkipFile("kunci relasi: bukan block list (flow/scalar)")
    end = _block_end(keys, pos, len(fm_lines))
    item_indent = None
    cont_indent = None
    last = None
    for j in range(idx + 1, end):
        raw = fm_lines[j].rstrip("\r\n")
        if raw.strip() == "" or raw.lstrip().startswith("#"):
            continue
        m = ITEM_RE.match(raw)
        if m and item_indent is None:
            item_indent = m.group(1)
        if m and m.group(1) == item_indent:
            last = j
            continue
        stripped = raw.lstrip()
        cur_indent = raw[:len(raw) - len(stripped)]
        if (item_indent is not None and len(cur_indent) > len(item_indent)
                and cont_indent is None):
            cont_indent = cur_indent
        last = j
    if item_indent is None:
        item_indent = _detect_list_indent(fm_lines)
    if cont_indent is None:
        cont_indent = item_indent + "  "
    insert_at = (last + 1) if last is not None else idx + 1
    lines = []
    for e in new_entries:
        lines.extend(_relasi_entry_lines(e, item_indent, cont_indent, eol))
    return (insert_at, lines, "insert")


def extract_src_url(fm: dict) -> str:
    """URL sumber pertama dokumen, sesuai konvensi entri dokumen_tentang."""
    src = fm.get("sumber")
    url = ""
    if isinstance(src, list) and src and isinstance(src[0], dict):
        url = src[0].get("url") or ""
    elif isinstance(src, dict):
        url = src.get("url") or ""
    elif isinstance(src, str):
        url = src
    return str(url).strip()


# ---------------------------------------------------------------- per file

def process_file(path: Path, rel_path: str, apply_mode: bool) -> dict:
    rec = {"file": rel_path, "status": None, "reason": "",
           "pillars": {}, "excluded": {}, "new_tags": [], "new_entries": []}
    try:
        text = path.read_bytes().decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        rec.update(status="skip", reason="gagal decode UTF-8 (strict)")
        return rec
    except OSError as exc:
        rec.update(status="skip", reason=f"gagal baca: {exc}")
        return rec
    try:
        parts = split_frontmatter(text)
        fm = yaml.safe_load(parts["fm_text"]) or {}
        _validate_parsed(fm)
        keys = scan_keys(parts["fm_lines"])
    except SkipFile as exc:
        rec.update(status="skip", reason=str(exc))
        return rec
    except yaml.YAMLError as exc:
        rec.update(status="skip", reason=f"gagal parse YAML: {exc}")
        return rec

    title = str(fm.get("title") or "")
    description = str(fm.get("description") or "")
    matches = classify(title, description, strip_boilerplate(parts["body"]))
    # v3: pasangan dalam daftar pengecualian tidak dihitung sebagai cocok.
    excluded = {slug: ev for slug, ev in matches.items()
                if (rel_path, slug) in EXCLUDE_FILES}
    matches = {slug: ev for slug, ev in matches.items()
               if (rel_path, slug) not in EXCLUDE_FILES}
    rec["excluded"] = excluded
    if not matches:
        rec.update(status="no_match")
        return rec
    rec["pillars"] = matches

    tags = list(fm.get("tags") or [])
    relasi = list(fm.get("relasi") or [])
    src_url = extract_src_url(fm)
    new_tags, new_entries = [], []
    for slug in matches:
        tag = PILAR_RULES[slug]["tag"]
        if tag not in tags:
            new_tags.append(tag)
        if not any(isinstance(r, dict)
                   and r.get("predikat") == "dokumen_tentang"
                   and r.get("objek") == slug for r in relasi):
            entry = {"predikat": "dokumen_tentang", "objek": slug}
            if src_url:
                entry["sumber"] = src_url
            new_entries.append(entry)
    rec["new_tags"] = new_tags
    rec["new_entries"] = new_entries
    if not new_tags and not new_entries:
        rec.update(status="already_mapped")
        return rec

    try:
        ops = []
        if new_tags:
            ops.append((0, plan_tags_insert(parts["fm_lines"], keys, new_tags, parts["eol"])))
        if new_entries:
            ops.append((1, plan_relasi_insert(parts["fm_lines"], keys, new_entries, parts["eol"])))
    except SkipFile as exc:
        rec.update(status="skip",
                   reason=f"struktur tak terduga ({exc}); cocok pilar: {', '.join(matches)}")
        return rec

    if not apply_mode:
        rec.update(status="would_change")
        return rec

    # --apply: terapkan operasi (sisip/ganti baris, dari indeks terbesar
    # agar indeks yang lebih kecil tetap valid), tulis, lalu verifikasi
    # dengan parse ulang.
    new_fm_lines = list(parts["fm_lines"])
    for _order, (idx, lines, kind) in sorted(ops, key=lambda o: (-o[1][0], -o[0])):
        if kind == "replace":
            new_fm_lines[idx] = lines[0]
        else:
            new_fm_lines[idx:idx] = lines
    new_text = ("".join(parts["lines"][:1]) + "".join(new_fm_lines)
                + "".join(parts["lines"][parts["closing_idx"]:]))
    inserted = sum(len(lines) for _, (_, lines, kind) in ops if kind == "insert")
    try:
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(new_text)
    except OSError as exc:
        rec.update(status="error", reason=f"gagal tulis: {exc}")
        return rec
    ok, problem = _verify_written(path, fm, tags + new_tags, relasi + new_entries,
                                  parts["body"], len(text.splitlines()), inserted)
    if not ok:
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)  # pulihkan byte semula
        rec.update(status="error", reason=f"verifikasi gagal ({problem}); file dipulihkan")
        return rec
    rec.update(status="applied")
    return rec


def _verify_written(path, original_fm, expected_tags, expected_relasi,
                    original_body, original_line_count, inserted):
    """Parse ulang file hasil tulis; harus == semula + tambahan saja."""
    try:
        new_text = path.read_bytes().decode("utf-8", errors="strict")
    except (UnicodeDecodeError, OSError) as exc:
        return False, f"gagal baca ulang: {exc}"
    try:
        parts = split_frontmatter(new_text)
        new_fm = yaml.safe_load(parts["fm_text"]) or {}
    except SkipFile as exc:
        return False, f"frontmatter hasil tulis tidak ter-parse: {exc}"
    except yaml.YAMLError as exc:
        return False, f"frontmatter hasil tulis bukan YAML valid: {exc}"
    if parts["body"] != original_body:
        return False, "badan file berubah"
    if len(new_text.splitlines()) != original_line_count + inserted:
        return False, "jumlah baris tidak sesuai jumlah sisipan"
    expected = dict(original_fm)
    expected["tags"] = expected_tags
    expected["relasi"] = expected_relasi
    if new_fm != expected:
        return False, "frontmatter hasil parse != semula + tambahan"
    return True, ""


# ---------------------------------------------------------------- laporan

def summarize(results):
    matched = [r for r in results if r["pillars"]]
    pillar_stats = {slug: 0 for slug in PILAR_RULES}
    pillar_files = {slug: [] for slug in PILAR_RULES}
    for r in matched:
        for slug in r["pillars"]:
            pillar_stats[slug] += 1
            pillar_files[slug].append(r["file"])
    multi = sum(1 for r in matched if len(r["pillars"]) > 1)
    by_status = {}
    for r in results:
        by_status[r["status"]] = by_status.get(r["status"], 0) + 1
    return {
        "examined": len(results),
        "matched": len(matched),
        "multi": multi,
        "pillar_stats": pillar_stats,
        "pillar_files": pillar_files,
        "by_status": by_status,
        "skips": [r for r in results if r["status"] == "skip"],
        "errors": [r for r in results if r["status"] == "error"],
        "excluded_pairs": sum(len(r["excluded"]) for r in results),
        "excluded": [(r["file"], slug, EXCLUDE_REASONS[(r["file"], slug)],
                      r["excluded"][slug])
                     for r in results for slug in sorted(r["excluded"])],
    }


def _evidence_text(evidence):
    bits = []
    for pat, ev in evidence.items():
        bits.append(f"`{pat}` x{ev['count']} ({', '.join(ev['where'])})")
    return "; ".join(bits)


def write_report(report_path, mode, folders, limit, summary, results, missing_pilars):
    now = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M %Z")
    lines = []
    lines.append("# Laporan klasifikasi — enrich_best_practices.py")
    lines.append("")
    lines.append(f"- Mode: **{mode}**")
    lines.append(f"- Waktu: {now}")
    lines.append(f"- Repo: `{REPO_DIR}`")
    lines.append(f"- Folder: {', '.join(folders)}" + (f" (limit {limit})" if limit else ""))
    lines.append(f"- File dipindai: {summary['examined']}")
    lines.append(f"- File cocok >=1 pilar: {summary['matched']} | multi-pilar: {summary['multi']}")
    for status, count in sorted(summary["by_status"].items()):
        lines.append(f"- Status `{status}`: {count}")
    lines.append(f"- Pasangan dikecualikan: {summary['excluded_pairs']} "
                 "(tidak dihitung sebagai cocok; lihat seksi di bawah)")
    if missing_pilars:
        lines.append("")
        lines.append("**Peringatan:** halaman pilar berikut BELUM ADA di "
                     f"`content/pelajaran/`: {', '.join(missing_pilars)}. "
                     "Relasi yang ditulis akan menunjuk ke target yang tidak eksis.")
    lines.append("")
    lines.append("## Hitungan per pilar")
    lines.append("")
    lines.append("| Pilar | Dokumen |")
    lines.append("|---|---|")
    for slug, count in summary["pillar_stats"].items():
        lines.append(f"| `{slug}` | {count} |")
    lines.append("")
    lines.append("## Skip / gagal")
    lines.append("")
    if summary["skips"]:
        for r in summary["skips"]:
            lines.append(f"- `{r['file']}` — {r['reason']}")
    else:
        lines.append("(tidak ada)")
    if summary["errors"]:
        lines.append("")
        lines.append("### Error tulis/verifikasi")
        lines.append("")
        for r in summary["errors"]:
            lines.append(f"- `{r['file']}` — {r['reason']}")
    lines.append("")
    lines.append("## Pasangan dikecualikan (daftar pengecualian v3)")
    lines.append("")
    if summary["excluded"]:
        for fname, slug, reason, evidence in summary["excluded"]:
            lines.append(f"- `{fname}` :: `{slug}` — {reason} "
                         f"(bukti: {_evidence_text(evidence)})")
    else:
        lines.append("(tidak ada)")
    lines.append("")
    lines.append("## Kecocokan per file (dengan bukti)")
    lines.append("")
    matched = [r for r in results if r["pillars"]]
    if not matched:
        lines.append("(tidak ada)")
    for r in matched:
        lines.append(f"### `{r['file']}` [{r['status']}]")
        for slug, evidence in r["pillars"].items():
            lines.append(f"- pilar `{slug}` — {_evidence_text(evidence)}")
        if r["new_tags"]:
            lines.append(f"- tag baru: {', '.join('`' + t + '`' for t in r['new_tags'])}")
        if r["new_entries"]:
            lines.append("- relasi baru: " + ", ".join(
                f"`dokumen_tentang -> {e['objek']}`" for e in r["new_entries"]))
        lines.append("")
    Path(report_path).write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------- main

def iter_target_files(folders):
    for folder in folders:
        d = CONTENT_DIR / folder
        if not d.exists():
            print(f"peringatan: folder tidak ada, dilewati: {d}", file=sys.stderr)
            continue
        for md in sorted(d.glob("*.md")):
            if md.name == "_index.md":
                continue
            yield folder, md


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Petakan korpus primer ke 6 pilar Best Practices "
                    "(default: dry-run, hanya melapor).")
    parser.add_argument("--apply", action="store_true",
                        help="TULIS perubahan ke frontmatter (default: dry-run).")
    parser.add_argument("--report", metavar="PATH",
                        help="tulis laporan klasifikasi Markdown ke path ini.")
    parser.add_argument("--limit", type=int, metavar="N",
                        help="hanya periksa N file pertama (urut folder + nama).")
    parser.add_argument("--folder", metavar="NAMA", choices=TARGET_DIRS,
                        help="hanya satu folder (untuk rollout bertahap).")
    args = parser.parse_args(argv)

    folders = [args.folder] if args.folder else TARGET_DIRS
    mode = "APPLIED" if args.apply else "DRY-RUN"

    missing_pilars = [slug for slug in PILAR_RULES
                      if not (CONTENT_DIR / "pelajaran" / f"{slug}.md").exists()]
    if missing_pilars:
        print(f"PERINGATAN: halaman pilar belum ada di content/pelajaran/: "
              f"{', '.join(missing_pilars)}", file=sys.stderr)

    results = []
    examined = 0
    for folder, md in iter_target_files(folders):
        if args.limit is not None and examined >= args.limit:
            break
        examined += 1
        results.append(process_file(md, f"{folder}/{md.name}", args.apply))

    summary = summarize(results)
    print(f"[{mode}] File dipindai: {summary['examined']} | "
          f"cocok: {summary['matched']} | multi-pilar: {summary['multi']}")
    for slug, count in summary["pillar_stats"].items():
        print(f"  - {slug}: {count} dokumen")
    for status in ("would_change", "applied", "already_mapped", "no_match", "skip", "error"):
        if summary["by_status"].get(status):
            print(f"  status {status}: {summary['by_status'][status]}")
    if summary["excluded_pairs"]:
        print(f"  pasangan dikecualikan: {summary['excluded_pairs']}")
    for r in summary["skips"]:
        print(f"  SKIP {r['file']}: {r['reason']}")
    for r in summary["errors"]:
        print(f"  ERROR {r['file']}: {r['reason']}", file=sys.stderr)
    if args.report:
        write_report(args.report, mode, folders, args.limit, summary, results, missing_pilars)
        print(f"Laporan ditulis: {args.report}")

    return 1 if summary["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
