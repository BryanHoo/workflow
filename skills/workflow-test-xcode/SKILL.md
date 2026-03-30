---
name: workflow-test-xcode
description: Use when iOS changes need simulator-based confidence in the current Workflow/Codex environment; verify build, launch, screenshots, UI hierarchy, and simulator logs with local xcodebuildmcp first, then fall back to native Xcode tools only when necessary
---

# Workflow Test Xcode

This skill is a Workflow/Codex adaptation of the upstream `test-xcode` skill. Keep its validation loop, but do **not** assume Claude-style MCP tools exist in this session.

**Core loop:** discover project -> choose scheme -> boot simulator -> build/install/launch -> inspect visible UI -> capture runtime evidence -> pause for human-only flows -> summarize pass/fail with next action.

**Core principle:** use the strongest automation surface that actually exists on this machine, and always leave evidence behind: exact command, simulator, screenshot path, UI snapshot, and log excerpt.

## Environment Mapping

| Upstream assumption | Current Workflow/Codex adaptation |
|---|---|
| Direct `mcp__xcodebuildmcp__*` tool calls | Use the local `xcodebuildmcp` CLI first |
| Claude asks questions with platform-specific question tools | Ask the user directly in chat and wait for the answer |
| Todo creation via a separate skill | Summarize failures in the test report unless the user explicitly asks to persist them elsewhere |
| Simulator actions may run inside helper agents | Keep simulator driving in the main agent; stateful local testing should not be delegated by default |
| One tool handles everything | Use `xcodebuildmcp` first, then `/usr/bin/xcodebuild` and `xcrun simctl` as fallback |

## Agent Architecture

Default ownership in this environment:

- The **main agent** owns project discovery, simulator selection, build/install/launch, screenshot capture, log capture, and the final report.
- **Do not spawn subagents by default** for simulator driving. The simulator, log sessions, and local artifacts are stateful and tied to the current machine.
- Only use subagents when the user explicitly asks for parallel or subagent work, or when a broader workflow has already decided delegation is worth it.
- If subagents are used, keep them on sidecar tasks such as log analysis, crash triage, or reviewing a summarized failure report. Do not have multiple agents compete for the same simulator.

## Prerequisites

Before testing, verify the local execution surface:

```bash
xcodebuildmcp --help
xcodebuildmcp tools
xcodebuildmcp simulator list --enabled
/usr/bin/xcodebuild -version
```

If `xcodebuildmcp` is missing or broken, do not pretend the upstream MCP path exists. Switch to native tools:

```bash
/usr/bin/xcodebuild -list
xcrun simctl list devices available
```

If neither `xcodebuildmcp` nor native Xcode tools are usable, stop and report the concrete blocker.

## Workflow

### 1. Discover projects and schemes

Discover Xcode projects from the current workspace:

```bash
xcodebuildmcp project-discovery discover-projects \
  --workspace-root "$PWD" \
  --output json
```

Then list schemes from the selected `.xcworkspace` or `.xcodeproj`:

```bash
xcodebuildmcp project-discovery list-schemes \
  --workspace-path "/abs/path/App.xcworkspace"
```

or:

```bash
xcodebuildmcp project-discovery list-schemes \
  --project-path "/abs/path/App.xcodeproj"
```

Scheme selection rules:

- User-specified scheme wins.
- Prefer `.xcworkspace` over `.xcodeproj` when both exist.
- If exactly one non-test app scheme is plausible, use it.
- If multiple app schemes are plausible, ask instead of guessing.
- If the user says "current", only resolve automatically when there is exactly one plausible app scheme.

### 2. Choose and boot a simulator

List available simulators:

```bash
xcodebuildmcp simulator list --enabled
```

Selection rules:

- Prefer the latest available iPhone Pro simulator on this machine.
- Fall back to the latest iPhone model if no Pro model exists.
- Use iPad only when the app specifically targets iPad flows.

Boot it:

```bash
xcodebuildmcp simulator-management boot --simulator-id "SIMULATOR_UUID"
```

Open the Simulator app only when visual inspection or manual interaction is required:

```bash
xcodebuildmcp simulator-management open
```

### 3. Build with the most inspectable path

For fast smoke testing, `build-and-run` is acceptable:

```bash
xcodebuildmcp simulator build-and-run \
  --workspace-path "/abs/path/App.xcworkspace" \
  --scheme "App" \
  --simulator-id "SIMULATOR_UUID"
```

For evidence-heavy verification, prefer the explicit path below because it preserves app-path and bundle-id lookups cleanly.

Build:

```bash
xcodebuildmcp simulator build \
  --workspace-path "/abs/path/App.xcworkspace" \
  --scheme "App" \
  --simulator-id "SIMULATOR_UUID"
```

Resolve built app path:

```bash
xcodebuildmcp simulator get-app-path \
  --workspace-path "/abs/path/App.xcworkspace" \
  --scheme "App" \
  --platform "iOS Simulator" \
  --simulator-id "SIMULATOR_UUID"
```

Resolve bundle id:

```bash
xcodebuildmcp project-discovery get-app-bundle-id \
  --app-path "/abs/path/DerivedData/.../App.app"
```

If build fails:

- Keep the exact failing command.
- Capture the build error text verbatim.
- Report which target/scheme/configuration failed.
- If the user wants a fix, switch to `workflow-systematic-debugging` before editing.

### 4. Install, launch, and capture a bounded log window

Install:

```bash
xcodebuildmcp simulator install \
  --simulator-id "SIMULATOR_UUID" \
  --app-path "/abs/path/DerivedData/.../App.app"
```

Start simulator log capture before launch or immediately before a specific flow:

