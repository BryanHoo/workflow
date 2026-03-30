#!/usr/bin/env node
// workflow-web-access 的本地 CDP proxy。
// 作用：通过 HTTP API 操控用户本机 Chrome，并复用日常登录态。

import http from 'node:http';
import { URL } from 'node:url';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import net from 'node:net';

const PORT = parseInt(process.env.WORKFLOW_WEB_ACCESS_PORT || process.env.CDP_PROXY_PORT || '3456', 10);
let ws = null;
let cmdId = 0;
const pending = new Map(); // id -> { resolve, timer }
const sessions = new Map(); // targetId -> sessionId

let WS;
if (typeof globalThis.WebSocket !== 'undefined') {
  WS = globalThis.WebSocket;
} else {
  try {
    WS = (await import('ws')).default;
  } catch {
    console.error('[workflow-web-access] Node.js 版本 < 22 且未安装 ws 模块');
    console.error('[workflow-web-access] 解决方案：升级到 Node.js 22+ 或执行 npm install -g ws');
    process.exit(1);
  }
}

async function discoverChromePort() {
  const possiblePaths = [];
  const platform = os.platform();

  if (platform === 'darwin') {
    const home = os.homedir();
    possiblePaths.push(
      path.join(home, 'Library/Application Support/Google/Chrome/DevToolsActivePort'),
      path.join(home, 'Library/Application Support/Google/Chrome Canary/DevToolsActivePort'),
      path.join(home, 'Library/Application Support/Chromium/DevToolsActivePort'),
    );
  } else if (platform === 'linux') {
    const home = os.homedir();
    possiblePaths.push(
      path.join(home, '.config/google-chrome/DevToolsActivePort'),
      path.join(home, '.config/chromium/DevToolsActivePort'),
    );
  } else if (platform === 'win32') {
    const localAppData = process.env.LOCALAPPDATA || '';
    possiblePaths.push(
      path.join(localAppData, 'Google/Chrome/User Data/DevToolsActivePort'),
      path.join(localAppData, 'Chromium/User Data/DevToolsActivePort'),
    );
  }

  for (const candidate of possiblePaths) {
    try {
      const content = fs.readFileSync(candidate, 'utf8').trim();
      const lines = content.split('\n');
      const port = parseInt(lines[0], 10);
      if (port > 0 && port < 65536) {
        const ok = await checkPort(port);
        if (ok) {
          const wsPath = lines[1] || null;
          console.log(`[workflow-web-access] 从 DevToolsActivePort 发现 Chrome: ${port}${wsPath ? ' (带 wsPath)' : ''}`);
          return { port, wsPath };
        }
      }
    } catch {
      // ignore and continue
    }
  }

  for (const port of [9222, 9229, 9333]) {
    if (await checkPort(port)) {
      console.log(`[workflow-web-access] 扫描发现 Chrome 调试端口: ${port}`);
      return { port, wsPath: null };
    }
  }

  return null;
}

function checkPort(port) {
  return new Promise((resolve) => {
    const socket = net.createConnection(port, '127.0.0.1');
    const timer = setTimeout(() => {
      socket.destroy();
      resolve(false);
    }, 2000);

    socket.once('connect', () => {
      clearTimeout(timer);
      socket.destroy();
      resolve(true);
    });

    socket.once('error', () => {
      clearTimeout(timer);
      resolve(false);
    });
  });
}

function getWebSocketUrl(port, wsPath) {
  if (wsPath) return `ws://127.0.0.1:${port}${wsPath}`;
  return `ws://127.0.0.1:${port}/devtools/browser`;
}

let chromePort = null;
let chromeWsPath = null;
let connectingPromise = null;

