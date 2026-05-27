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
- 不添加 frontend/database
- 测试用 tmp_path，不改真实文件

## 测试命令
```bash
PYTHONPATH=apps/api/src python3 -m pytest apps/api/tests/ -q
```
