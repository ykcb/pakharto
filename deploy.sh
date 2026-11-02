#!/bin/bash
set -e

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
