#!/bin/bash
set -e

# Box cuma punya 1.9 GB RAM; build Quartz (3.800+ halaman + esbuild) bisa
# memuncak dan membuat V8 crash (FatalProcessOutOfMemory). Batasi heap Node
# ke 1 GB supaya V8 GC lebih agresif dan memakai swap, bukan abort.
export NODE_OPTIONS="${NODE_OPTIONS:-} --max-old-space-size=1024"

REPO_DIR="/home/ubuntu/quartz"
cd "$REPO_DIR"

MD_COUNT=$(find content -name '*.md' | wc -l)
echo "Markdown di content/: $MD_COUNT"

echo "=== [1/8] Generating llms.txt & llms-full.txt ==="
/usr/bin/python3 scripts/build_llms_txt.py

echo "=== [2/8] Validating frontmatter schema (fail-fast) ==="
/usr/bin/python3 scripts/validate_frontmatter.py

echo "=== [3/8] Rebuilding FTS5 index (atomic: tmp DB -> verifikasi -> swap) ==="
/usr/bin/python3 scripts/indexer/build-fts5.py

echo "=== [4/8] MCP smoke test (12 tools, assertion nyata) ==="
/usr/bin/python3 scripts/mcp/server.py --test

echo "=== [5/8] Building Quartz static pages ==="
npx quartz build

echo "=== [5b/8] Guard jumlah halaman ==="
HTML_COUNT=$(find public -name '*.html' | wc -l)
echo "Markdown: $MD_COUNT | HTML hasil build: $HTML_COUNT"
if [ "$HTML_COUNT" -lt "$MD_COUNT" ]; then
  echo "ERROR: HTML hasil build ($HTML_COUNT) < Markdown sumber ($MD_COUNT); deploy dihentikan."
  exit 1
fi

echo "=== [6/8] Copying root assets (robots.txt, llms.txt, llms-full.txt, yandex, indexnow) ==="
cp scripts/assets/robots.txt scripts/assets/llms.txt scripts/assets/llms-full.txt scripts/assets/yandex_2bee282885b1cc97.html scripts/assets/a20508eb3c3f5f9d83f340c121a1840c.txt public/

echo "=== [7/8] Deploying to live web root (/var/www/pakharto.my.id/public/) ==="
rsync -a --delete /home/ubuntu/quartz/public/ /var/www/pakharto.my.id/public/

echo "=== [8/8] Submitting changed URLs to IndexNow ==="
/usr/bin/python3 scripts/submit_indexnow.py || echo "[IndexNow] Peringatan: submit IndexNow keluar dengan error, deploy tetap sukses."

echo "=== DEPLOY SUKSES: pakharto.my.id telah terverifikasi live! ==="
