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
4. **自动拉取 GPT 回复**（不要问用户，自己从 CDP 读）
5. GPT 给出 PASS 或 BLOCKED 判定
6. 如果 BLOCKED → 修复问题，重新提交审查
7. 如果 PASS → 继续执行下一个 macro-slice
8. Charlie 在全程监控，随时可以介入

### 自动化关键规则

- 发送 completion report 后，**必须自己拉取 GPT 回复**，不要等用户转达
- **Relay 原则：发一次，等回复，不要追。** 发送 completion report 后等 GPT 自己回复。不要发 follow-up 追问 verdict。GPT 需要时间审查，追发只会产生噪音。
- **发完 relay 后保持沉默。** 不要输出 "waiting for GPT" 之类的话。发完就闭嘴，等 GPT 回复触发下一步。
- **CDP 轮询：每 5 秒检查一次 GPT 回复。** 发送 relay 后，如果 relay 超时或用户说"他回答了"，用 CDP 每 5 秒读取页面内容，直到找到 verdict（PASS/BLOCKED）。不要一次性只读一次就放弃。
- 拉取方式：直接从 CDP 读取 last assistant message（见下方脚本）
- 如果 relay 超时，用 CDP 直接读取页面内容
- 收到 verdict 后立即执行下一步，不要停下来问用户

### Relay 脚本

通过 Chrome CDP (localhost:9222) 连接已登录的 ChatGPT web UI：
```bash
python3 ~/.hermes/scripts/chatgpt_relay.py '你的消息'
```
- 每次调用是独立的（新对话）
- 超时 120 秒
- 需要 Chrome 开启 --remote-debugging-port=9222

### 直接读取 GPT 回复（relay 超时时用）

当 relay 脚本超时，直接从 CDP 读取页面内容：
```bash
python3 -c "
import asyncio, json, urllib.request, websockets
async def r():
    tabs = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json/list', timeout=3).read())
    ws_url = next(t['webSocketDebuggerUrl'] for t in tabs if 'chatgpt.com' in t.get('url',''))
    async with websockets.connect(ws_url, max_size=10*1024*1024) as ws:
        await ws.send(json.dumps({'id':1,'method':'Runtime.evaluate','params':{'expression':'document.body.innerText.substring(document.body.innerText.length-2000)','returnByValue':True}}))
        while True:
            raw = await asyncio.wait_for(ws.recv(), timeout=10)
            d = json.loads(raw)
            if d.get('id')==1:
                print(d.get('result',{}).get('result',{}).get('value',''))
                break
asyncio.run(r())
"
```
- 读取页面最后 2000 字符（GPT 回复在页面底部）
- 如果要读更多，调大 substring 的 length

## 代码规范
- 不修改 alters/current/ 下的 active YAML（除非有明确 approval）
- 不连接 LLM provider
- 不添加 frontend/database
- 测试用 tmp_path，不改真实文件

## 测试命令
```bash
PYTHONPATH=apps/api/src python3 -m pytest apps/api/tests/ -q
```
