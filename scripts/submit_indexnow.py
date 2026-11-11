#!/usr/bin/env python3
"""
Submit URL yang berubah ke protokol IndexNow (Bing, Yandex, dll.)
Endpoint: https://api.indexnow.org/indexnow
Dijalankan sebagai langkah [8] di akhir deploy.sh (best-effort, fail-safe).
"""

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path

KEY = "a20508eb3c3f5f9d83f340c121a1840c"
HOST = "pakharto.my.id"
KEY_LOCATION = f"https://{HOST}/{KEY}.txt"
INDEXNOW_ENDPOINT = "https://api.indexnow.org/indexnow"

REPO_DIR = Path(__file__).resolve().parent.parent
STATE_FILE = REPO_DIR / ".last-indexnow-commit"
SITEMAP_FILE = REPO_DIR / "public" / "sitemap.xml"
LOG_DIR = REPO_DIR / "logs"
LOG_FILE = LOG_DIR / "indexnow.log"

WIB = timezone(timedelta(hours=7))


def now_str():
    return datetime.now(WIB).strftime("%Y-%m-%d %H:%M:%S WIB")


def log_entry(msg, to_file=True):
    line = f"[{now_str()}] [IndexNow] {msg}"
    print(line)
    if to_file:
        try:
            LOG_DIR.mkdir(parents=True, exist_ok=True)
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except Exception as e:
            print(f"[IndexNow] Gagal menulis log: {e}", file=sys.stderr)


def file_to_url(rel_path):
    """Memetakan path file Markdown di content/ ke URL publik Quartz."""
    p = rel_path.replace("\\", "/").strip()
    if not p.startswith("content/"):
        return None
    p = p.removeprefix("content/")
    if not p.endswith(".md"):
        return None
    p = p.removesuffix(".md")
    if p == "index":
        return f"https://{HOST}/"
    if p.endswith("/_index") or p == "_index":
        folder = p.removesuffix("/_index").removesuffix("_index")
        return f"https://{HOST}/{folder}/" if folder else f"https://{HOST}/"
    return f"https://{HOST}/{p}"


def get_sitemap_urls():
    """Membaca daftar URL kanonikal dari public/sitemap.xml."""
    urls = set()
    if not SITEMAP_FILE.exists():
        log_entry(f"Peringatan: File sitemap {SITEMAP_FILE} tidak ditemukan.", to_file=False)
        return urls
    try:
        tree = ET.parse(SITEMAP_FILE)
        root = tree.getroot()
        for elem in root.iter():
            if elem.tag.endswith("loc") and elem.text:
                urls.add(elem.text.strip())
    except Exception as e:
        log_entry(f"Peringatan: Gagal membaca sitemap.xml: {e}", to_file=False)
    return urls


def submit_to_indexnow(urls):
    """Mengirim batch URL ke IndexNow endpoint. Mengembalikan (sukses: bool, status_code: int, pesan: str)."""
    if not urls:
        return True, 200, "Tidak ada URL untuk dikirim"

    # Protokol membatasi maksimal 10.000 URL per request
    batch = urls[:10000]
    payload = {
        "host": HOST,
        "key": KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": batch
    }
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        INDEXNOW_ENDPOINT,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "IndexNowSubmitter/1.0"
        }
    )

    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            code = r.status
            dur = round(time.time() - t0, 2)
            msg = f"Sukses kirim {len(batch)} URL (HTTP {code}, durasi {dur}s)"
            return True, code, msg
    except urllib.error.HTTPError as e:
        dur = round(time.time() - t0, 2)
        err_body = e.read().decode("utf-8", "replace")[:200]
        msg = f"HTTP {e.code}: {e.reason} ({err_body}) durasi {dur}s"
        return False, e.code, msg
    except Exception as e:
        dur = round(time.time() - t0, 2)
        msg = f"Error jaringan/koneksi: {type(e).__name__} - {e} durasi {dur}s"
        return False, 0, msg


def get_current_head():
    try:
        r = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_DIR, text=True).strip()
        return r
    except Exception:
        return ""