async function connect() {
  if (ws && (ws.readyState === WS.OPEN || ws.readyState === 1)) return;
  if (connectingPromise) return connectingPromise;

  if (!chromePort) {
    const discovered = await discoverChromePort();
    if (!discovered) {
      throw new Error(
        'Chrome 未开启远程调试端口。请打开 chrome://inspect/#remote-debugging 并勾选 Allow remote debugging。'
      );
    }
    chromePort = discovered.port;
    chromeWsPath = discovered.wsPath;
  }

  const wsUrl = getWebSocketUrl(chromePort, chromeWsPath);
  if (!wsUrl) throw new Error('无法获取 Chrome WebSocket URL');

  return connectingPromise = new Promise((resolve, reject) => {
    ws = new WS(wsUrl);

    const onOpen = () => {
      cleanup();
      connectingPromise = null;
      console.log(`[workflow-web-access] 已连接 Chrome (端口 ${chromePort})`);
      resolve();
    };

    const onError = (event) => {
      cleanup();
      connectingPromise = null;
      const message = event.message || event.error?.message || '连接失败';
      console.error('[workflow-web-access] 连接错误:', message);
      reject(new Error(message));
    };

    const onClose = () => {
      console.log('[workflow-web-access] 连接断开');
      ws = null;
      chromePort = null;
      chromeWsPath = null;
      sessions.clear();
    };

    const onMessage = (event) => {
      const raw = typeof event === 'string' ? event : (event.data || event);
      const message = JSON.parse(typeof raw === 'string' ? raw : raw.toString());

      if (message.method === 'Target.attachedToTarget') {
        const { sessionId, targetInfo } = message.params;
        sessions.set(targetInfo.targetId, sessionId);
      }

      if (message.id && pending.has(message.id)) {
        const { resolve: finish, timer } = pending.get(message.id);
        clearTimeout(timer);
        pending.delete(message.id);
        finish(message);
      }
    };

    function cleanup() {
      ws.removeEventListener?.('open', onOpen);
      ws.removeEventListener?.('error', onError);
    }

    if (ws.on) {
      ws.on('open', onOpen);
      ws.on('error', onError);
      ws.on('close', onClose);
      ws.on('message', onMessage);
    } else {
      ws.addEventListener('open', onOpen);
      ws.addEventListener('error', onError);
      ws.addEventListener('close', onClose);
      ws.addEventListener('message', onMessage);
    }
  });
}

function sendCDP(method, params = {}, sessionId = null) {
  return new Promise((resolve, reject) => {
    if (!ws || (ws.readyState !== WS.OPEN && ws.readyState !== 1)) {
      reject(new Error('WebSocket 未连接'));
      return;
    }

    const id = ++cmdId;
    const payload = { id, method, params };
    if (sessionId) payload.sessionId = sessionId;

    const timer = setTimeout(() => {
      pending.delete(id);
      reject(new Error(`CDP 命令超时: ${method}`));
    }, 30000);

    pending.set(id, { resolve, timer });
    ws.send(JSON.stringify(payload));
  });
}

async function ensureSession(targetId) {
  if (sessions.has(targetId)) return sessions.get(targetId);

  const response = await sendCDP('Target.attachToTarget', { targetId, flatten: true });
  if (response.result?.sessionId) {
    sessions.set(targetId, response.result.sessionId);
    return response.result.sessionId;
  }

  throw new Error(`attach 失败: ${JSON.stringify(response.error)}`);
}

async function waitForLoad(sessionId, timeoutMs = 15000) {
  await sendCDP('Page.enable', {}, sessionId);

  return new Promise((resolve) => {
    let resolved = false;

    const finish = (result) => {
      if (resolved) return;
      resolved = true;
      clearTimeout(timer);
      clearInterval(interval);
      resolve(result);
    };

    const timer = setTimeout(() => finish('timeout'), timeoutMs);
    const interval = setInterval(async () => {
      try {
        const response = await sendCDP(
          'Runtime.evaluate',
          {
            expression: 'document.readyState',
            returnByValue: true,
          },
          sessionId,
        );

        if (response.result?.result?.value === 'complete') {
          finish('complete');
        }
      } catch {
        // ignore and keep waiting
      }
    }, 500);
  });
}

async function readBody(req) {
  let body = '';
  for await (const chunk of req) body += chunk;
  return body;
}

