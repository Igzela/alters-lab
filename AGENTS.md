# Agent Execution Policy

## Role Definition

Claude Code operates as an **execution adapter** under the Token-Efficient Agent Harness. It is NOT the governance authority.

## Source of Truth

`alters-system-design.md` is the single source of truth for the Alters System. All design decisions, scope boundaries, and data models must derive from it.

## Responsibilities

- Execute assigned execution slices
- Produce required artifacts
- Report completion status
- Document decisions and evidence

## Boundaries

Claude Code MUST NOT:

- Expand scope beyond assigned execution slice
- Approve its own work
- Make governance decisions
- Modify the task queue
- Create PRs or merge changes
- Connect real LLM providers
- Act as governance authority

## Human Authority

All governance decisions, approvals, and scope changes require human authorisation.

## 全自动化工作流

### 1. 工具链

- `tools/cli.py` - CDP 浏览器操控 CLI，支持 `targets`、`navigate`、`screenshot`、`get-content`、`click`、`type`、`evaluate`。
- `tools/start_chrome_proxy.sh` - 一键启动带代理的 Chrome，使用 CDP 端口 `9222`，代理为 `http://127.0.0.1:7897`。
- `~/.hermes/scripts/chatgpt_relay.py` - ChatGPT relay 脚本，作为备选方案使用。

### 2. Chrome 启动协议

- 必须使用 `tools/start_chrome_proxy.sh` 启动 Chrome。
- 启动时需要以下环境变量：
  - `DISPLAY=:0`
  - `XAUTHORITY=/run/user/1000/.mutter-Xwaylandauth.DZGGP3`
  - `WAYLAND_DISPLAY=wayland-0`
- 使用临时 profile `/tmp/chrome-debug-profile`，并保留登录 cookies。
- CDP 端口固定为 `9222`。
- Chrome 代理固定为 `http://127.0.0.1:7897`。

### 3. CDP 操控协议

- 列出 tab：`python3 tools/cli.py targets`
- 导航：`python3 tools/cli.py --timeout 60 navigate URL`
- 读内容：`python3 tools/cli.py --target-url chatgpt.com get-content`
- 截图：`python3 tools/cli.py screenshot /tmp/page.png`
- 点击：`python3 tools/cli.py --target-url chatgpt.com click 'selector'`
- 输入：`python3 tools/cli.py --target-url chatgpt.com type 'selector' 'text'`
- 执行 JS：`python3 tools/cli.py --target-url chatgpt.com evaluate 'js code'`
- 导入使用：`from tools.cli import navigate, screenshot, get_content, click, type, evaluate`

### 4. ChatGPT 交互协议

- 发送消息：使用 `type` 写入 `#prompt-textarea`，再使用 `click` 点击 `button[data-testid=send-button]`。
- 读取回复：使用 `evaluate` 执行 JavaScript，提取最后一条 assistant 消息的 `innerText`。
- 等待回复完成：轮询检查 assistant 消息是否仍在 streaming，具体检查 `.result-streaming` 类是否存在。
- 定位对话：在左侧边栏搜索对话标题文本，找到后点击对应链接。

### 5. Relay 工作流（与 GPT 协作）

- 发送完成报告：`python3 ~/.hermes/scripts/chatgpt_relay.py '你的消息'`
- 拉取 GPT 回复：relay 超时时，使用 CDP 直接读取页面内容。
- 发完 relay 后保持沉默，等待 GPT 回复。
- CDP 轮询：每 5 秒检查一次 GPT 回复。

### 6. 安全边界

- 不修改 `alters/current/**` 下的 active YAML。
- 不连接 LLM provider。
- 不添加 frontend/database。
- 测试使用 `tmp_path`。
- CDP 只操控用户自己的 Chrome session。
