# CDP Proxy API 参考

## 基础信息

- 默认地址：`http://127.0.0.1:3456`
- 可通过环境变量 `WORKFLOW_WEB_ACCESS_PORT` 覆盖端口
- 推荐启动方式：在同一条命令里设置并使用 `SKILL_DIR`，例如 `SKILL_DIR="/absolute/path/to/workflow-web-access"; bash "${SKILL_DIR}/scripts/check-deps.sh"`
- Proxy 启动后可持续复用，不建议任务结束时主动停止
- 在当前 Codex 环境里，如果沙箱阻止访问本机端口，相关 `curl` 或连通性检测需要用提权方式执行

## 使用顺序

1. 运行 `check-deps.sh`
2. 用 `/new` 创建自己的后台 tab
3. 用 `/info` 或 `/eval` 理解页面结构
4. 按需要使用 `/click`、`/clickAt`、`/scroll`、`/setFiles`
5. 任务结束后用 `/close` 关闭自己创建的 tab

## API 端点

### `GET /health`

健康检查。

```bash
curl -s http://127.0.0.1:3456/health
```

### `GET /targets`

列出当前已打开的页面 tab。

```bash
curl -s http://127.0.0.1:3456/targets
```

### `GET /new?url=URL`

创建新后台 tab，并等待页面加载完成。

```bash
curl -s "http://127.0.0.1:3456/new?url=https://example.com"
```

### `GET /close?target=ID`

关闭指定 tab。

```bash
curl -s "http://127.0.0.1:3456/close?target=TARGET_ID"
```

### `GET /navigate?target=ID&url=URL`

在已有 tab 中导航到新 URL，并等待加载。

```bash
curl -s "http://127.0.0.1:3456/navigate?target=TARGET_ID&url=https://example.com"
```

### `GET /back?target=ID`

后退一页。

```bash
curl -s "http://127.0.0.1:3456/back?target=TARGET_ID"
```

### `GET /info?target=ID`

获取页面标题、URL、`readyState`。

```bash
curl -s "http://127.0.0.1:3456/info?target=TARGET_ID"
```

### `POST /eval?target=ID`

执行任意 JavaScript。POST body 为 JS 表达式。

```bash
curl -s -X POST "http://127.0.0.1:3456/eval?target=TARGET_ID" -d 'document.title'
```

建议：

- 返回值尽量可序列化
- 大对象用 `JSON.stringify(...)`
- 未知页面先用轻量表达式理解 DOM，再逐步深入

### `POST /click?target=ID`

使用 `el.click()` 点击 CSS 选择器命中的元素。

```bash
curl -s -X POST "http://127.0.0.1:3456/click?target=TARGET_ID" -d 'button.submit'
```

### `POST /clickAt?target=ID`

使用 CDP 真实鼠标事件点击。适合需要用户手势或普通点击无效的场景。

```bash
curl -s -X POST "http://127.0.0.1:3456/clickAt?target=TARGET_ID" -d '.upload-btn'
```

### `POST /setFiles?target=ID`

给 `input[type=file]` 设置本地文件，绕过系统文件对话框。

```bash
curl -s -X POST "http://127.0.0.1:3456/setFiles?target=TARGET_ID" \
  -d '{"selector":"input[type=file]","files":["/path/to/file.png"]}'
```

### `GET /scroll?target=ID&direction=bottom`

滚动页面并等待懒加载触发。

```bash
curl -s "http://127.0.0.1:3456/scroll?target=TARGET_ID&direction=bottom"
curl -s "http://127.0.0.1:3456/scroll?target=TARGET_ID&y=3000"
```

### `GET /screenshot?target=ID&file=/tmp/shot.png`

截图到本地文件；不带 `file` 时返回图片二进制。

```bash
curl -s "http://127.0.0.1:3456/screenshot?target=TARGET_ID&file=/tmp/workflow-web-access-shot.png"
```

## 错误处理

| 错误 | 常见原因 | 处理方式 |
|---|---|---|
| `Chrome 未开启远程调试端口` | Chrome 没开调试能力 | 让用户打开 `chrome://inspect/#remote-debugging` 并启用 |
| `attach 失败` | target 已关闭或 ID 失效 | 重新用 `/targets` 获取 |
| `CDP 命令超时` | 页面未响应或执行表达式过重 | 缩小操作范围，或重新载入页面 |
| `端口已被占用` | 已有 proxy 或其他服务占用 | 先查 `/health`，如果不是当前 proxy 再换端口 |

## 操作建议

- 未知页面先 `/info` 或简短 `/eval`，不要上来就写复杂提取脚本
- 优先提取站点自己生成的完整链接，不要手工删减查询参数
- 需要视觉确认时再截图，不要把截图当作默认读取手段
- 懒加载页面先滚动，再提取图片、列表项或分页内容
