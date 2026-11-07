#!/usr/bin/env python3
"""Fase otomatis verifikasi kliping (7 Nov 2026).

Untuk tiap kliping di content/perpustakaan-soeharto/:
  1. Ambil teks asli dari WordPress REST API soehartolibrary.id
     (berdasar slug dari sumber.url; slug numerik dicoba sebagai ID).
     Bila API kosong, fallback: unduh halaman sumber.url langsung.
  2. Bandingkan isi kliping dengan teks asli (containment kata:
     berapa % kata kliping yang ada di teks sumber).
  3. Klasifikasi: match / review / mismatch / not_found / dead_link / error.

HANYA membaca content/*.md dan menulis laporan — TIDAK mengubah file
konten. Hasil ditulis incremental ke JSONL (resumable: slug yang sudah
ada dilewati bila skrip dijalankan ulang). Sopan ke server sumber:
delay antar request + retry sekali + User-Agent jelas.
"""
import html
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import yaml

REPO = Path("/home/ubuntu/quartz")
KLIPING = REPO / "content/perpustakaan-soeharto"
OUT = Path("/home/ubuntu/kliping-verify.jsonl")
API_SLUG = "https://soehartolibrary.id/wp-json/wp/v2/posts?slug={}&per_page=5"
API_ID = "https://soehartolibrary.id/wp-json/wp/v2/posts/{}"
UA = {"User-Agent": "Wiki-Soeharto-verifier/1.0 (pakharto.my.id)"}
DELAY = 0.6
TIMEOUT = 25

MATCH_MIN = 0.85
REVIEW_MIN = 0.70


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return resp.status, resp.read().decode("utf-8", errors="ignore")


def strip_html(s):
    s = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    return html.unescape(s)


def normalize_text(s):
    s = strip_html(s)
    s = re.sub(r"!?\[[^\]]*\]\([^)]*\)", " ", s)  # tautan/gambar markdown
    s = re.sub(r"[#>*`_~|]", " ", s)
    return s


def words(s):
    return set(re.findall(r"[a-z0-9]+", normalize_text(s).lower()))


def containment(kliping_text, source_text):
    wk = words(kliping_text)
    ws = words(source_text)
    if not wk:
        return 0.0, 0, 0
    return len(wk & ws) / len(wk), len(wk), len(ws)


def title_match(t1, t2):
    w1, w2 = words(t1), words(t2)
    if not w1 or not w2:
        return False
    return len(w1 & w2) / len(w1) >= 0.8


def get_source(slug, url):
    """Kembalikan (method, http_status, title, text) atau raise."""
    # Slug numerik: coba sebagai ID dulu (slug "108" dst.)
    if slug.isdigit():
        try:
            status, body = fetch(API_ID.format(slug))
            d = json.loads(body)
            if isinstance(d, dict) and d.get("content"):
                return ("api-id", status,
                        strip_html(d.get("title", {}).get("rendered", "")),
                        d["content"]["rendered"])
        except Exception:
            pass
    try:
        status, body = fetch(API_SLUG.format(slug))
        d = json.loads(body)
        if isinstance(d, list) and d:
            post = d[0]
            if post.get("slug") == slug or len(d) == 1:
                return ("api", status,
                        strip_html(post.get("title", {}).get("rendered", "")),
                        post.get("content", {}).get("rendered", ""))
            return ("api-empty", status, "", "")
        return ("api-empty", status, "", "")
    except urllib.error.HTTPError as e:
        if e.code in (404, 410):
            return ("api-empty", e.code, "", "")
        raise
    except Exception:
        # Fallback: halaman HTML sumber langsung
        status, body = fetch(url)
        return ("html", status, "", body)


def main():
    done = {}
    if OUT.exists():
        for line in OUT.read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(line)
                done[r["slug"]] = r
            except Exception:
                pass
    print(f"Melanjutkan: {len(done)} slug sudah diperiksa sebelumnya")

    files = sorted(f for f in KLIPING.glob("*.md") if f.name != "_index.md")
    counts = {"match": 0, "review": 0, "mismatch": 0,
              "not_found": 0, "dead_link": 0, "error": 0}
    for r in done.values():
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1

    out_f = OUT.open("a", encoding="utf-8")
    n = 0
    for f in files:
        text = f.read_text(encoding="utf-8", errors="ignore")
        m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
        fm = yaml.safe_load(m.group(1)) if m else {}
        body = m.group(2) if m else text
        src_url = ""
        for s in fm.get("sumber", []) or []:
            if isinstance(s, dict) and s.get("url"):
                src_url = s["url"]
                break
        slug = src_url.rstrip("/").rsplit("/", 1)[-1] if src_url else ""
        if not slug:
            rec = {"slug": "", "file": f.name, "entity_id": fm.get("entity_id", ""),
                   "verdict": "error", "note": "tanpa sumber.url"}
            out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            out_f.flush()
            counts["error"] += 1
            continue
        if slug in done:
            continue

        verdict, note, cont, method, status = "error", "", 0.0, "", 0
        title_src = ""
        try:
            method, status, title_src, src_text = get_source(slug, src_url)
            if method == "api-empty" or not src_text.strip():
                verdict, note = "not_found", "API kosong / tanpa isi"
            else:
                cont, nk, ns = containment(body, src_text)
                tm = title_match(fm.get("title", ""), title_src) if title_src else None
                if cont >= MATCH_MIN:
                    verdict = "match"
                    note = f"containment {cont:.2f} ({nk} kata kliping vs {ns} kata sumber)"
                elif cont >= REVIEW_MIN:
                    verdict = "review"
                    note = f"containment {cont:.2f} — periksa manual"
                else:
                    verdict = "mismatch"
                    note = f"containment {cont:.2f} — isi jauh berbeda"
                if tm is False and verdict == "match" and cont < 0.92:
                    verdict, note = "review", note + "; judul tidak cocok"
        except urllib.error.HTTPError as e:
            verdict, note, status = "dead_link", f"HTTP {e.code}", e.code
        except Exception as e:
            verdict, note = "error", f"{type(e).__name__}: {e}"
            # Retry sekali setelah jeda
            try:
                time.sleep(5)
                method, status, title_src, src_text = get_source(slug, src_url)
                if src_text.strip():
                    cont, nk, ns = containment(body, src_text)
                    verdict = ("match" if cont >= MATCH_MIN else
                               "review" if cont >= REVIEW_MIN else "mismatch")
                    note = f"containment {cont:.2f} (retry sukses)"
                else:
                    verdict, note = "not_found", "API kosong / tanpa isi (retry)"
            except Exception as e2:
                verdict, note = "error", f"retry gagal: {type(e2).__name__}: {e2}"

        rec = {"slug": slug, "file": f.name,
               "entity_id": fm.get("entity_id", ""),
               "title": fm.get("title", ""),
               "source_url": src_url, "method": method, "http": status,
               "containment": round(cont, 3), "verdict": verdict, "note": note}
        out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        out_f.flush()
        counts[verdict] = counts.get(verdict, 0) + 1
        n += 1
        if n % 50 == 0:
            print(f"  ...{len(done) + n} diperiksa: {counts}", flush=True)
        time.sleep(DELAY)

    out_f.close()
    print("SELESAI:", counts)
    print(f"Laporan: {OUT}")


if __name__ == "__main__":
    main()
