#!/usr/bin/env python3
"""Small CDP automation CLI for a locally running Chrome instance.

Chrome must already be running with a remote debugging endpoint, for example:
    google-chrome --remote-debugging-port=9222

For a GUI Chrome instance that keeps CDP on port 9222 and routes traffic through
the local Clash Verge proxy, use:
    tools/start_chrome_proxy.sh
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_ENDPOINT = os.environ.get("CDP_ENDPOINT", "http://127.0.0.1:9222")


class CDPError(RuntimeError):
    """Raised when Chrome or a CDP command returns an error."""


@dataclass(frozen=True)
class Target:
    id: str
    url: str
    title: str
    websocket_url: str


def _normalize_endpoint(endpoint: str) -> str:
    endpoint = endpoint.rstrip("/")
    if endpoint.startswith("ws://") or endpoint.startswith("wss://"):
        return endpoint
    if not endpoint.startswith(("http://", "https://")):
        endpoint = f"http://{endpoint}"
    return endpoint


def _read_json(url: str, *, timeout: float) -> Any:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise CDPError(f"Cannot reach Chrome debugging endpoint {url}: {exc}") from exc


def _request_json(url: str, *, method: str, timeout: float) -> Any:
    request = urllib.request.Request(url, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise CDPError(f"Chrome debugging endpoint request failed for {url}: {exc}") from exc


def list_targets(endpoint: str = DEFAULT_ENDPOINT, *, timeout: float = 5.0) -> list[Target]:
    """Return controllable page targets from Chrome's /json/list endpoint."""

    endpoint = _normalize_endpoint(endpoint)
    if endpoint.startswith(("ws://", "wss://")):
        return [
            Target(
                id="direct",
                url="",
                title="direct websocket",
                websocket_url=endpoint,
            )
        ]

    raw_targets = _read_json(f"{endpoint}/json/list", timeout=timeout)
    targets: list[Target] = []
    for item in raw_targets:
        if item.get("type") != "page" or not item.get("webSocketDebuggerUrl"):
            continue
        targets.append(
            Target(
                id=str(item.get("id", "")),
                url=str(item.get("url", "")),
                title=str(item.get("title", "")),
                websocket_url=str(item["webSocketDebuggerUrl"]),
            )
        )
    return targets


def _create_target(endpoint: str, *, timeout: float) -> Target:
    endpoint = _normalize_endpoint(endpoint)
    if endpoint.startswith(("ws://", "wss://")):
        raise CDPError("Cannot create a tab from a direct WebSocket endpoint")

    encoded = urllib.parse.quote("about:blank", safe="")
    item = _request_json(f"{endpoint}/json/new?{encoded}", method="PUT", timeout=timeout)
    websocket_url = item.get("webSocketDebuggerUrl")
    if not websocket_url:
        raise CDPError("Chrome created a target without a WebSocket debugger URL")
    return Target(
        id=str(item.get("id", "")),
        url=str(item.get("url", "")),
        title=str(item.get("title", "")),
        websocket_url=str(websocket_url),
    )


def select_target(
    endpoint: str = DEFAULT_ENDPOINT,
    *,
    target_url: str | None = None,
    timeout: float = 5.0,
) -> Target:
    """Select a page target, preferring a URL substring match when provided."""

    targets = list_targets(endpoint, timeout=timeout)
    if target_url:
        for target in targets:
            if target_url in target.url:
                return target
        raise CDPError(f"No Chrome page target URL contains {target_url!r}")
    if targets:
        return targets[0]
    return _create_target(endpoint, timeout=timeout)


