#!/usr/bin/env python3
"""
Generator untuk llms.txt dan llms-full.txt di Wiki Soeharto (pakharto.my.id).
Sesuai standar llmstxt.org dan Fase 4 Cetak Biru Wiki Orde Baru (§14).
"""

from pathlib import Path
import re
import yaml

REPO_DIR = Path("/home/ubuntu/quartz")
CONTENT_DIR = REPO_DIR / "content"
OUTPUT_DIR = REPO_DIR / "scripts/assets"

LLMS_TXT_HEADER = """# Wiki Soeharto & Sistem Orde Baru (1966–1998)

> Rujukan komprehensif, berbasis data, dan terverifikasi mengenai sistem politik, ekonomi, kelembagaan, dan kehidupan sosial masa Orde Baru Indonesia serta warisannya hari ini.

Situs rujukan publik: https://pakharto.my.id
Repo & Kontribusi: https://github.com/ykcb/pakharto

## Kategori Utama (Taksonomi Resmi)

- [Bagaimana Orde Baru Berkuasa?](https://pakharto.my.id/kategori/kekuasaan-dan-legitimasi): Transisi kekuasaan, legitimasi, pemilu, militer/Dwifungsi ABRI, dan aturan main politik 1966–1998.
- [Siapa Menguasai Ekonomi?](https://pakharto.my.id/kategori/ekonomi-dan-kepemilikan): Pembangunan, konglomerat, BUMN, utang luar negeri, teknokrat, dan konsentrasi kepemilikan modal di era Orde Baru.
- [Siapa Diawasi, Siapa Dibungkam?](https://pakharto.my.id/kategori/keamanan-dan-kebebasan): Keamanan negara, intelijen, pers, Kopkamtib/Bakin, dan penindakan terhadap kritik serta oposisi politik.
- [Bagaimana Rakyat Hidup?](https://pakharto.my.id/kategori/pembangunan-dan-kehidupan): Dinamika pedesaan, buruh, tani, pendidikan (SD Inpres), transmigrasi, kesehatan, dan kehidupan sehari-hari di bawah pembangunan.
- [Bagaimana Orde Baru Berakhir?](https://pakharto.my.id/kategori/krisis-dan-reformasi): Krisis moneter 1997–1998, gerakan mahasiswa dan masyarakat sipil, kejatuhan rezim, dan transisi awal era reformasi.
- [Konsep Kunci](https://pakharto.my.id/kategori/konsep): Penjelas istilah, doktrin politik, instrumen hukum, dan konsep sentral untuk memahami cara kerja sistem Orde Baru.

## Hub Fondasi & Konsep Kunci

- [Orde Baru (1966–1998)](https://pakharto.my.id/hub/orde-baru): Peta isi sistemik, periodisasi kekuasaan, dan mekanisme institusional rezim.
- [Transisi 1965–1967](https://pakharto.my.id/peristiwa/transisi-1965-1967): Titik balik pergantian kekuasaan, Supersemar, pembentukan Kopkamtib, dan pengangkatan Soeharto.
- [Pemilu-pemilu Orde Baru](https://pakharto.my.id/hub/pemilu-orde-baru): Mekanisme elektoral lima tahunan, mobilisasi Korpri/birokrasi, dan hegemoni Golkar.
- [Dwifungsi ABRI](https://pakharto.my.id/konsep/dwifungsi-abri): Doktrin peran ganda militer sebagai kekuatan pertahanan dan kekuatan sosial-politik kenegaraan.
- [Demokrasi Pancasila](https://pakharto.my.id/konsep/demokrasi-pancasila): Format politik fusi partai, asas tunggal, dan penertiban musyawarah mufakat.
- [Trilogi Pembangunan](https://pakharto.my.id/konsep/trilogi-pembangunan): Doktrin pembangunan terencana: Stabilitas Nasional, Pertumbuhan Ekonomi, dan Pemerataan.
- [Stabilitas Nasional](https://pakharto.my.id/konsep/stabilitas-nasional): Doktrin keamanan sebagai prasyarat mutlak kelancaran pembangunan ekonomi.
- [Soeharto](https://pakharto.my.id/aktor/soeharto): Rekam jejak, jaringan relasi kekuasaan, dan peran sentral Soeharto dalam sistem Orde Baru.

## Dokumen Tambahan & Arsip

- [llms-full.txt](https://pakharto.my.id/llms-full.txt): Teks kurasi lengkap dari seluruh hub fondasi, konsep kunci, dan kategori untuk konteks penuh model bahasa.
- [Sitemap](https://pakharto.my.id/sitemap.xml): Peta seluruh 2.700+ artikel pidato, peristiwa, dan kliping berita terindeks.
"""

CORE_PAGES = [
    "content/kategori/kekuasaan-dan-legitimasi.md",
    "content/kategori/ekonomi-dan-kepemilikan.md",
    "content/kategori/keamanan-dan-kebebasan.md",
    "content/kategori/pembangunan-dan-kehidupan.md",
    "content/kategori/krisis-dan-reformasi.md",
    "content/kategori/konsep.md",
    "content/hub/orde-baru.md",
    "content/peristiwa/transisi-1965-1967.md",
    "content/hub/pemilu-orde-baru.md",
    "content/konsep/dwifungsi-abri.md",
    "content/konsep/demokrasi-pancasila.md",
    "content/konsep/trilogi-pembangunan.md",
    "content/konsep/stabilitas-nasional.md",
    "content/aktor/soeharto.md"
]


def clean_markdown_for_llm(text: str) -> str:
    # Hilangkan tags HTML berlebih
    text = re.sub(r'<[^>]+>', '', text)
    # Ubah wikilink [[Target|Alias]] -> Alias atau [[Target]] -> Target
    text = re.sub(r'\[\[([^\]\|]+)\|([^\]]+)\]\]', r'\2', text)
    text = re.sub(r'\[\[([^\]]+)\]\]', r'\1', text)
    return text.strip()


def build():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Tulis llms.txt
    llms_txt_path = OUTPUT_DIR / "llms.txt"
    llms_txt_path.write_text(LLMS_TXT_HEADER.strip() + "\n", encoding="utf-8")
    print(f"Generated: {llms_txt_path} ({len(LLMS_TXT_HEADER)} chars)")

    # 2. Tulis llms-full.txt
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
        else:
            print(f"Warning: {file_path} not found, skipped.")

    llms_full_path = OUTPUT_DIR / "llms-full.txt"
    full_content = "".join(full_sections)
    llms_full_path.write_text(full_content.strip() + "\n", encoding="utf-8")
    print(f"Generated: {llms_full_path} ({len(full_content)} chars)")


if __name__ == "__main__":
    build()
