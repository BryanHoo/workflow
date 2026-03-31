---
name: workflow-web-access
description: Use when a task needs current public web information, page reading, dynamic or login-dependent browser access, website interaction, or web research in the current Workflow/Codex environment; prefer the web tool for public pages and escalate to CDP only when lightweight retrieval is insufficient.
---

# Workflow Web Access

## Overview

这是对上游 `web-access` 的 workflow 适配版。它保留了上游最重要的三层能力，但把执行面改成当前环境能稳定使用的方式：

- **联网路由**：把“先用什么工具”当成核心决策，而不是默认开浏览器
- **真实浏览器兜底**：公开网页优先走 `web`，只有不够用时才升级到本机 Chrome 的 CDP
- **站点经验积累**：把已验证的平台特征和陷阱存到 `references/site-patterns/`

**核心原则：用能真实完成任务的最轻路径。**

- 能用 `web` 得到完整、可信结果时，不升级到 CDP
- 只有在 `web` 不足、页面依赖真实渲染、需要登录态或需要交互时，才进入 CDP
- 进入 CDP 后，默认只操作自己创建的后台 tab，不打扰用户已有页面

## When to Use

在这些场景使用：

- 用户要求搜索、核实、阅读最新网页信息
- 目标页面是公开网页，但你不确定 `web` 能否完整读取
- 页面需要真实浏览器渲染、滚动、点击、上传、视频采样或登录态
- 你需要读取站点自己的真实 DOM、原始链接参数、图片或视频资源
- 你要处理反爬明显的平台，或 `web` 已经拿不到有效内容

不要在这些场景使用：

- 完全离线的本地代码任务
- 用户已经给出了完整网页内容且无需再访问网络
- 任务只是简单改写文本，而不是获取网页信息

## Workflow Mapping

| 上游 web-access | 当前 workflow 适配 |
|---|---|
| `WebSearch` | 原生 `web.search_query` |
| `WebFetch` | 原生 `web.open` |
| `curl` 原始 HTML | 终端里的 `curl` |
| 自定义浏览器自动化 | 本机 Chrome + `scripts/check-deps.sh` + `scripts/cdp-proxy.mjs` |
| 并行子 Agent 调研 | 仅在用户明确要求并行/子 Agent，且目标彼此独立时再结合 workflow 并行技能 |

## Tool Routing

### 默认路径：先 `web`

公开网页读取优先走 `web`：

| 场景 | 默认工具 | 升级条件 |
|---|---|---|
| 搜索入口、发现来源 | `web.search_query` | 搜不到有效来源，或结果页摘要不够 |
| 已知 URL，读取公开页面 | `web.open` | 页面内容缺失、被简化过度、需要真实渲染 |
| 要原始 HTML、meta、JSON-LD | `curl` | 请求被拦截，或数据只存在真实浏览器运行态 |
| 登录态、动态渲染、真实交互、上传、滚动加载、视频采帧 | 直接 CDP | 无 |
| 已知静态层经常无效的平台 | 直接 CDP | 无 |

**不要因为有 CDP 就跳过 `web`。**

只有下面这些信号出现时才升级：

- `web` 返回的信息明显不完整，无法满足任务成功标准
- 页面关键信息只有在客户端脚本运行后才出现
- 需要点击、翻页、填写、上传、滚动、播放视频等交互
- 需要复用用户在本机 Chrome 中已有的登录态
- 平台对静态抓取明显不友好，或你已经验证轻量路径没有改进

## Browsing Philosophy

像人一样思考，但始终围绕任务成功标准，而不是围绕固定步骤。

### 1. 先定义完成条件

拿到请求后，先说清楚：

- 最终要拿到什么信息或完成什么操作
- 什么算成功，什么算无效结果
- 是否必须来自一手来源

### 2. 先选最可能直达的起点

- 公开页面先从 `web` 开始
- 任务天然依赖登录态、交互或真实渲染时，直接 CDP
- 如果一个方法连续几次都没有质的改进，不要机械重试，直接换层级

### 3. 每一步都把结果当证据

不要只看“成功/失败”二元结果。看这些信号：

- 返回内容的质量是否足以回答问题
- 页面结构是否说明方向正确
- 报错或空结果，是目标不存在，还是当前方法不对
- 平台提示“内容不存在”时，先判断是不是访问方式的问题

### 4. 完成就停，不追求过度操作

达到成功标准后停止，不为“也许还能再找点什么”继续消耗网络、时间和上下文。

## Source Quality

信息核实时，一手来源优先于二手转载：

- 政策、法规：发布机构官网
- 企业公告：公司官方站点
- 工具能力：官方文档、源码
- 站点行为：你刚刚通过当前页面验证到的 DOM、链接、请求结果

