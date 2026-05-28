# Alters Lab — Project Instructions

## 项目身份
Alters Lab 是个人未来路径模拟和校准系统。不是内容创作工具。

## 当前阶段
- P0-P14 全部完成（P14: Frontend polish — component standardization, date i18n, styled inputs, progress bar, JSON display, skip-to-content）
- P11 已封印：PRODUCT_COMPLETE_BEFORE_VALIDATION
- P12 已完成：P12-M7 决策 — 从零重启 P6 验证
- P13 已完成：GPT PASS_WITH_GOVERNANCE_CLOSEOUT，P13 scope COMPLETE
- P14 已完成：GPT PASS（BLOCKED_WITH_SMALL_R1 resolved — governance commit only），P14 scope COMPLETE
- P6 状态：CODE_COMPLETE_VALIDATION_RESTARTED / NOT_VALIDATED / NOT_SEALED
- Week 1 证据已归档为历史（pre-P12），不计入 P6 closeout
- 下一步：收集 fresh post-P14 证据（4 weekly reviews + 4 calibration records + 1 pattern review，跨越 21+ 天）

## 技术栈
- **后端**: Python 3.11+, FastAPI, Pydantic, PyYAML
- **前端**: React 18, TypeScript, Vite（已激活，P11 新增多个页面）
- **存储**: YAML + JSON 文件（alters/ 目录），无数据库
- **打包**: Debian (.deb)，CLI 入口 `alters-lab`
- **测试**: pytest + httpx
- **部署**: 本地安装，运行在 127.0.0.1:18790

## 核心数据流
Snapshot → Branch Discovery → Alter Generation → Dialogue → Calibration → Archive
详见 docs/architecture.md 和 docs/data-model.md

## 新 session 启动顺序

所有 Claude Code、Codex 或其他 coding agent 必须先读：

1. `AGENTS.md`
2. `docs/harness/START_HERE_FOR_NEW_SESSION.md`
3. `docs/harness/CURRENT_SESSION_CONTEXT.md`
4. `docs/harness/PROJECT_BOARD.md`
5. `docs/harness/TASK_QUEUE.md`

如果这些文件、README、最近 git log 互相冲突，先修文档，不要直接进入功能开发。

## 协作模式

三方角色分工：

- **GPT (ChatGPT web)** = 主导构建者/总指挥。定义 macro-slice 任务，审查 commit，给出 PASS/BLOCKED 判定，决定下一步任务。
- **Claude Code (我)** = 执行者。接收 GPT 的长指令，实现代码/测试，commit，push，发送完成报告。
- **Charlie (用户)** = 人类负责人。在 GPT 聊天窗口监控，批准 stage gate，随时可以纠正中断。

### 执行协议

1. GPT 下达 macro-slice 指令（schemas + service + API + tests + docs 打包为一个执行单元）
2. 我执行代码、测试、commit、push
3. 完成后通过 chrome-devtools MCP 发送 completion report 给 GPT 审查
4. **自动拉取 GPT 回复**（不要问用户，自己用 MCP 读）
5. GPT 给出 PASS 或 BLOCKED 判定
6. 如果 BLOCKED → 修复问题，重新提交审查
7. 如果 PASS → 继续执行下一个 macro-slice
8. Charlie 在全程监控，随时可以介入

### 自动化关键规则

- 发送 completion report 后，**必须自己拉取 GPT 回复**，不要等用户转达
- **发一次，等回复，不要追。** 发送 completion report 后等 GPT 自己回复。不要发 follow-up 追问 verdict。GPT 需要时间审查，追发只会产生噪音。
- **发完消息后保持沉默。** 不要输出 "waiting for GPT" 之类的话。发完就闭嘴，等 GPT 回复触发下一步。
- **轮询：每 5 秒检查一次 GPT 回复。** 用 MCP `evaluate_script` 读取页面内容，直到找到 verdict（PASS/BLOCKED）。不要一次性只读一次就放弃。
- 收到 verdict 后立即执行下一步，不要停下来问用户

### GPT 通信方式（chrome-devtools MCP）

所有 ChatGPT 交互通过 chrome-devtools MCP 完成，不使用外部脚本。

**发送消息：**
1. `list_pages` → 找 chatgpt.com 页面 → `select_page`
2. `evaluate_script`: `document.querySelector('.ProseMirror').focus(); document.execCommand('insertText', false, '消息内容')`
3. `evaluate_script`: `form.querySelectorAll('button').find(b => (b.getAttribute('aria-label')||'').includes('Send')).click()`

**读取 GPT 回复：**
1. `evaluate_script`: `document.body.innerText.substring(document.body.innerText.length - 2000)`
2. 从返回文本中找 PASS/BLOCKED/accepted 关键词

## 代码规范
- 不修改 alters/current/ 下的 active YAML（除非有明确 approval）
- 不连接 LLM provider
- 测试用 tmp_path，不改真实文件
- commit message 用英文，格式: `P{N}-M{N}: 简短描述`，修正用 `-R{N}` 后缀
- 1270 backend tests passing

## 文档维护规则

每次 commit 前，如果状态、测试数、命令、边界、页面、路由、证据或下一步发生变化，必须同步更新：

- `docs/harness/START_HERE_FOR_NEW_SESSION.md`
- `docs/harness/CURRENT_SESSION_CONTEXT.md`
- `docs/harness/PROJECT_BOARD.md`
- `docs/harness/TASK_QUEUE.md`
- `docs/harness/RUN_LOG.md`
- `docs/harness/EVIDENCE_INDEX.md`
- `README.md`
- `CLAUDE.md`
- `AGENTS.md`

如果不需要更新文档，在 completion report 中说明原因。新 session 必须能只靠文档接手。

## 测试命令
```bash
PYTHONPATH=apps/api/src python3 -m pytest apps/api/tests/ -q
```

## 项目文档
- docs/ — 工作流和架构文档（architecture.md, data-model.md, product-spec.md 等）
- docs/harness/ — 里程碑证据和关闭报告
- 当前任务方向见最近 git log

## 前端页面
- SystemStatus (status), GettingStarted, WeeklyReview, AlterDialogue
- RealityScore, CalibrationHistory, RubricDelta, CheckpointPlan
- ProviderSettings, PatternReview, BehaviorValidation, DataManagement
- 所有页面通过 App.tsx 路由，nav bar 导航
