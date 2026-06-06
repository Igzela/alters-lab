# Alters Lab — Project Instructions

## 项目身份
Alters Lab 是个人未来路径模拟和校准系统。不是内容创作工具。

## 当前阶段
- v1.0 已 tag 并发布（2026-06-04）
- P6 状态：NOT_VALIDATED / NOT_SEALED
- LLM-Driven Calibration Phase 1-2 完成（schema/service/API/前端 page/hooks/i18n）
- 下一步：Phase 3（前端 UI 打磨）+ Phase 4（outcome targets + predictor profile 提取）
- 1970 backend tests, 84 frontend tests

## 下一个 Session 待办

**LLM-Driven Calibration**（详见 `docs/LDRIVEN_CALIBRATION_PLAN.md`）：

Phase 1-2：✅ 完成
Phase 3：前端 UI 打磨（draft 编辑、对话体验优化、错误处理）
Phase 4：扩展到 outcome targets + predictor profile 提取

## 技术栈
- **后端**: Python 3.11+, FastAPI, Pydantic, PyYAML
- **前端**: React 18, TypeScript, Vite, Tailwind v4, TanStack Query, recharts
- **存储**: YAML + JSON 文件，无数据库
- **部署**: 本地 127.0.0.1:18790，Docker 支持
- **测试**: pytest (后端), vitest (前端)

## 新 session 启动顺序

1. `CLAUDE.md`（本文件）— 项目状态、待办
2. `AGENTS.md` — 协作模式、硬边界、验证命令、commit 检查清单
3. `docs/architecture.md` — 技术架构
4. `docs/data-model.md` — schema 索引

如果文件之间冲突：代码 > data-model.md > architecture.md > CLAUDE.md > README.md

## 测试命令
```bash
PYTHONPATH=apps/api/src python3 -m pytest apps/api/tests/ -q
cd apps/web && npm run test && npm run build
```