const server = http.createServer(async (req, res) => {
  const parsed = new URL(req.url, `http://127.0.0.1:${PORT}`);
  const pathname = parsed.pathname;
  const query = Object.fromEntries(parsed.searchParams);

  res.setHeader('Content-Type', 'application/json; charset=utf-8');

  try {
    if (pathname === '/health') {
      const connected = ws && (ws.readyState === WS.OPEN || ws.readyState === 1);
      res.end(JSON.stringify({ status: 'ok', connected, sessions: sessions.size, chromePort }));
      return;
    }

    await connect();

    if (pathname === '/targets') {
      const response = await sendCDP('Target.getTargets');
      const pages = response.result.targetInfos.filter((target) => target.type === 'page');
      res.end(JSON.stringify(pages, null, 2));
      return;
    }

    if (pathname === '/new') {
      const targetUrl = query.url || 'about:blank';
      const response = await sendCDP('Target.createTarget', { url: targetUrl, background: true });
      const targetId = response.result.targetId;

      if (targetUrl !== 'about:blank') {
        try {
          const sessionId = await ensureSession(targetId);
          await waitForLoad(sessionId);
        } catch {
          // 页面等待失败不阻断 tab 返回
        }
      }

      res.end(JSON.stringify({ targetId }));
      return;
    }

    if (pathname === '/close') {
      const response = await sendCDP('Target.closeTarget', { targetId: query.target });
      sessions.delete(query.target);
      res.end(JSON.stringify(response.result));
      return;
    }

    if (pathname === '/navigate') {
      const sessionId = await ensureSession(query.target);
      const response = await sendCDP('Page.navigate', { url: query.url }, sessionId);
      await waitForLoad(sessionId);
      res.end(JSON.stringify(response.result));
      return;
    }

    if (pathname === '/back') {
      const sessionId = await ensureSession(query.target);
      await sendCDP('Runtime.evaluate', { expression: 'history.back()' }, sessionId);
      await waitForLoad(sessionId);
      res.end(JSON.stringify({ ok: true }));
      return;
    }

    if (pathname === '/eval') {
      const sessionId = await ensureSession(query.target);
      const body = await readBody(req);
      const expression = body || query.expr || 'document.title';
      const response = await sendCDP(
        'Runtime.evaluate',
        {
          expression,
          returnByValue: true,
          awaitPromise: true,
        },
        sessionId,
      );

      if (response.result?.result?.value !== undefined) {
        res.end(JSON.stringify({ value: response.result.result.value }));
        return;
      }

      if (response.result?.exceptionDetails) {
        res.statusCode = 400;
        res.end(JSON.stringify({ error: response.result.exceptionDetails.text }));
        return;
      }

      res.end(JSON.stringify(response.result));
      return;
    }

    if (pathname === '/click') {
      const sessionId = await ensureSession(query.target);
      const selector = await readBody(req);
      if (!selector) {
        res.statusCode = 400;
        res.end(JSON.stringify({ error: 'POST body 需要 CSS 选择器' }));
        return;
      }

      const selectorJson = JSON.stringify(selector);
      const js = `(() => {
        const el = document.querySelector(${selectorJson});
        if (!el) return { error: '未找到元素: ' + ${selectorJson} };
        el.scrollIntoView({ block: 'center' });
        el.click();
        return { clicked: true, tag: el.tagName, text: (el.textContent || '').slice(0, 100) };
      })()`;

      const response = await sendCDP(
        'Runtime.evaluate',
        {
          expression: js,
          returnByValue: true,
          awaitPromise: true,
        },
        sessionId,
      );

      const value = response.result?.result?.value;
      if (value?.error) {
        res.statusCode = 400;
        res.end(JSON.stringify(value));
        return;
      }

      res.end(JSON.stringify(value || response.result));
      return;
    }

    if (pathname === '/clickAt') {
      const sessionId = await ensureSession(query.target);
      const selector = await readBody(req);
      if (!selector) {
        res.statusCode = 400;
        res.end(JSON.stringify({ error: 'POST body 需要 CSS 选择器' }));
        return;
      }

      const selectorJson = JSON.stringify(selector);
      const js = `(() => {
        const el = document.querySelector(${selectorJson});
        if (!el) return { error: '未找到元素: ' + ${selectorJson} };
        el.scrollIntoView({ block: 'center' });
        const rect = el.getBoundingClientRect();
        return {
          x: rect.x + rect.width / 2,
          y: rect.y + rect.height / 2,
          tag: el.tagName,
          text: (el.textContent || '').slice(0, 100)
        };
      })()`;

      const coordResponse = await sendCDP(
        'Runtime.evaluate',
        {
          expression: js,
          returnByValue: true,
          awaitPromise: true,
        },
        sessionId,
      );

      const coord = coordResponse.result?.result?.value;
      if (!coord || coord.error) {
        res.statusCode = 400;
        res.end(JSON.stringify(coord || coordResponse.result));
        return;
      }

      await sendCDP(
        'Input.dispatchMouseEvent',
        { type: 'mousePressed', x: coord.x, y: coord.y, button: 'left', clickCount: 1 },
        sessionId,
      );
      await sendCDP(
        'Input.dispatchMouseEvent',
        { type: 'mouseReleased', x: coord.x, y: coord.y, button: 'left', clickCount: 1 },
        sessionId,
      );

      res.end(JSON.stringify({ clicked: true, x: coord.x, y: coord.y, tag: coord.tag, text: coord.text }));
      return;
    }

    if (pathname === '/setFiles') {
      const sessionId = await ensureSession(query.target);
      const body = JSON.parse(await readBody(req));
      if (!body.selector || !body.files) {
        res.statusCode = 400;
        res.end(JSON.stringify({ error: '需要 selector 和 files 字段' }));
        return;
      }

      await sendCDP('DOM.enable', {}, sessionId);
      const documentNode = await sendCDP('DOM.getDocument', {}, sessionId);
      const node = await sendCDP(
        'DOM.querySelector',
        {
          nodeId: documentNode.result.root.nodeId,
          selector: body.selector,
        },
        sessionId,
      );

      if (!node.result?.nodeId) {
        res.statusCode = 400;
        res.end(JSON.stringify({ error: `未找到元素: ${body.selector}` }));
        return;
      }

      await sendCDP(
        'DOM.setFileInputFiles',
        {
          nodeId: node.result.nodeId,
          files: body.files,
        },
        sessionId,
      );

      res.end(JSON.stringify({ success: true, files: body.files.length }));
      return;
    }

    if (pathname === '/scroll') {
      const sessionId = await ensureSession(query.target);
      const y = parseInt(query.y || '3000', 10);
      const direction = query.direction || 'down';

      let js;
      if (direction === 'top') {
        js = 'window.scrollTo(0, 0); "scrolled to top"';
      } else if (direction === 'bottom') {
        js = 'window.scrollTo(0, document.body.scrollHeight); "scrolled to bottom"';
      } else if (direction === 'up') {
        js = `window.scrollBy(0, -${Math.abs(y)}); "scrolled up ${Math.abs(y)}px"`;
      } else {
        js = `window.scrollBy(0, ${Math.abs(y)}); "scrolled down ${Math.abs(y)}px"`;
      }

      const response = await sendCDP(
        'Runtime.evaluate',
        {
          expression: js,
          returnByValue: true,
        },
        sessionId,
      );

      await new Promise((resolve) => setTimeout(resolve, 800));
      res.end(JSON.stringify({ value: response.result?.result?.value }));
      return;
    }

    if (pathname === '/screenshot') {
      const sessionId = await ensureSession(query.target);
      const format = query.format || 'png';
      const response = await sendCDP(
        'Page.captureScreenshot',
        {
          format,
          quality: format === 'jpeg' ? 80 : undefined,
        },
        sessionId,
      );

      if (query.file) {
        fs.writeFileSync(query.file, Buffer.from(response.result.data, 'base64'));
        res.end(JSON.stringify({ saved: query.file }));
        return;
      }

      res.setHeader('Content-Type', `image/${format}`);
      res.end(Buffer.from(response.result.data, 'base64'));
      return;
    }

    if (pathname === '/info') {
      const sessionId = await ensureSession(query.target);
      const response = await sendCDP(
        'Runtime.evaluate',
        {
          expression: 'JSON.stringify({title: document.title, url: location.href, ready: document.readyState})',
          returnByValue: true,
        },
        sessionId,
      );
      res.end(response.result?.result?.value || '{}');
      return;
    }

    res.statusCode = 404;
    res.end(JSON.stringify({
      error: '未知端点',
      endpoints: {
        '/health': 'GET - 健康检查',
        '/targets': 'GET - 列出所有页面 tab',
        '/new?url=': 'GET - 创建新后台 tab（自动等待加载）',
        '/close?target=': 'GET - 关闭 tab',
        '/navigate?target=&url=': 'GET - 导航（自动等待加载）',
        '/back?target=': 'GET - 后退',
        '/info?target=': 'GET - 页面标题/URL/状态',
        '/eval?target=': 'POST body=JS表达式 - 执行 JS',
        '/click?target=': 'POST body=CSS选择器 - JS 点击元素',
        '/clickAt?target=': 'POST body=CSS选择器 - 真实鼠标点击',
        '/setFiles?target=': 'POST body=JSON - 给 file input 赋值',
        '/scroll?target=&y=&direction=': 'GET - 滚动页面',
        '/screenshot?target=&file=': 'GET - 页面截图',
      },
    }));
  } catch (error) {
    res.statusCode = 500;
    res.end(JSON.stringify({ error: error.message }));
  }
});

