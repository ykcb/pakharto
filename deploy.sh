#!/bin/bash
set -e
cd /home/ubuntu/quartz
npx quartz build
rsync -a --delete /home/ubuntu/quartz/public/ /var/www/pakharto.my.id/public/
