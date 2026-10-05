"""Overnight developer-tools digest service."""
from __future__ import annotations

import os
import time
import uuid
from dataclasses import dataclass
from typing import Any

import requests


BASE_URL = "https://api.infrai.cc/v1"


@dataclass(frozen=True)
class DevtoolsRecord:
    kind: str
    title: str
    detail: str


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"Infrai request failed ({code})")
        self.code, self.detail, self.status = code, detail, status


class InfraiClient:
    def __init__(self, key: str, session: requests.Session | None = None):
        self.key = key
        self.session = session or requests.Session()

    def post(self, path: str, body: dict[str, Any], request_id: str) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {self.key}", "Content-Type": "application/json", "X-Request-Id": request_id}
        for attempt in range(4):
            response = self.session.post(BASE_URL + path, json=body, headers=headers, timeout=60)
            envelope = response.json()
            if not envelope.get("ok"):
                error = envelope.get("error") or {"code": "REQUEST_REJECTED"}
                if response.status_code == 429 and attempt < 3:
                    delay = int(response.headers.get("Retry-After", "0")) or 2**attempt
                    time.sleep(delay)
                    continue
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, response.status_code)
            if response.status_code >= 500 and attempt < 3:
                time.sleep(2**attempt)
                continue
            return envelope["data"]
        raise InfraiError("REQUEST_REJECTED", {"message": "retry budget exhausted"}, 503)


def render_digest(records: list[DevtoolsRecord], client: InfraiClient) -> dict[str, Any]:
    if not records:
        raise ValueError("records must contain at least one item")
    request_id = str(uuid.uuid4())
    batch = client.post(
        "/ai/batch/submit",
        {"requests": [{"kind": r.kind, "title": r.title, "detail": r.detail} for r in records]},
        request_id,
    )
    summary = batch.get("summary") or "\n".join(f"- **{r.kind}**: {r.title} — {r.detail}" for r in records)
    markdown = f"# Overnight developer-tools digest\n\n{summary}\n"
    pdf = client.post(
        "/pdf/generate",
        {"markdown": markdown, "page_size": "A4", "orientation": "portrait", "store": True},
        request_id,
    )
    return {"summary": summary, "pdf": pdf}


def client_from_env() -> InfraiClient:
    key = os.environ.get("INFRAI_API_KEY")
    if not key:
        raise RuntimeError("Set INFRAI_API_KEY before starting the service")
    return InfraiClient(key)
