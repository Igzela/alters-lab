import asyncio
import base64
import json

import pytest

from tools import cli


class FakeWebSocket:
    def __init__(self, replies):
        self.replies = list(replies)
        self.sent = []
        self.closed = False

    async def send(self, payload):
        self.sent.append(json.loads(payload))

    async def recv(self):
        if not self.replies:
            raise AssertionError("No fake CDP reply queued")
        return json.dumps(self.replies.pop(0))

    async def close(self):
        self.closed = True


def run(coro):
    return asyncio.run(coro)


def target():
    return cli.Target(
        id="target-1",
        url="https://example.test",
        title="Example",
        websocket_url="ws://127.0.0.1:9222/devtools/page/target-1",
    )


def test_cdp_session_send_ignores_events_until_matching_response():
    fake = FakeWebSocket(
        [
            {"method": "Runtime.consoleAPICalled", "params": {}},
            {"id": 1, "result": {"ok": True}},
        ]
    )

    async def scenario():
        session = cli.CDPSession("ws://example")
        session._ws = fake
        return await session.send("Runtime.evaluate", {"expression": "1 + 1"})

    assert run(scenario()) == {"ok": True}
    assert fake.sent == [
        {"id": 1, "method": "Runtime.evaluate", "params": {"expression": "1 + 1"}}
    ]


def test_get_content_reads_body_inner_text(monkeypatch):
    fake = FakeWebSocket(
        [
            {
                "id": 1,
                "result": {
                    "result": {
                        "type": "string",
                        "value": "Hello from the page",
                    }
                },
            }
        ]
    )

    async def open_websocket(self):
        return fake

    monkeypatch.setattr(cli.BrowserAutomation, "_target", lambda self: target())
    monkeypatch.setattr(cli.CDPSession, "_open_websocket", open_websocket)

    assert cli.BrowserAutomation().get_content() == "Hello from the page"
    assert fake.closed is True
    assert fake.sent[0]["method"] == "Runtime.evaluate"
    assert "document.body.innerText" in fake.sent[0]["params"]["expression"]


def test_screenshot_writes_png(monkeypatch, tmp_path):
    png_bytes = b"\x89PNG\r\n\x1a\nfake"
    fake = FakeWebSocket(
        [
            {"id": 1, "result": {}},
            {"id": 2, "result": {"data": base64.b64encode(png_bytes).decode("ascii")}},
        ]
    )

    async def open_websocket(self):
        return fake

    monkeypatch.setattr(cli.BrowserAutomation, "_target", lambda self: target())
    monkeypatch.setattr(cli.CDPSession, "_open_websocket", open_websocket)

    output_path = tmp_path / "shot.png"
    assert cli.BrowserAutomation().screenshot(output_path) == output_path
    assert output_path.read_bytes() == png_bytes
    assert [message["method"] for message in fake.sent] == [
        "Page.enable",
        "Page.captureScreenshot",
    ]


@pytest.mark.parametrize(
    ("method_name", "args", "expected_methods"),
    [
        (
            "click",
            ("button.submit",),
            [
                "Runtime.evaluate",
                "Input.dispatchMouseEvent",
                "Input.dispatchMouseEvent",
                "Input.dispatchMouseEvent",
            ],
        ),
        (
            "type",
            ("input[name=q]", "hello"),
            [
                "Runtime.evaluate",
                "Input.dispatchMouseEvent",
                "Input.dispatchMouseEvent",
                "Input.insertText",
            ],
        ),
    ],
)
def test_click_and_type_use_element_center_and_input_events(
    monkeypatch,
    method_name,
    args,
    expected_methods,
):
    fake = FakeWebSocket(
        [
            {
                "id": 1,
                "result": {
                    "result": {
                        "type": "object",
                        "value": {"ok": True, "x": 10, "y": 20},
                    }
                },
            },
            {"id": 2, "result": {}},
            {"id": 3, "result": {}},
            {"id": 4, "result": {}},
        ]
    )

    async def open_websocket(self):
        return fake

    monkeypatch.setattr(cli.BrowserAutomation, "_target", lambda self: target())
    monkeypatch.setattr(cli.CDPSession, "_open_websocket", open_websocket)

    getattr(cli.BrowserAutomation(), method_name)(*args)

    assert [message["method"] for message in fake.sent] == expected_methods
    assert args[0] in fake.sent[0]["params"]["expression"]
    if method_name == "type":
        assert fake.sent[-1]["params"] == {"text": "hello"}


def test_select_target_prefers_url_match(monkeypatch):
    def fake_read_json(url, *, timeout):
        return [
            {
                "id": "a",
                "type": "page",
                "url": "https://example.test",
                "title": "Example",
                "webSocketDebuggerUrl": "ws://example/a",
            },
            {
                "id": "b",
                "type": "page",
                "url": "https://chatgpt.com/",
                "title": "ChatGPT",
                "webSocketDebuggerUrl": "ws://example/b",
            },
        ]

    monkeypatch.setattr(cli, "_read_json", fake_read_json)

    selected = cli.select_target("http://127.0.0.1:9222", target_url="chatgpt.com")
    assert selected.id == "b"
    assert selected.websocket_url == "ws://example/b"
