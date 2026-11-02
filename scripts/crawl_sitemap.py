#!/usr/bin/env python3
"""Tarik semua URL dari sitemap WordPress, lalu unduh tiap halaman secara sopan.

Contoh pakai (dari folder script ini):
    python3 crawl_sitemap.py --limit 20          # uji coba 20 URL dulu
    python3 crawl_sitemap.py                     # penuh: ~19.384 URL soehartolibrary.id

Hanya memakai pustaka standar Python (tanpa pip install).
Hasil:
    out/index.jsonl   -- satu baris JSON per URL: url, file, status, judul
    out/html/<slug>.html -- HTML mentah tiap halaman (untuk ekstraksi teks tahap berikut)

Perilaku sopan (penting untuk situs kecil seperti ini):
    - jeda antar request (default 1 detik, atur --delay)
    - satu request dalam satu waktu, tanpa paralel
    - retry 3x dengan backoff kalau kena 429/5xx
    - bisa dilanjutkan (resume): file yang sudah ada dilewati
    - berhenti bersih dengan Ctrl+C, jalankan lagi untuk lanjut

Perkiraan waktu untuk 19.384 URL:
    delay 1,0 dtk -> ~6-7 jam | delay 0,5 dtk -> ~3-4 jam
    Jalankan di latar:  nohup python3 crawl_sitemap.py > crawl.log 2>&1 &
"""

import argparse
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

USER_AGENT = "SoehartoLibrary-Research/1.0 (kontak: peneliti pribadi; tarik sopan 1 req/detik)"
NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}


def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def sitemap_urls(xml_bytes):
    """Kembalikan daftar (loc, lastmod) dari sebuah sitemap / sitemap index."""
    root = ET.fromstring(xml_bytes)
    out = []
    for node in root:
        tag = node.tag.split("}")[-1]
        if tag not in ("url", "sitemap"):
            continue
        loc = lastmod = None
        for child in node:
            name = child.tag.split("}")[-1]
            if name == "loc":
                loc = (child.text or "").strip()
            elif name == "lastmod":
                lastmod = (child.text or "").strip()
        if loc:
            out.append((loc, lastmod))
    return out


def slug_from_url(url):
    slug = url.rstrip("/").rsplit("/", 1)[-1] or "beranda"
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", slug)[:150]
    return slug or "tanpa-nama"


def extract_title(html_bytes):
    try:
        text = html_bytes.decode("utf-8", errors="ignore")
    except Exception:
        return None
    m = re.search(r"<title[^>]*>(.*?)</title>", text, re.S | re.I)
    if not m:
        return None
    return html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip() or None


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sitemap", default="https://soehartolibrary.id/wp-sitemap.xml")
    ap.add_argument("--out", default="out")
    ap.add_argument("--delay", type=float, default=1.0, help="jeda detik antar request")
    ap.add_argument("--limit", type=int, default=0, help="0 = semua URL")
    ap.add_argument("--only-posts", action="store_true", default=True,
                    help="hanya sitemap posts-post-* (bukan tag/kategori)")
    args = ap.parse_args()

    html_dir = os.path.join(args.out, "html")
    os.makedirs(html_dir, exist_ok=True)
    index_path = os.path.join(args.out, "index.jsonl")

    print(f"[1/3] Membaca sitemap induk: {args.sitemap}", flush=True)
    submaps = sitemap_urls(fetch(args.sitemap))
    print(f"      {len(submaps)} sub-sitemap ditemukan", flush=True)

    urls = []
    for sm_url, _ in submaps:
        if args.only_posts and "posts-post-" not in sm_url:
            continue
        try:
            entries = sitemap_urls(fetch(sm_url))
        except Exception as e:  # noqa: BLE001 - laporkan, lanjut ke file berikut
            print(f"      GAGAL {sm_url}: {e}", flush=True)
            continue
        urls.extend(entries)
        print(f"      {sm_url.rsplit('/', 1)[-1]}: {len(entries)} URL", flush=True)
        time.sleep(args.delay)

    # Buang duplikat, jaga urutan.
    seen, uniq = set(), []
    for u, lm in urls:
        if u not in seen:
            seen.add(u)
            uniq.append((u, lm))
    if args.limit:
        uniq = uniq[: args.limit]
    print(f"[2/3] Total URL unik yang akan diunduh: {len(uniq)}", flush=True)

    done = set()
    if os.path.exists(index_path):
        with open(index_path, encoding="utf-8") as f:
            for line in f:
                try:
                    done.add(json.loads(line)["url"])
                except Exception:  # noqa: BLE001 - baris rusak dilewati
                    pass
    print(f"      sudah selesai sebelumnya (resume): {len(done)}", flush=True)

    ok = fail = skipped = 0
    with open(index_path, "a", encoding="utf-8") as idx:
        for i, (url, lastmod) in enumerate(uniq, 1):
            if url in done:
                skipped += 1
                continue
            fname = f"{i:05d}-{slug_from_url(url)}.html"
            fpath = os.path.join(html_dir, fname)
            status, title, err = None, None, None
            for attempt in range(4):  # 1 percobaan + 3 retry
                try:
                    data = fetch(url)
                    with open(fpath, "wb") as f:
                        f.write(data)
                    status, title = 200, extract_title(data)
                    break
                except urllib.error.HTTPError as e:
                    status, err = e.code, str(e)
                    if e.code in (429, 500, 502, 503, 504) and attempt < 3:
                        time.sleep(args.delay * (2 ** attempt) * 5)
                        continue
                    break
                except Exception as e:  # noqa: BLE001 - jaringan/timeout/dns
                    status, err = 0, str(e)
                    if attempt < 3:
                        time.sleep(args.delay * (2 ** attempt) * 5)
                        continue
                    break
            idx.write(json.dumps({"url": url, "lastmod": lastmod, "file": fname,
                                  "status": status, "title": title, "error": err},
                                 ensure_ascii=False) + "\n")
            idx.flush()
            if status == 200:
                ok += 1
            else:
                fail += 1
            if i % 100 == 0 or i == len(uniq):
                print(f"[{i}/{len(uniq)}] ok={ok} gagal={fail} dilewati={skipped}", flush=True)
            time.sleep(args.delay)

    print(f"[3/3] SELESAI: ok={ok} gagal={fail} dilewati={skipped}", flush=True)
    print(f"      HTML di {html_dir}, indeks di {index_path}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
