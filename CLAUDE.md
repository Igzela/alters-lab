# Alters Lab — Project Instructions

## 项目身份
Alters Lab 是个人未来路径模拟和校准系统。不是内容创作工具。

## 协作模式

三方角色分工：

- **GPT (ChatGPT web)** = 主导构建者/总指挥。定义 macro-slice 任务，审查 commit，给出 PASS/BLOCKED 判定，决定下一步任务。
- **Claude Code (我)** = 执行者。接收 GPT 的长指令，实现代码/测试，commit，push，发送完成报告。
- **Charlie (用户)** = 人类负责人。在 GPT 聊天窗口监控，批准 stage gate，随时可以纠正中断。

### 执行协议

1. GPT 下达 macro-slice 指令（schemas + service + API + tests + docs 打包为一个执行单元）
2. 我执行代码、测试、commit、push
3. 完成后通过 relay 发送 completion report 给 GPT 审查
4. GPT 给出 PASS 或 BLOCKED 判定
5. 如果 BLOCKED → 修复问题，重新提交审查
6. 如果 PASS → 等待 GPT 下达下一个 macro-slice
7. Charlie 在全程监控，随时可以介入

### Relay 脚本

通过 Chrome CDP (localhost:9222) 连接已登录的 ChatGPT web UI：
```bash
python3 ~/.hermes/scripts/chatgpt_relay.py '你的消息'
```
- 每次调用是独立的（新对话）
- 超时 120 秒
- 需要 Chrome 开启 --remote-debugging-port=9222

## 代码规范
- 不修改 alters/current/ 下的 active YAML（除非有明确 approval）
- 不连接 LLM provider
- 不添加 frontend/database
- 测试用 tmp_path，不改真实文件

## 测试命令
```bash
PYTHONPATH=apps/api/src python3 -m pytest apps/api/tests/ -q
```
