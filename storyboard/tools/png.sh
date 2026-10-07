#!/bin/sh
# usage: png.sh previews/shot-1-x.svg -> .png (static render of the exported svg, timeout-guarded)
f="$1"; b="$(pwd)/${f%.svg}"; CH=/opt/pw-browsers/chromium-1194/chrome-linux/chrome
printf '<html><body style="margin:0;background:#0c0f14"><img src="file://%s.svg" width="1200" height="900" style="display:block"></body></html>' "$b" > "$b.html"
timeout 60 $CH --headless --no-sandbox --disable-gpu --hide-scrollbars --window-size=1280,1000 --screenshot="$b.png" "file://$b.html" >/dev/null 2>&1; rm -f "$b.html"; ls "$b.png"
