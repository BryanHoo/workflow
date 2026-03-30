#!/usr/bin/env bash
# 检查 workflow-web-access 的 CDP 依赖，并确保 proxy 可用。

set -u

PORT="${WORKFLOW_WEB_ACCESS_PORT:-${CDP_PROXY_PORT:-3456}}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_FILE="/tmp/workflow-web-access-cdp.log"

# Node.js
if command -v node >/dev/null 2>&1; then
  NODE_VER="$(node --version 2>/dev/null)"
  NODE_MAJOR="$(echo "$NODE_VER" | sed 's/^v//' | cut -d. -f1)"
  if [ "${NODE_MAJOR:-0}" -ge 22 ] 2>/dev/null; then
    echo "node: ok ($NODE_VER)"
  else
    echo "node: warn ($NODE_VER, 建议升级到 22+)"
  fi
else
  echo "node: missing — 请安装 Node.js 22+"
  exit 1
fi

# Chrome 调试端口
if ! CHROME_PORT=$(node -e "
const fs = require('fs');
const path = require('path');
const os = require('os');
const net = require('net');

function checkPort(port) {
  return new Promise((resolve) => {
    const socket = net.createConnection(port, '127.0.0.1');
    const timer = setTimeout(() => { socket.destroy(); resolve(false); }, 2000);
    socket.once('connect', () => { clearTimeout(timer); socket.destroy(); resolve(true); });
    socket.once('error', () => { clearTimeout(timer); resolve(false); });
  });
}

function activePortFiles() {
  const home = os.homedir();
  const localAppData = process.env.LOCALAPPDATA || '';

  switch (process.platform) {
    case 'darwin':
      return [
        path.join(home, 'Library/Application Support/Google/Chrome/DevToolsActivePort'),
        path.join(home, 'Library/Application Support/Google/Chrome Canary/DevToolsActivePort'),
        path.join(home, 'Library/Application Support/Chromium/DevToolsActivePort'),
      ];
    case 'linux':
      return [
        path.join(home, '.config/google-chrome/DevToolsActivePort'),
        path.join(home, '.config/chromium/DevToolsActivePort'),
      ];
    case 'win32':
      return [
        path.join(localAppData, 'Google/Chrome/User Data/DevToolsActivePort'),
        path.join(localAppData, 'Chromium/User Data/DevToolsActivePort'),
      ];
    default:
      return [];
  }
}

(async () => {
  for (const filePath of activePortFiles()) {
    try {
      const lines = fs.readFileSync(filePath, 'utf8').trim().split(/\\r?\\n/).filter(Boolean);
      const port = parseInt(lines[0], 10);
      if (port > 0 && port < 65536 && await checkPort(port)) {
        console.log(port);
        process.exit(0);
      }
    } catch (_) {}
  }

  for (const port of [9222, 9229, 9333]) {
    if (await checkPort(port)) {
      console.log(port);
      process.exit(0);
    }
  }

  process.exit(1);
})();
" 2>/dev/null); then
  echo "chrome: not connected — 请打开 chrome://inspect/#remote-debugging 并勾选 Allow remote debugging"
  exit 1
fi
echo "chrome: ok (port $CHROME_PORT)"

# Proxy
TARGETS="$(curl -s --connect-timeout 3 "http://127.0.0.1:${PORT}/targets" 2>/dev/null)"
if echo "$TARGETS" | grep -q '^\['; then
  echo "proxy: ready (port $PORT)"
  exit 0
fi

echo "proxy: connecting..."
WORKFLOW_WEB_ACCESS_PORT="$PORT" node "$SCRIPT_DIR/cdp-proxy.mjs" >"$LOG_FILE" 2>&1 &
sleep 2

for i in $(seq 1 15); do
  if curl -s --connect-timeout 5 --max-time 8 "http://127.0.0.1:${PORT}/targets" 2>/dev/null | grep -q '^\['; then
    echo "proxy: ready (port $PORT)"
    exit 0
  fi

  if [ "$i" -eq 1 ]; then
    echo "chrome: 如果看到了调试授权弹窗，请点击允许"
  fi
done

echo "proxy: failed — 请检查 Chrome 调试设置，日志见 $LOG_FILE"
exit 1
