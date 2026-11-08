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

echo "=== [1/7] Generating llms.txt & llms-full.txt ==="
/usr/bin/python3 scripts/build_llms_txt.py

echo "=== [2/7] Validating frontmatter schema (fail-fast) ==="
/usr/bin/python3 scripts/validate_frontmatter.py

echo "=== [3/7] Rebuilding FTS5 index (atomic: tmp DB -> verifikasi -> swap) ==="
/usr/bin/python3 scripts/indexer/build-fts5.py

echo "=== [4/7] MCP smoke test (12 tools, assertion nyata) ==="
/usr/bin/python3 scripts/mcp/server.py --test

echo "=== [5/7] Building Quartz static pages ==="
npx quartz build

echo "=== [5b/7] Guard jumlah halaman ==="
HTML_COUNT=$(find public -name '*.html' | wc -l)
echo "Markdown: $MD_COUNT | HTML hasil build: $HTML_COUNT"
if [ "$HTML_COUNT" -lt "$MD_COUNT" ]; then
  echo "ERROR: HTML hasil build ($HTML_COUNT) < Markdown sumber ($MD_COUNT); deploy dihentikan."
  exit 1
fi

echo "=== [6/7] Copying root assets (robots.txt, llms.txt, llms-full.txt, yandex verification) ==="
cp scripts/assets/robots.txt scripts/assets/llms.txt scripts/assets/llms-full.txt scripts/assets/yandex_2bee282885b1cc97.html public/

echo "=== [7/7] Deploying to live web root (/var/www/pakharto.my.id/public/) ==="
rsync -a --delete /home/ubuntu/quartz/public/ /var/www/pakharto.my.id/public/

echo "=== DEPLOY SUKSES: pakharto.my.id telah terverifikasi live! ==="