搜索引擎是发现入口，不是最终证据。找到线索后，回到原始来源验证。

## CDP Mode

当你决定进入 CDP，先运行：

```bash
SKILL_DIR=/absolute/path/to/workflow-web-access
bash "$SKILL_DIR/scripts/check-deps.sh"
```

这些脚本属于当前 skill 自身。不要去目标仓库里查找 `skills/workflow-web-access/scripts/...`，也不要假设当前工作目录就是 skill 目录。

这个脚本会检查：

- `node` 是否可用
- Chrome 远程调试端口是否已经打开
- 本地 proxy 是否已就绪；如果没有，会自动拉起

如果检查失败，告诉用户缺的是什么，不要假装自己还能继续。

**当前环境注意事项：** 在 Codex 的沙箱 shell 中，访问 `127.0.0.1` 这类本机端口可能被拦截。若 `check-deps.sh`、`curl http://127.0.0.1:3456/...` 或对 `9222` 的连通性检测报权限/连接错误，但你确认 Chrome 已开启远程调试，应改用带提权的本地命令重试，而不是误判为站点或脚本故障。

### CDP 使用规则

- 默认只使用自己创建的 tab
- 不主动关闭或污染用户原有 tab
- 任务结束后关闭自己创建的 tab，保留 proxy 常驻
- 如果页面内容拿不到，再判断是否真的需要用户先登录

### 快速入口

```bash
# 新建后台 tab
curl -s "http://127.0.0.1:3456/new?url=https://example.com"

# 读取页面信息
curl -s "http://127.0.0.1:3456/info?target=TARGET_ID"

# 执行 JS
curl -s -X POST "http://127.0.0.1:3456/eval?target=TARGET_ID" -d 'document.title'

# 点击 / 滚动 / 截图
curl -s -X POST "http://127.0.0.1:3456/click?target=TARGET_ID" -d 'button.submit'
curl -s "http://127.0.0.1:3456/scroll?target=TARGET_ID&direction=bottom"
curl -s "http://127.0.0.1:3456/screenshot?target=TARGET_ID&file=/tmp/workflow-web-access-shot.png"

# 关闭自己创建的 tab
curl -s "http://127.0.0.1:3456/close?target=TARGET_ID"
```

完整 API、错误处理和 `eval` 模式见 `references/cdp-api.md`。

## Using CDP Well

进入浏览器层后，`/eval` 是最重要的观察和执行接口：

- **看**：读取 DOM 结构、链接、按钮、表单、文本
- **做**：点击元素、滚动懒加载、填写表单、触发页面状态改变
- **读**：提取文本、图片 URL、视频元数据，不要默认靠全页截图硬读

优先读取真实 DOM 和站点生成的链接，不要随意手工拼接站内 URL。站点自己输出的链接往往带着必要上下文参数。

## Media and Dynamic Pages

- 图片承载核心信息时，优先从 DOM 里拿图片 URL，再定向读取
- 视频承载核心信息时，可用 `/eval` 控制 `<video>` 的播放、暂停、跳转，再配合 `/screenshot` 采样
- 懒加载页面先滚动，再提取图片或新增内容

## Login Handling

本机 Chrome 往往已经带有用户的日常登录态，但不要先假设必须登录。

正确顺序是：

1. 先尝试获取目标内容
2. 内容确实拿不到，再判断是否是登录导致
3. 只有在登录能明显解决问题时，才通知用户去 Chrome 登录

推荐表述：

> 当前页面在未登录状态下无法获取目标内容，请先在你的 Chrome 中登录对应网站，完成后告诉我继续。

## Site Patterns

确定目标站点后，检查是否已有经验文件：

```bash
SKILL_DIR=/absolute/path/to/workflow-web-access
bash "$SKILL_DIR/scripts/match-site.sh" "xiaohongshu"
```

站点经验位于 `references/site-patterns/`，按域名保存。只记录经过验证的事实：

- 平台特征
- 有效 URL 模式或 DOM 模式
- 已知陷阱和失效方式

不要把猜测写进经验文件。

## Parallel Research

多个目标彼此独立时，这个技能适合和 workflow 的并行能力组合；但在当前 Codex 约束下，**只有用户明确要求子 Agent 或并行处理时**才这样做。

给子 Agent 描述目标，不要过度规定手段。重点是“获取什么”“验证什么”，不是预设它必须先搜索还是先开页面。

## References

按需加载这些文件：

- `references/cdp-api.md`：需要 CDP API 细节、`eval` 用法、错误处理
- `references/site-patterns/{domain}.md`：目标站点已有经验时必须读取
