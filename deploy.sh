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

echo "=== [1/6] Generating llms.txt & llms-full.txt ==="
/usr/bin/python3 scripts/build_llms_txt.py

echo "=== [2/6] Rebuilding FTS5 index (atomic: tmp DB -> verifikasi -> swap) ==="
/usr/bin/python3 scripts/indexer/build-fts5.py

echo "=== [3/6] MCP smoke test (12 tools, assertion nyata) ==="
/usr/bin/python3 scripts/mcp/server.py --test

echo "=== [4/6] Building Quartz static pages ==="
npx quartz build

echo "=== [4b/6] Guard jumlah halaman ==="
HTML_COUNT=$(find public -name '*.html' | wc -l)
echo "Markdown: $MD_COUNT | HTML hasil build: $HTML_COUNT"
if [ "$HTML_COUNT" -lt "$MD_COUNT" ]; then
  echo "ERROR: HTML hasil build ($HTML_COUNT) < Markdown sumber ($MD_COUNT); deploy dihentikan."
  exit 1
fi

echo "=== [5/6] Copying root assets (robots.txt, llms.txt, llms-full.txt) ==="
cp scripts/assets/robots.txt scripts/assets/llms.txt scripts/assets/llms-full.txt public/

echo "=== [6/6] Deploying to live web root (/var/www/pakharto.my.id/public/) ==="
rsync -a --delete /home/ubuntu/quartz/public/ /var/www/pakharto.my.id/public/

echo "=== DEPLOY SUKSES: pakharto.my.id telah terverifikasi live! ==="
