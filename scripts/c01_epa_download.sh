#!/bin/sh
# download EPA Q2 microdata zips, 1999-2025
cd "$(dirname "$0")/../data/raw/c01/epa_q2" || exit 1
for y in $(seq 1999 2025); do yy=$(printf %02d $((y%100))); f=datos_2t$yy.zip
 [ -s $f ] || curl -s -m 300 -O https://www.ine.es/ftp/microdatos/epa/$f
done
echo done > ../epa_download_done.txt
