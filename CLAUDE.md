# Alters Lab — Project Instructions

## 项目身份
Alters Lab 是个人未来路径模拟和校准系统。不是内容创作工具。

## 当前阶段
- P0-P14 全部完成
- P6 状态：CODE_COMPLETE_VALIDATION_RESTARTED / NOT_VALIDATED / NOT_SEALED
- 下一步：收集 fresh post-P14 证据（4 weekly reviews + 4 calibration records + 1 pattern review，跨越 21+ 天）
- 项目已开源（MIT LICENSE），有 sample data 和 load-sample 命令
- P6 证据收集需要时间积累（21+ 天），不是纯编码任务

## 下一个 Session 待办

技术端（按优先级）：
1. ✅ Docker 支持 — Dockerfile + docker-compose.yml + docker-entrypoint.sh + .dockerignore
2. ✅ GettingStarted 加 load-sample 步骤
3. ✅ ProviderSettings 去掉硬编码 GitHub URL
4. ✅ P6 前缀清理 — p6Progress → progress, p6_behavior_validated → behavior_validated
5. ✅ data-model.md 补全 — WeeklyNote, ProviderConfig, PatternReview
6. ✅ 前端测试 — vitest + 12 tests (ErrorBoundary, Button, Card)
7. ✅ sample weekly note 数据 — 2 个示例周笔记
8. ✅ Dashboard 仪表盘 — recharts 图表（评分趋势、每周活动、模式触发）
9. ✅ Dark Mode — ThemeContext + CSS 变量迁移 + 切换按钮
10. ✅ Keyboard Shortcuts — G+key 导航，? 帮助

算法端（下一个 session）：
11. 趋势外推算法 — 用历史评分预测未来 4 周
12. 置信区间 — 基于数据量和一致性
13. 动态权重 — 根据当前状态调整 rubric 维度权重
14. 模式修正 — 检测到的模式影响预测

## 技术栈
- **后端**: Python 3.11+, FastAPI, Pydantic, PyYAML
- **前端**: React 18, TypeScript, Vite, Tailwind v4, TanStack Query, Phosphor Icons, recharts, Outfit + JetBrains Mono 字体
- **存储**: YAML + JSON 文件（alters/ 目录），无数据库
- **打包**: Debian (.deb) + Docker，CLI 入口 `alters-lab`
- **测试**: pytest + httpx
- **部署**: 本地安装，运行在 127.0.0.1:18790
- **中间件**: CORS, Rate Limiting (600 req/min), 结构化日志

## 核心数据流
Snapshot → Branch Discovery → Alter Generation → Dialogue → Calibration → Archive
详见 docs/architecture.md 和 docs/data-model.md

## 新 session 启动顺序

所有 Claude Code、Codex 或其他 coding agent 必须先读：

1. `CLAUDE.md`（本文件）— 项目状态、技术栈、文档规范、待办任务
2. `AGENTS.md` — 协作模式、硬边界、验证命令
3. `docs/architecture.md` — 技术架构（系统怎么工作的）
4. `docs/data-model.md` — 数据模型（schema 定义）

**⚠️ `docs/harness/` 已删除** — 历史里程碑文档（P0-P14 治理记录）已清理。当前状态以 CLAUDE.md 为准。

如果这些文件、README、最近 git log 互相冲突，先修文档，不要直接进入功能开发。

## 文档维护规范

### 文档层级（按优先级）

| 文件 | 定位 | 谁该读 | 什么时候更新 |
|------|------|--------|-------------|
| `README.md` | 公开入口，用户第一印象 | 用户、贡献者 | 用户可见功能变化（新页面、新 CLI 命令、安装方式） |
| `CLAUDE.md` | Agent 指令，项目状态 | 所有 coding agent | 状态变化、新功能、测试数变化、技术栈变化 |
| `AGENTS.md` | 协作协议，硬边界 | 所有 coding agent | 协作方式变化、边界变化、验证命令变化 |
| `docs/architecture.md` | 技术架构（系统怎么工作的） | 开发者、agent | 新模块、中间件、API 路由、部署方式变化 |
| `docs/data-model.md` | 数据模型（schema 定义） | 开发者、agent | Pydantic schema 变化、新实体、字段增删 |
| `docs/product-spec.md` | 产品规格（产品做什么） | 开发者、agent | 新功能、能力变化、用户工作流变化 |
| `docs/user/` | 用户指南 | 用户 | 用户工作流变化 |

### 更新规则

**每次 commit 前，检查：**
1. 这次改动是否影响了用户可见功能？→ 更新 `README.md`
2. 这次改动是否改变了系统状态、测试数、技术栈？→ 更新 `CLAUDE.md`
3. 这次改动是否改变了协作方式或硬边界？→ 更新 `AGENTS.md`
4. 这次改动是否新增/修改了模块、中间件、API 路由？→ 更新 `docs/architecture.md`
5. 这次改动是否新增/修改了 Pydantic schema？→ 更新 `docs/data-model.md`
6. 这次改动是否新增/修改了产品功能？→ 更新 `docs/product-spec.md`

**不需要全改，只改受影响的。** 如果不需要更新文档，在 completion report 中说明原因。

### 冲突解决

如果文档之间冲突：
- 代码 > `docs/data-model.md` > `docs/architecture.md` > `CLAUDE.md` > `README.md`
- 以代码为准，修文档

### 测试数维护

`CLAUDE.md` 中的测试数必须与实际一致。每次 commit 前运行测试确认。

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
- 1267 backend tests passing
- 12 frontend tests passing (vitest)

## 测试命令
```bash
# 后端
PYTHONPATH=apps/api/src python3 -m pytest apps/api/tests/ -q

# 前端
cd apps/web && npm run test
```

## 项目文档
- `docs/architecture.md` — 技术架构（真相源）
- `docs/data-model.md` — 数据模型（真相源）
- `docs/product-spec.md` — 产品规格（真相源）
- `docs/USER_GUIDE.md` — 用户指南
- `docs/PROVIDER_CONFIGURATION.md` — Provider 配置
- `docs/user/` — 安装、配置、故障排除
- `docs/*-workflow.md` — 概念性工作流参考
- `alters/sample/` — 新用户示例数据

## 前端页面
- Dashboard (默认首页), SystemStatus, GettingStarted, WeeklyReview, AlterDialogue
- RealityScore, CalibrationHistory, RubricDelta, CheckpointPlan
- ProviderSettings, PatternReview, BehaviorValidation, DataManagement
- 所有页面通过 App.tsx 路由，侧边栏导航（桌面端 220px 固定侧边栏 + 移动端底部 tab bar）
- 数据层：TanStack Query hooks（src/hooks/useApi.ts），替代手动 useState+useEffect
- 图表：recharts（Dashboard 页面的评分趋势、每周活动）
- 深色模式：ThemeContext + CSS 变量，侧边栏/移动端切换按钮
- 键盘快捷键：G+key 导航，? 显示帮助
- 设计风格：温暖专业（Notion/Obsidian 风格），Outfit 字体，amber-700 强调色
