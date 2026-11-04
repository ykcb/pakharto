#!/bin/bash
set -e

# Box cuma punya 1.9 GB RAM; build Quartz (3.800+ halaman + esbuild) bisa
# memuncak dan membuat V8 crash (FatalProcessOutOfMemory). Batasi heap Node
# ke 1 GB supaya V8 GC lebih agresif dan memakai swap, bukan abort.
export NODE_OPTIONS="${NODE_OPTIONS:-} --max-old-space-size=1024"

REPO_DIR="/home/ubuntu/quartz"
cd "$REPO_DIR"

echo "=== [1/4] Generating llms.txt & llms-full.txt ==="
/usr/bin/python3 scripts/build_llms_txt.py

echo "=== [2/4] Building Quartz static pages ==="
npx quartz build

echo "=== [3/4] Copying root assets (robots.txt, llms.txt, llms-full.txt) ==="
cp scripts/assets/robots.txt scripts/assets/llms.txt scripts/assets/llms-full.txt public/

echo "=== [4/4] Deploying to live web root (/var/www/pakharto.my.id/public/) ==="
rsync -a --delete /home/ubuntu/quartz/public/ /var/www/pakharto.my.id/public/

echo "=== DEPLOY SUKSES: pakharto.my.id telah terverifikasi live! ==="
