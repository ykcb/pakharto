#!/usr/bin/env python3
"""HTML hasil crawl -> Markdown siap Quartz, dengan frontmatter + atribusi sumber.

Alur:  out/html/*.html + out/index.jsonl  ->  <quartz>/content/perpustakaan-soeharto/*.md

Pakai:
    python3 html_to_quartz.py --html-dir out/html --index out/index.jsonl \\
        --content-dir ~/quartz/content/perpustakaan-soeharto --limit 5   # uji dulu
    python3 html_to_quartz.py --html-dir out/html --index out/index.jsonl \\
        --content-dir ~/quartz/content/perpustakaan-soeharto            # penuh

Syarat: perintah `markitdown` dari microsoft/markitdown sudah terpasang
(cek: `markitdown --help`). Kalau belum: `pip install markitdown`.

Yang dilakukan per file:
  1. Ambil isi <article>...</article> bila ada (membuang menu/sidebar/footer
     tema WordPress); kalau tidak ada <article>, pakai seluruh HTML.
  2. Konversi ke Markdown lewat `markitdown` (stdin -> stdout).
  3. Tambah frontmatter Quartz: title (dari index.jsonl), source (URL asli),
     date (lastmod sitemap). Judul fallback = slug.
  4. Lewati file yang .md-nya sudah ada (resume, seperti crawler).

Catatan: gambar tetap menunjuk URL asli (hotlink). Mengunduh gambar lokal
adalah tahap terpisah bila nanti mau situs mandiri penuh.
"""

import argparse
import json
import os
import re
import subprocess
import sys

ARTICLE_RE = re.compile(r"<article\b[^>]*>(.*?)</article>", re.S | re.I)


def extract_article(html_text):
    m = ARTICLE_RE.search(html_text)
    return m.group(0) if m else html_text


def markitdown(html_text):
    proc = subprocess.run(["markitdown", "-x", "html"], input=html_text.encode("utf-8"),
                          capture_output=True, timeout=120)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.decode("utf-8", errors="ignore")[:500])
    return proc.stdout.decode("utf-8", errors="replace")


def yaml_quote(value):
    value = (value or "").replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")
    return f'"{value}"'


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--html-dir", required=True)
    ap.add_argument("--index", required=True, help="out/index.jsonl dari crawler")
    ap.add_argument("--content-dir", required=True)
    ap.add_argument("--limit", type=int, default=0, help="0 = semua")
    args = ap.parse_args()

    entries = []
    with open(args.index, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    if args.limit:
        entries = entries[: args.limit]
    os.makedirs(args.content_dir, exist_ok=True)

    ok = fail = skipped = 0
    for i, e in enumerate(entries, 1):
        src = os.path.join(args.html_dir, e["file"])
        md_name = re.sub(r"\.html$", ".md", e["file"])
        dst = os.path.join(args.content_dir, md_name)
        if os.path.exists(dst):
            skipped += 1
            continue
        if not os.path.exists(src):
            print(f"[{i}] HILANG {src}", flush=True)
            fail += 1
            continue
        try:
            with open(src, encoding="utf-8", errors="ignore") as f:
                html_text = f.read()
            md = markitdown(extract_article(html_text)).strip()
            title = e.get("title") or re.sub(r"^\d+-", "", md_name[:-3]).replace("-", " ")
            frontmatter = (
                "---\n"
                f"title: {yaml_quote(title)}\n"
                f"source: {yaml_quote(e['url'])}\n"
                f"date: {yaml_quote(e.get('lastmod') or '')}\n"
                "---\n\n"
            )
            with open(dst, "w", encoding="utf-8") as f:
                f.write(frontmatter + md + "\n")
            ok += 1
        except Exception as exc:  # noqa: BLE001 - catat, lanjut ke file berikut
            print(f"[{i}] GAGAL {e['url']}: {exc}", flush=True)
            fail += 1
        if i % 100 == 0 or i == len(entries):
            print(f"[{i}/{len(entries)}] ok={ok} gagal={fail} dilewati={skipped}", flush=True)

    print(f"SELESAI: ok={ok} gagal={fail} dilewati={skipped}", flush=True)
    print(f"Markdown di {args.content_dir}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
