#!/usr/bin/env python3
"""
ChatGPT Relay v2 — send a question to ChatGPT via CDP, print reply to stdout.
Fixes: long messages (clipboard paste), stability detection (strip timestamps).
"""
import asyncio
import json
import sys
import urllib.request
import websockets
from html import escape as html_escape

CDP_LIST_URL = "http://127.0.0.1:9222/json/list"
TIMEOUT = 60
STABLE_WINDOW = 2
POLL_INTERVAL = 0.5
THINKING_MIN_LEN = 15  # skip short 'Thinking' placeholders

class CDP:
    def __init__(self, ws):
        self._ws = ws
        self._next_id = 0

    async def eval(self, expression: str):
        self._next_id += 1
        msg_id = self._next_id
        await self._ws.send(json.dumps({
            "id": msg_id,
            "method": "Runtime.evaluate",
            "params": {"expression": expression, "returnByValue": True},
        }))
        while True:
            raw = await asyncio.wait_for(self._ws.recv(), timeout=10)
            data = json.loads(raw)
            if data.get("id") == msg_id:
                return data.get("result", {}).get("result", {}).get("value")

async def find_chatgpt_ws_url():
    for attempt in range(5):
        try:
            resp = urllib.request.urlopen(CDP_LIST_URL, timeout=3)
            tabs = json.loads(resp.read())
            for tab in tabs:
                url = tab.get("url", "")
                if "chatgpt.com" in url:
                    return tab["webSocketDebuggerUrl"]
            raise SystemExit("No ChatGPT tab found.")
        except urllib.error.URLError:
            if attempt < 4:
                await asyncio.sleep(1)
            else:
                raise SystemExit("Cannot connect to CDP at 127.0.0.1:9222")

async def send_message(cdp, question):
    # Use clipboard paste instead of innerHTML for long messages
    safe_q = json.dumps(question)  # properly escape for JS string
    await cdp.eval(f"""
        (function() {{
            var el = document.getElementById('prompt-textarea');
            if (!el) throw new Error('no prompt-textarea');
            el.focus();
            // Use execCommand to paste — works with ProseMirror
            var dt = new DataTransfer();
            dt.setData('text/plain', {safe_q});
            var pe = new ClipboardEvent('paste', {{clipboardData: dt, bubbles: true, cancelable: true}});
            el.dispatchEvent(pe);
        }})();
    """)
    await asyncio.sleep(0.5)

    # Fallback: if paste didn't work, try innerHTML
    await cdp.eval(f"""
        (function() {{
            var el = document.getElementById('prompt-textarea');
            var text = el.innerText.trim();
            if (!text || text.length < 5) {{
                el.innerHTML = '<p>{html_escape(question, quote=True)}</p>';
                el.dispatchEvent(new Event('input', {{bubbles: true}}));
            }}
        }})();
    """)
    await asyncio.sleep(0.3)

    await cdp.eval("""
        (function() {
            var btn = document.querySelector('button[data-testid="send-button"]');
            if (btn && !btn.disabled) { btn.click(); return 'sent'; }
            // Fallback: press Enter in textarea
            var el = document.getElementById('prompt-textarea');
            if (el) {
                el.focus();
                el.dispatchEvent(new KeyboardEvent('keydown', {key:'Enter', code:'Enter', keyCode:13, bubbles:true}));
                return 'enter';
            }
            return 'nothing';
        })();
    """)

def clean_text(text):
    """Strip timestamps and UI noise from assistant message text."""
    if not text:
        return text
    # Remove common timestamp patterns
    import re
    text = re.sub(r'\d{1,2}:\d{2}\s*(AM|PM|上午|下午)?', '', text)
    text = re.sub(r'Copy code|copied!', '', text)
    text = re.sub(r'↩', '', text)
    return text.strip()

async def wait_for_reply(cdp, last_before=''):
    start = asyncio.get_event_loop().time()
    last_text = None
    stable_since = None
    new_reply_seen = False

    while True:
        now = asyncio.get_event_loop().time()
        if now - start > TIMEOUT:
            raise TimeoutError(f"Timeout ({TIMEOUT}s)")

        raw = await cdp.eval("""
            (function() {
                var msgs = document.querySelectorAll('[data-message-author-role="assistant"]');
                if (!msgs.length) return JSON.stringify({text: null, streaming: false});
                var last = msgs[msgs.length - 1];
                var stopBtn = document.querySelector('button[aria-label="Stop streaming"]');
                var retryBtn = document.querySelector('button[aria-label="Retry"]');
                return JSON.stringify({
                    text: last.innerText,
                    streaming: !!stopBtn,
                    done: !!retryBtn
                });
            })();
        """)

        if raw:
            info = json.loads(raw)
            text = clean_text(info.get("text"))
            streaming = info.get("streaming", False)
            done = info.get("done", False)
        else:
            text = None
            streaming = False
            done = False

        # Skip short "Thinking" placeholders
        if text and len(text) < THINKING_MIN_LEN:
            text = None

        if text and text != last_before:
            new_reply_seen = True

        if new_reply_seen and text and not streaming:
            if text != last_text:
                last_text = text
                stable_since = now
            elif stable_since and (now - stable_since) >= STABLE_WINDOW:
                return text
            # Also return if retry button visible (response fully done)
            elif done and len(text) > 10:
                return text

        await asyncio.sleep(POLL_INTERVAL)

async def relay(question):
    ws_url = await find_chatgpt_ws_url()
    # Get existing messages count before sending
    async with websockets.connect(ws_url, max_size=10*1024*1024) as ws:
        cdp = CDP(ws)

        await send_message(cdp, question)
        reply = await wait_for_reply(cdp)
        print(reply)

def main():
    if len(sys.argv) < 2:
        print("Usage: python chatgpt_relay.py 'your question'", file=sys.stderr)
        sys.exit(1)
    try:
        asyncio.run(relay(sys.argv[1]))
    except TimeoutError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
