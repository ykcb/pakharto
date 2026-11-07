#!/usr/bin/env python3
"""
Generator untuk llms.txt dan llms-full.txt di Wiki Soeharto (pakharto.my.id).
Sesuai standar llmstxt.org dan Fase 4 Cetak Biru Wiki Orde Baru (§14).
"""

from pathlib import Path
import os
import re
import sys
import yaml

REPO_DIR = Path(os.environ.get("PAKHARTO_REPO") or "/home/ubuntu/quartz")
CONTENT_DIR = REPO_DIR / "content"
OUTPUT_DIR = REPO_DIR / "scripts/assets"

LLMS_TXT_HEADER = """# Wiki Soeharto & Sistem Orde Baru (1966–1998)

> Rujukan komprehensif, berbasis data, dan terverifikasi mengenai sistem politik, ekonomi, kelembagaan, dan kehidupan sosial masa Orde Baru Indonesia serta warisannya hari ini.

Situs rujukan publik: https://pakharto.my.id
Repo & Kontribusi: https://github.com/ykcb/pakharto

## Hub Fondasi & Konsep Kunci

- [Orde Baru (1966–1998)](https://pakharto.my.id/hub/orde-baru): Peta isi sistemik, periodisasi kekuasaan, dan mekanisme institusional rezim.
- [Transisi 1965–1967](https://pakharto.my.id/hub/orde-baru#transisi-1965-1967): Titik balik pergantian kekuasaan, Supersemar, pembentukan Kopkamtib, dan pengangkatan Soeharto.
- [Pemilu-pemilu Orde Baru](https://pakharto.my.id/hub/pemilu-orde-baru): Mekanisme elektoral lima tahunan, mobilisasi Korpri/birokrasi, dan hegemoni Golkar.
- [Glosarium Istilah Orde Baru](https://pakharto.my.id/konsep/glosarium-istilah-orde-baru): Dwifungsi ABRI, Demokrasi Pancasila, Trilogi Pembangunan, dan Stabilitas Nasional — empat konsep kunci dalam satu halaman.
- [Soeharto](https://pakharto.my.id/aktor/soeharto): Rekam jejak, jaringan relasi kekuasaan, dan peran sentral Soeharto dalam sistem Orde Baru.
- [Ekonomi Orde Baru](https://pakharto.my.id/hub/ekonomi-orde-baru): Stabilisasi moneter, Repelita, konglomerasi, dan utang luar negeri.
- [Peristiwa Malari 1974](https://pakharto.my.id/peristiwa/malari-1974): Aksi mahasiswa anti-modal asing, kerusuhan Senen, dan pengetatan pers/kampus.
- [Floating Mass](https://pakharto.my.id/konsep/floating-mass): Doktrin depolitisasi pedesaan dan pengebirian partai di akar rumput.
- [KKN](https://pakharto.my.id/konsep/kkn): Anatomi korupsi, kolusi, dan nepotisme yang melandasi tuntutan Reformasi 1998.
- [Kopkamtib](https://pakharto.my.id/lembaga/kopkamtib): Komando keamanan ekstra-yudisial terkuat era Orde Baru.
- [Bakin](https://pakharto.my.id/lembaga/bakin): Badan koordinasi intelijen strategis dan operasi politik Orde Baru.
- [Kehidupan Rakyat & Pembangunan](https://pakharto.my.id/hub/kehidupan-rakyat): Swasembada pangan, revolusi hijau, SD Inpres, KB, Puskesmas, dan dinamika pedesaan.
- [Krisis & Reformasi 1998](https://pakharto.my.id/hub/krisis-dan-reformasi-1998): Krisis moneter, kerusuhan Mei 1998, mundurnya 14 menteri, dan pengunduran diri Soeharto.
- [Peristiwa Tanjung Priok 1984](https://pakharto.my.id/peristiwa/peristiwa-tanjung-priok-1984): Tragedi bentrokan aparat dengan massa berlatar ketegangan asas tunggal.
- [Penembakan Misterius (Petrus)](https://pakharto.my.id/peristiwa/penembakan-misterius-petrus): Operasi penindakan premanisme ekstra-yudisial (1982–1985) dengan metode shock therapy.
- [Kasus Kedung Ombo](https://pakharto.my.id/peristiwa/kasus-kedung-ombo): Konflik agraria penggusuran lahan waduk dan tonggak advokasi HAM akar rumput.
- [Asas Tunggal Pancasila](https://pakharto.my.id/konsep/asas-tunggal-pancasila): Kewajiban formal Pancasila sebagai satu-satunya asas ormas dan parpol lewat Paket UU Politik 1985.

## Dokumen Tambahan & Arsip

- [llms-full.txt](https://pakharto.my.id/llms-full.txt): Teks kurasi lengkap dari seluruh hub fondasi, konsep kunci, lembaga, dan kategori untuk konteks penuh model bahasa.
- [Sitemap](https://pakharto.my.id/sitemap.xml): Peta seluruh halaman wiki, termasuk 1.100+ kliping berita terindeks.
"""