def get_changed_files_since(last_commit):
    """Mendapatkan daftar file yang berubah di content/ sejak last_commit."""
    files = set()
    try:
        # Cek apakah commit masih valid di repo
        subprocess.check_call(
            ["git", "cat-file", "-e", last_commit],
            cwd=REPO_DIR, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    except Exception:
        log_entry(f"Commit lama {last_commit} tidak ditemukan lagi di git, menggunakan fallback sitemap.")
        return None

    try:
        # Diff commit
        out = subprocess.check_output(
            ["git", "diff", "--name-only", last_commit, "HEAD", "--", "content/"],
            cwd=REPO_DIR, text=True
        )
        for line in out.splitlines():
            line = line.strip()
            if line.endswith(".md"):
                files.add(line)

        # Tambahkan juga uncommitted changes jika ada
        out_working = subprocess.check_output(
            ["git", "status", "--porcelain", "--", "content/"],
            cwd=REPO_DIR, text=True
        )
        for line in out_working.splitlines():
            # Format: ' M content/...' atau '?? content/...'
            parts = line.strip().split()
            if len(parts) >= 2:
                path = parts[-1]
                if path.endswith(".md"):
                    files.add(path)
    except Exception as e:
        log_entry(f"Peringatan: Gagal menjalankan git diff: {e}")
        return None

    return sorted(list(files))


def main():
    parser = argparse.ArgumentParser(description="Submit URL ke IndexNow")
    parser.add_argument("--test-url", help="Uji submit satu URL langsung (tanpa mengubah state commit)")
    parser.add_argument("--all", action="store_true", help="Paksa submit seluruh sitemap")
    parser.add_argument("--dry-run", action="store_true", help="Cek URL yang akan dikirim tanpa memanggil API")
    parser.add_argument("--endpoint", help="Ganti endpoint (untuk pengujian kegagalan)")
    args = parser.parse_args()

    global INDEXNOW_ENDPOINT
    if args.endpoint:
        INDEXNOW_ENDPOINT = args.endpoint

    # Mode 1: Uji manual satu URL
    if args.test_url:
        target_url = args.test_url.strip()
        log_entry(f"Mode Uji Manual: Mengirim 1 URL -> {target_url}")
        ok, code, msg = submit_to_indexnow([target_url])
        log_entry(f"Hasil: ok={ok}, status={code}, info={msg}")
        return 0 if ok else 1

    sitemap_urls = get_sitemap_urls()
    head_commit = get_current_head()

    urls_to_submit = []
    is_initial_run = False

    # Mode 2: Force all atau initial run
    if args.all or not STATE_FILE.exists():
        is_initial_run = True
        log_entry(f"Inisialisasi: Mengirim seluruh URL sitemap ({len(sitemap_urls)} URL).")
        urls_to_submit = sorted(list(sitemap_urls))
    else:
        last_commit = ""
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                last_commit = f.read().strip()
        except Exception:
            pass

        if not last_commit:
            is_initial_run = True
            urls_to_submit = sorted(list(sitemap_urls))
        else:
            changed_files = get_changed_files_since(last_commit)
            if changed_files is None:
                # Fallback bila git diff gagal
                log_entry("Fallback ke seluruh sitemap karena diff commit gagal.")
                urls_to_submit = sorted(list(sitemap_urls))
            elif not changed_files:
                log_entry(f"Tidak ada URL content/ yang berubah sejak commit {last_commit[:8]}. Selesai.")
                return 0
            else:
                log_entry(f"Terdeteksi {len(changed_files)} file Markdown berubah sejak commit {last_commit[:8]}.")
                for fpath in changed_files:
                    url = file_to_url(fpath)
                    if not url:
                        continue
                    full_disk_path = REPO_DIR / fpath
                    # Validasi silang dengan sitemap
                    if url in sitemap_urls:
                        urls_to_submit.append(url)
                    elif not full_disk_path.exists():
                        # Halaman dihapus: kirim ke IndexNow agar mesin tahu URL ini hilang
                        urls_to_submit.append(url)
                        log_entry(f"URL dihapus terdeteksi: {url}")
                    else:
                        log_entry(f"Info: {url} tidak ditemukan di sitemap.xml (mungkin draft/private), dilewati.")

    # Deduplikasi
    urls_to_submit = sorted(list(dict.fromkeys(urls_to_submit)))

    if not urls_to_submit:
        log_entry("Tidak ada URL yang memenuhi syarat untuk dikirim.")
        return 0

    log_entry(f"Mempersiapkan pengiriman {len(urls_to_submit)} URL ke {INDEXNOW_ENDPOINT}...")

    if args.dry_run:
        log_entry(f"[DRY-RUN] Daftar URL ({len(urls_to_submit)}):")
        for u in urls_to_submit[:10]:
            print(f"  - {u}")
        if len(urls_to_submit) > 10:
            print(f"  ... dan {len(urls_to_submit) - 10} URL lainnya")
        return 0

    # Eksekusi pengiriman
    ok, code, msg = submit_to_indexnow(urls_to_submit)
    log_entry(f"Hasil submit: {msg}")

    if ok:
        if head_commit:
            try:
                with open(STATE_FILE, "w", encoding="utf-8") as f:
                    f.write(head_commit + "\n")
                log_entry(f"State commit diperbarui ke {head_commit[:8]}.")
            except Exception as e:
                log_entry(f"Peringatan: Gagal memperbarui file state: {e}")
        return 0
    else:
        log_entry(f"Peringatan: Pengiriman IndexNow gagal (kode {code}). State commit tidak diperbarui agar dicoba lagi pada deploy berikutnya.")
        # Kembalikan 0 agar tidak menggagalkan deploy.sh
        return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        log_entry(f"Pengecualian tak terduga di submit_indexnow: {e}")
        sys.exit(0)  # Selalu keluar 0 agar tidak menggagalkan deploy
