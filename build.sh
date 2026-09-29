#!/usr/bin/env sh
# Cloudflare Pages build. Only publish HTML, generated data, and intended static assets.
set -eu
mkdir -p dist
cp index.html eldovant-data.js dist/
if [ -d assets ]; then cp -R assets dist/; fi
if [ -f robots.txt ]; then cp robots.txt dist/; fi