class CDPSession:
    """Minimal async CDP JSON-RPC session."""

    def __init__(self, websocket_url: str, *, timeout: float = 30.0) -> None:
        self.websocket_url = websocket_url
        self.timeout = timeout
        self._next_id = 0
        self._ws: Any = None

    async def __aenter__(self) -> "CDPSession":
        self._ws = await self._open_websocket()
        return self

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        if self._ws is not None:
            await self._ws.close()

    async def _open_websocket(self) -> Any:
        try:
            import websockets
        except ImportError as exc:
            raise CDPError(
                "Python package 'websockets' is required. Install it with: "
                "python3 -m pip install websockets"
            ) from exc
        return await websockets.connect(  # type: ignore[attr-defined]
            self.websocket_url,
            max_size=32 * 1024 * 1024,
            open_timeout=self.timeout,
        )

    async def send(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        if self._ws is None:
            raise CDPError("CDP session is not connected")

        self._next_id += 1
        message_id = self._next_id
        payload: dict[str, Any] = {"id": message_id, "method": method}
        if params is not None:
            payload["params"] = params

        await self._ws.send(json.dumps(payload))
        while True:
            raw = await asyncio.wait_for(self._ws.recv(), timeout=self.timeout)
            message = json.loads(raw)
            if message.get("id") != message_id:
                continue
            if "error" in message:
                error = message["error"]
                raise CDPError(f"{method} failed: {error.get('message', error)}")
            return message.get("result", {})

    async def recv_event(self, event_name: str, *, timeout: float | None = None) -> dict[str, Any]:
        if self._ws is None:
            raise CDPError("CDP session is not connected")

        deadline = timeout if timeout is not None else self.timeout
        while True:
            raw = await asyncio.wait_for(self._ws.recv(), timeout=deadline)
            message = json.loads(raw)
            if message.get("method") == event_name:
                return message.get("params", {})


class BrowserAutomation:
    """Automation facade backed by a single Chrome page target."""

    def __init__(
        self,
        endpoint: str = DEFAULT_ENDPOINT,
        *,
        target_url: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.endpoint = endpoint
        self.target_url = target_url
        self.timeout = timeout

    def _target(self) -> Target:
        return select_target(self.endpoint, target_url=self.target_url, timeout=min(self.timeout, 10.0))

    async def _with_session(self) -> CDPSession:
        target = self._target()
        return CDPSession(target.websocket_url, timeout=self.timeout)

    async def anavigate(self, url: str) -> str:
        async with await self._with_session() as session:
            await session.send("Page.enable")
            await session.send("Page.navigate", {"url": url})
            try:
                await session.recv_event("Page.loadEventFired", timeout=self.timeout)
            except asyncio.TimeoutError:
                pass
            result = await session.send(
                "Runtime.evaluate",
                {"expression": "location.href", "returnByValue": True},
            )
            return str(result.get("result", {}).get("value", url))

    async def ascreenshot(self, path: str | os.PathLike[str]) -> Path:
        output_path = Path(path)
        async with await self._with_session() as session:
            await session.send("Page.enable")
            result = await session.send("Page.captureScreenshot", {"format": "png", "fromSurface": True})
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(base64.b64decode(result["data"]))
        return output_path

    async def aget_content(self) -> str:
        async with await self._with_session() as session:
            result = await session.send(
                "Runtime.evaluate",
                {
                    "expression": "document.body ? document.body.innerText : ''",
                    "returnByValue": True,
                },
            )
            return str(result.get("result", {}).get("value", ""))

    async def aevaluate(self, js: str) -> Any:
        async with await self._with_session() as session:
            result = await session.send(
                "Runtime.evaluate",
                {
                    "expression": js,
                    "awaitPromise": True,
                    "returnByValue": True,
                },
            )
            payload = result.get("result", {})
            if payload.get("subtype") == "error":
                description = payload.get("description", "JavaScript evaluation failed")
                raise CDPError(description)
            return payload.get("value")

    async def _element_center(self, session: CDPSession, selector: str) -> tuple[float, float]:
        expression = f"""
(() => {{
  const el = document.querySelector({json.dumps(selector)});
  if (!el) return {{ ok: false, error: 'No element matches selector' }};
  el.scrollIntoView({{ block: 'center', inline: 'center' }});
  const rect = el.getBoundingClientRect();
  return {{
    ok: true,
    x: rect.left + rect.width / 2,
    y: rect.top + rect.height / 2
  }};
}})()
"""
        result = await session.send(
            "Runtime.evaluate",
            {"expression": expression, "returnByValue": True},
        )
        value = result.get("result", {}).get("value", {})
        if not value.get("ok"):
            raise CDPError(f"{value.get('error', 'Cannot find element')}: {selector}")
        return float(value["x"]), float(value["y"])

    async def aclick(self, selector: str) -> None:
        async with await self._with_session() as session:
            x, y = await self._element_center(session, selector)
            event = {"x": x, "y": y, "button": "left", "clickCount": 1}
            await session.send("Input.dispatchMouseEvent", {"type": "mouseMoved", **event})
            await session.send("Input.dispatchMouseEvent", {"type": "mousePressed", **event})
            await session.send("Input.dispatchMouseEvent", {"type": "mouseReleased", **event})

    async def atype(self, selector: str, text: str) -> None:
        async with await self._with_session() as session:
            x, y = await self._element_center(session, selector)
            event = {"x": x, "y": y, "button": "left", "clickCount": 1}
            await session.send("Input.dispatchMouseEvent", {"type": "mousePressed", **event})
            await session.send("Input.dispatchMouseEvent", {"type": "mouseReleased", **event})
            await session.send("Input.insertText", {"text": text})

    def navigate(self, url: str) -> str:
        return asyncio.run(self.anavigate(url))

    def screenshot(self, path: str | os.PathLike[str]) -> Path:
        return asyncio.run(self.ascreenshot(path))

    def get_content(self) -> str:
        return asyncio.run(self.aget_content())

    def click(self, selector: str) -> None:
        asyncio.run(self.aclick(selector))

    def type(self, selector: str, text: str) -> None:
        asyncio.run(self.atype(selector, text))

    def evaluate(self, js: str) -> Any:
        return asyncio.run(self.aevaluate(js))


def _default_client(endpoint: str = DEFAULT_ENDPOINT, target_url: str | None = None, timeout: float = 30.0) -> BrowserAutomation:
    return BrowserAutomation(endpoint=endpoint, target_url=target_url, timeout=timeout)


def navigate(url: str, *, endpoint: str = DEFAULT_ENDPOINT, target_url: str | None = None, timeout: float = 30.0) -> str:
    return _default_client(endpoint, target_url, timeout).navigate(url)


def screenshot(
    path: str | os.PathLike[str],
    *,
    endpoint: str = DEFAULT_ENDPOINT,
    target_url: str | None = None,
    timeout: float = 30.0,
) -> Path:
    return _default_client(endpoint, target_url, timeout).screenshot(path)


def get_content(*, endpoint: str = DEFAULT_ENDPOINT, target_url: str | None = None, timeout: float = 30.0) -> str:
    return _default_client(endpoint, target_url, timeout).get_content()


def click(
    selector: str,
    *,
    endpoint: str = DEFAULT_ENDPOINT,
    target_url: str | None = None,
    timeout: float = 30.0,
) -> None:
    _default_client(endpoint, target_url, timeout).click(selector)


def type(
    selector: str,
    text: str,
    *,
    endpoint: str = DEFAULT_ENDPOINT,
    target_url: str | None = None,
    timeout: float = 30.0,
) -> None:
    _default_client(endpoint, target_url, timeout).type(selector, text)


def evaluate(js: str, *, endpoint: str = DEFAULT_ENDPOINT, target_url: str | None = None, timeout: float = 30.0) -> Any:
    return _default_client(endpoint, target_url, timeout).evaluate(js)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Control an existing Chrome tab through CDP.")
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT, help="Chrome debugging endpoint or direct tab WebSocket URL.")
    parser.add_argument("--target-url", help="Select the first existing tab whose URL contains this text.")
    parser.add_argument("--timeout", type=float, default=30.0, help="CDP command timeout in seconds.")

    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("targets", help="List controllable page targets.")

    navigate_parser = subparsers.add_parser("navigate", help="Navigate the selected tab.")
    navigate_parser.add_argument("url")

    screenshot_parser = subparsers.add_parser("screenshot", help="Capture a PNG screenshot.")
    screenshot_parser.add_argument("path")

    subparsers.add_parser("get-content", help="Print document.body.innerText.")

    click_parser = subparsers.add_parser("click", help="Click the center of the first element matching a CSS selector.")
    click_parser.add_argument("selector")

    type_parser = subparsers.add_parser("type", help="Click a CSS selector and insert text.")
    type_parser.add_argument("selector")
    type_parser.add_argument("text")

    evaluate_parser = subparsers.add_parser("evaluate", help="Evaluate JavaScript in the selected tab.")
    evaluate_parser.add_argument("js")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    client = BrowserAutomation(endpoint=args.endpoint, target_url=args.target_url, timeout=args.timeout)

    if args.command == "targets":
        print(json.dumps([target.__dict__ for target in list_targets(args.endpoint, timeout=args.timeout)], indent=2))
    elif args.command == "navigate":
        print(client.navigate(args.url))
    elif args.command == "screenshot":
        print(client.screenshot(args.path))
    elif args.command == "get-content":
        print(client.get_content())
    elif args.command == "click":
        client.click(args.selector)
    elif args.command == "type":
        client.type(args.selector, args.text)
    elif args.command == "evaluate":
        print(json.dumps(client.evaluate(args.js), ensure_ascii=False))
    else:
        raise CDPError(f"Unsupported command: {args.command}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CDPError as exc:
        raise SystemExit(f"error: {exc}") from exc