```bash
xcodebuildmcp logging start-simulator-log-capture \
  --simulator-id "SIMULATOR_UUID" \
  --bundle-id "com.example.app" \
  --capture-console
```

Keep the returned `log-session-id`. Then launch:

```bash
xcodebuildmcp simulator launch-app \
  --simulator-id "SIMULATOR_UUID" \
  --bundle-id "com.example.app"
```

Important adaptation: this CLI does **not** expose a live `get logs now` call like the upstream skill assumed. Instead, capture logs in bounded windows:

1. Start capture
2. Exercise one screen or one flow
3. Stop capture and inspect logs
4. Start a fresh capture for the next flow if needed

Stop and retrieve logs:

```bash
xcodebuildmcp logging stop-simulator-log-capture \
  --log-session-id "LOG_SESSION_ID"
```

### 5. Inspect UI with both screenshot and hierarchy

Capture a screenshot:

```bash
xcodebuildmcp simulator screenshot \
  --simulator-id "SIMULATOR_UUID" \
  --return-format path
```

Capture the current accessibility-visible hierarchy:

```bash
xcodebuildmcp simulator snapshot-ui \
  --simulator-id "SIMULATOR_UUID"
```

Review both artifacts together. A screenshot shows rendering; `snapshot-ui` shows what automation can actually target.

Look for:

- Blank or stuck launch screens
- Crash alerts, permission alerts, or sign-in blockers
- Clipped layouts, missing text, or off-screen controls
- Missing navigation affordances
- Keyboard overlap on forms
- Obvious error states or placeholder content

When interaction is required, use `ui-automation` conservatively:

```bash
xcodebuildmcp ui-automation tap --simulator-id "SIMULATOR_UUID" --label "Continue"
xcodebuildmcp ui-automation type-text --help
xcodebuildmcp ui-automation swipe --help
```

Use label/id targeting when possible; coordinate tapping is the last resort.

### 6. Known limitations and human-only flows

Pause and ask the user for help when automation is not trustworthy.

Known limitation carried over from upstream and still relevant here:

- SwiftUI `Text` with inline `AttributedString` links often cannot be activated reliably by simulator automation. A tap may report success but have no visible effect.

Also treat these as human-only by default:

- Sign in with Apple
- Permission prompts whose outcome matters to the scenario
- Push notifications
- In-app purchases
- Camera / Photos access
- Location prompts and map validation

Ask in plain chat with a short action list, for example:

```text
需要人工验证：
1. 请在 Simulator 中完成 Sign in with Apple
2. 确认登录后是否进入首页

结果如何？
1. 正常
2. 不正常，并描述现象
```

Do not reference unavailable platform question tools. In this environment, a normal chat turn is the default mechanism.

### 7. Failure handling

When a test step fails:

1. Preserve evidence first.
2. State the failing screen or flow.
3. Include the simulator, scheme, exact command, screenshot path, and the relevant log excerpt.
4. Ask whether to debug now or continue collecting failures.

If the user wants a fix:

- Move into `workflow-systematic-debugging` before changing code.
- After a fix, rerun the narrowest failing flow first.
- Only rerun the full smoke test when the narrow retest passes.

If the user only wants validation:

- Stop at diagnosis and produce a clean test summary.
- Do not invent todo files or side artifacts unless explicitly asked.

### 8. Native fallback path

If `xcodebuildmcp` is unavailable or insufficient, use native tools explicitly:

```bash
/usr/bin/xcodebuild -list -workspace "/abs/path/App.xcworkspace"
/usr/bin/xcodebuild -workspace "/abs/path/App.xcworkspace" -scheme "App" -destination "platform=iOS Simulator,id=SIMULATOR_UUID" build
xcrun simctl boot "SIMULATOR_UUID"
xcrun simctl install "SIMULATOR_UUID" "/abs/path/DerivedData/.../App.app"
xcrun simctl launch "SIMULATOR_UUID" "com.example.app"
xcrun simctl io "SIMULATOR_UUID" screenshot "/tmp/workflow-test-xcode-screen.png"
```

Use the native fallback when:

- `xcodebuildmcp` is missing
- A specific CLI subcommand is broken
- The user specifically asks for raw Xcode tooling

Do not silently mix paths without saying so. Report when you have switched from `xcodebuildmcp` to native tools.

## Summary Format

Use a compact report with concrete evidence:

```markdown
## Xcode Test Results

**Project:** App.xcworkspace
**Scheme:** App
**Simulator:** iPhone 17 Pro (iOS 26.2)
**Tooling path:** xcodebuildmcp / native fallback

### Build
Pass / Fail

### Flows Checked
| Flow | Status | Evidence |
|---|---|---|
| Launch | Pass | screenshot + clean logs |
| Home | Pass | hierarchy matched |
| Settings | Fail | crash after tap |

### Log Findings
- [relevant runtime error or "none"]

### Human Verification
- Sign in with Apple: confirmed / failed / not run

### Result
PASS / FAIL / PARTIAL
```

## Workflow Integration

- Use this skill directly when the task is "test the iOS app on simulator" or "smoke-test iOS changes."
- If failure investigation starts, switch to `workflow-systematic-debugging`.
- Before declaring the work complete, use `workflow-verification-before-completion`.
- Only combine with parallel-agent workflows when the user explicitly wants delegation and each delegated task is truly independent from the live simulator session.

## Red Flags

Never:

- Claim simulator coverage without preserving evidence
- Guess a scheme when multiple plausible app schemes exist
- Let multiple agents drive the same simulator concurrently
- Treat a successful tap command as proof the intended UI state changed
- Skip runtime log review after launch
- Pretend a Claude-only MCP tool is available in this session
