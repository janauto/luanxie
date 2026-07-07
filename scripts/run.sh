#!/bin/zsh
# 乱写APP 启动脚本:自动续期 Tailscale 证书(如可用)并以 HTTPS 启动;否则退回 HTTP。
set -e
cd "$(dirname "$0")/.."

UV=/opt/homebrew/bin/uv
PORT="${PORT:-8787}"
CERT_DIR="data/certs"
mkdir -p "$CERT_DIR"

TS=/Applications/Tailscale.app/Contents/MacOS/Tailscale
[ -x "$TS" ] || TS="$(command -v tailscale || true)"

if [ -n "$TS" ] && "$TS" status >/dev/null 2>&1; then
  # MagicDNS 主机名,如 mymac.tailxxxx.ts.net
  HOST=$("$TS" status --json | /usr/bin/python3 -c 'import json,sys; print(json.load(sys.stdin)["Self"]["DNSName"].rstrip("."))')
  if "$TS" cert --cert-file "$CERT_DIR/cert.pem" --key-file "$CERT_DIR/key.pem" "$HOST" 2>/dev/null; then
    echo "HTTPS 模式: https://$HOST:$PORT"
    exec "$UV" run uvicorn server.main:app --host 0.0.0.0 --port "$PORT" \
      --ssl-certfile "$CERT_DIR/cert.pem" --ssl-keyfile "$CERT_DIR/key.pem"
  fi
fi

echo "未检测到 Tailscale,HTTP 模式(手机端录音功能不可用): http://$(ipconfig getifaddr en0 2>/dev/null || echo 127.0.0.1):$PORT"
exec "$UV" run uvicorn server.main:app --host 0.0.0.0 --port "$PORT"