function checkPortAvailable(port) {
  return new Promise((resolve) => {
    const server = net.createServer();
    server.once('error', () => resolve(false));
    server.once('listening', () => {
      server.close();
      resolve(true);
    });
    server.listen(port, '127.0.0.1');
  });
}

async function main() {
  const available = await checkPortAvailable(PORT);
  if (!available) {
    try {
      const ok = await new Promise((resolve) => {
        http.get(`http://127.0.0.1:${PORT}/health`, { timeout: 2000 }, (res) => {
          let body = '';
          res.on('data', (chunk) => {
            body += chunk;
          });
          res.on('end', () => resolve(body.includes('"ok"')));
        }).on('error', () => resolve(false));
      });

      if (ok) {
        console.log(`[workflow-web-access] 已有实例运行在端口 ${PORT}，退出`);
        process.exit(0);
      }
    } catch {
      // ignore and fall through
    }

    console.error(`[workflow-web-access] 端口 ${PORT} 已被占用`);
    process.exit(1);
  }

  server.listen(PORT, '127.0.0.1', () => {
    console.log(`[workflow-web-access] proxy 运行在 http://127.0.0.1:${PORT}`);
    connect().catch((error) => {
      console.error('[workflow-web-access] 初始连接失败:', error.message, '（将在首次请求时重试）');
    });
  });
}

process.on('uncaughtException', (error) => {
  console.error('[workflow-web-access] 未捕获异常:', error.message);
});

process.on('unhandledRejection', (error) => {
  console.error('[workflow-web-access] 未处理拒绝:', error?.message || error);
});

main();