CORE_PAGES = [
    "content/hub/orde-baru.md",
    "content/konsep/glosarium-istilah-orde-baru.md",
    "content/hub/pemilu-orde-baru.md",
    "content/aktor/soeharto.md",
    "content/hub/ekonomi-orde-baru.md",
    "content/peristiwa/malari-1974.md",
    "content/konsep/floating-mass.md",
    "content/konsep/kkn.md",
    "content/lembaga/kopkamtib.md",
    "content/lembaga/bakin.md",
    "content/hub/kehidupan-rakyat.md",
    "content/hub/krisis-dan-reformasi-1998.md",
    "content/peristiwa/peristiwa-tanjung-priok-1984.md",
    "content/peristiwa/penembakan-misterius-petrus.md",
    "content/peristiwa/kasus-kedung-ombo.md",
    "content/konsep/asas-tunggal-pancasila.md"
]


def clean_markdown_for_llm(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\[\[([^\]\|]+)\|([^\]]+)\]\]", r"\2", text)
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)
    return text.strip()


def build():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    missing = [rp for rp in CORE_PAGES if not (REPO_DIR / rp).exists()]
    if missing:
        print("ERROR: halaman CORE hilang, build dihentikan:")
        for rp in missing:
            print(f"  - {rp}")
        sys.exit(1)

    
    llms_txt_path = OUTPUT_DIR / "llms.txt"
    llms_txt_path.write_text(LLMS_TXT_HEADER.strip() + "\n", encoding="utf-8")
    print(f"Generated: {llms_txt_path} ({len(LLMS_TXT_HEADER)} chars)")

    full_sections = [
        "# Wiki Soeharto (pakharto.my.id) — Naskah Konteks Penuh Fondasi Sejarah\n",
        "> Dokumen ini memuat kumpulan naskah lengkap halaman hub, peristiwa milestone, konsep kunci, dan kategori kanonikal untuk inferensi LLM yang akurat.\n"
    ]

    for rel_path in CORE_PAGES:
        file_path = REPO_DIR / rel_path
        if file_path.exists():
            raw = file_path.read_text(encoding="utf-8", errors="replace")
            m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.DOTALL)
            if m:
                fm = yaml.safe_load(m.group(1)) or {}
                body = m.group(2)
            else:
                fm = {}
                body = raw
            
            title = fm.get("title", file_path.stem)
            category = fm.get("kategori", "")
            cleaned_body = clean_markdown_for_llm(body)

            section = (
                f"\n\n{'='*70}\n"
                f"DOKUMEN: {title}\n"
                f"Kategori: {category} | Path: {rel_path}\n"
                f"{'='*70}\n\n"
                f"{cleaned_body}\n"
            )
            full_sections.append(section)


    llms_full_path = OUTPUT_DIR / "llms-full.txt"
    full_content = "".join(full_sections)
    llms_full_path.write_text(full_content.strip() + "\n", encoding="utf-8")
    print(f"Generated: {llms_full_path} ({len(full_content)} chars)")


if __name__ == "__main__":
    build()
