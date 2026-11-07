#!/usr/bin/env python3
"""Validator skema frontmatter Wiki Soeharto (audit ChatGPT, batch 3).

Memeriksa setiap content/*.md: bentuk relasi harus predikat/objek
(bukan type/target), predikat harus dari kosakata terkontrol, kategori
harus 6 slug kanonikal, entity_type dari kosakata resmi, dan field
confidence/risiko/status/verification_status dari enum yang diizinkan.
Dipakai di CI dan di deploy.sh (fail-fast sebelum rebuild FTS).

Keluar 1 bila ada error; warning (mis. status kosong) tidak menggagalkan.
"""
import os
import re
import sys
from pathlib import Path
import yaml

REPO = Path(os.environ.get("PAKHARTO_REPO") or "/home/ubuntu/quartz")
CONTENT = REPO / "content"

CANONICAL_CATEGORIES = {
    "kekuasaan-dan-legitimasi", "ekonomi-dan-kepemilikan",
    "keamanan-dan-kebebasan", "pembangunan-dan-kehidupan",
    "krisis-dan-reformasi", "konsep",
}
ENTITY_TYPES = {
    "aktor", "peristiwa", "organisasi", "pelajaran",
    "konsep", "topik", "kliping",
}
# Kosakata predikat terkontrol: yang sudah dipakai konten + yang
# disarankan audit (§5 handoff). Relasi dokumen arsip memakai
# dokumen_tentang, bukan terkait_dengan yang generik.
ALLOWED_PREDIKAT = {
    "terkait_dengan", "bagian_dari", "dipimpin_oleh", "memimpin",
    "menerbitkan", "diterapkan_oleh", "berakar_dari", "memicu_peristiwa",
    "ditentang_oleh", "memuat_hub", "dokumen_tentang",
    "berisi_konsep", "berisi_hub", "berisi_peristiwa",
    "terlibat_dalam", "menunjuk", "didukung_oleh", "menentang",
    "anggota_dari", "menyebut",
}
CONFIDENCE = {"low", "medium", "high"}
RISIKO = {"rendah", "sedang", "tinggi"}
STATUS = {"", "unreviewed", "source_checked", "cross_checked",
          "disputed", "needs_review", "draft", "verified", "draf"}
VERIFICATION_STATUS = {"verified", "unreviewed", "source_checked",
                       "cross_checked", "disputed", "needs_review"}


def main():
    errors = []
    warnings = []
    n_files = 0
    for f in sorted(CONTENT.rglob("*.md")):
        n_files += 1
        text = f.read_text(encoding="utf-8", errors="ignore")
        m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
        if not m:
            errors.append(f"{f.relative_to(REPO)}: tanpa frontmatter")
            continue
        try:
            fm = yaml.safe_load(m.group(1)) or {}
        except Exception as e:
            errors.append(f"{f.relative_to(REPO)}: YAML frontmatter rusak: {e}")
            continue
        rel = str(f.relative_to(REPO))

        et = fm.get("entity_type")
        if et is not None and str(et) not in ENTITY_TYPES:
            errors.append(f"{rel}: entity_type tidak dikenal: {et!r}")

        kat = fm.get("kategori")
        if kat:
            if str(kat) not in CANONICAL_CATEGORIES:
                errors.append(f"{rel}: kategori bukan slug kanonikal: {kat!r}")
        for kat2 in fm.get("kategori_tambahan", []) or []:
            if str(kat2) not in CANONICAL_CATEGORIES:
                errors.append(f"{rel}: kategori_tambahan bukan slug kanonikal: {kat2!r}")

        conf = fm.get("confidence")
        if conf is not None and str(conf) not in CONFIDENCE:
            errors.append(f"{rel}: confidence tidak dikenal: {conf!r}")
        risiko = fm.get("risiko_editorial")
        if risiko is not None and str(risiko) not in RISIKO:
            errors.append(f"{rel}: risiko_editorial tidak dikenal: {risiko!r}")
        status = fm.get("status")
        if status is not None and str(status) not in STATUS:
            errors.append(f"{rel}: status tidak dikenal: {status!r}")
        elif status in ("", None):
            warnings.append(f"{rel}: status kosong")
        vs = fm.get("verification_status")
        if vs is not None and str(vs) not in VERIFICATION_STATUS:
            errors.append(f"{rel}: verification_status tidak dikenal: {vs!r}")

        rels = fm.get("relasi", [])
        if rels is None:
            continue
        if not isinstance(rels, list):
            errors.append(f"{rel}: relasi bukan daftar")
            continue
        for r in rels:
            if not isinstance(r, dict):
                errors.append(f"{rel}: entri relasi bukan dict: {r!r}")
                continue
            if "type" in r or "target" in r:
                errors.append(f"{rel}: relasi masih memakai type/target "
                              f"(harus predikat/objek): {r!r}")
                continue
            pred = r.get("predikat")
            obj = r.get("objek")
            if not pred or not obj:
                errors.append(f"{rel}: relasi tanpa predikat/objek: {r!r}")
                continue
            if str(pred) not in ALLOWED_PREDIKAT:
                errors.append(f"{rel}: predikat di luar kosakata: {pred!r}")

        for s in fm.get("sumber", []) or []:
            if isinstance(s, dict) and not s.get("url") and not s.get("judul"):
                errors.append(f"{rel}: entri sumber tanpa url maupun judul: {s!r}")

    print(f"Validasi frontmatter: {n_files} file, "
          f"{len(errors)} error, {len(warnings)} warning")
    for e in errors[:20]:
        print(f"  ERROR: {e}")
    if len(errors) > 20:
        print(f"  ... dan {len(errors) - 20} error lain")
    for w in warnings[:10]:
        print(f"  warning: {w}")
    if len(warnings) > 10:
        print(f"  ... dan {len(warnings) - 10} warning lain")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
