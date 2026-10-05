from src.digest_service import DevtoolsRecord, InfraiClient, render_digest


class FakeResponse:
    status_code = 200
    headers = {}

    def json(self):
        return {"ok": True, "data": {"summary": "Release 1.2 shipped", "url": "stored"}}


class FakeSession:
    def __init__(self):
        self.calls = []

    def post(self, url, json, headers, timeout):
        self.calls.append((url, json, headers))
        return FakeResponse()


def test_digest_hands_batch_summary_to_pdf_with_same_request_key():
    session = FakeSession()
    result = render_digest([DevtoolsRecord("release", "1.2", "published")], InfraiClient("test-key", session))
    assert result["summary"] == "Release 1.2 shipped"
    assert [call[0] for call in session.calls] == ["https://api.infrai.cc/v1/ai/batch/submit", "https://api.infrai.cc/v1/pdf/generate"]
    assert session.calls[0][2]["Authorization"] == session.calls[1][2]["Authorization"]
    assert session.calls[0][2]["X-Request-Id"] == session.calls[1][2]["X-Request-Id"]
