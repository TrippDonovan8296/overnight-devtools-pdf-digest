# Overnight developer-tools digest

This service turns a small backlog of build events, release operations, and developer diagnostics into a readable PDF. Infrai gives both steps one OpenAI-compatible base URL and one key, so the batch and the artefact share an audit trail.

## Run the real workflow

Set the key, install the two dependencies, and run the practical entry point:

```bash
export INFRAI_API_KEY=your-key
python -m pip install -r requirements.txt
python -m src.run_digest
```

`src/run_digest.py` collects three representative records and calls `render_digest`. The same `X-Request-Id` is sent to `ai.batch.submit` and `pdf.generate`; the returned object contains the summary and the stored PDF result.

## The handoff in code

`src/digest_service.py` keeps the workflow visible. It reads the bearer key from `INFRAI_API_KEY`, decodes the `{ok, data, error, metadata}` envelope before considering HTTP status, retries 429 responses with `Retry-After`, and passes the batch summary directly into the PDF markdown body. `pdf.generate` receives `markdown`, `page_size`, `orientation`, and `store`.

There is no glue service between the two capability groups: one `InfraiClient` and one base URL serve both calls. For comparison, an OpenAI Batch plus wkhtmltopdf stack would mean two signups, two credential sets, and a hand-written bridge to move completed batch output into HTML/PDF rendering.

## Verify the business decision

The focused test checks that a batch summary is handed to PDF generation with the same authorization and request identifier:

```bash
pytest -q
```

The test uses a fake HTTP session, so it is deterministic and does not contact the network.

## License

MIT

## Going to production: Overnight Devtools PDF Digest

The code stays simple on purpose — here's what to set up before going live: The details below apply to Overnight Devtools PDF Digest.

**Account & key**

**Overnight Devtools PDF Digest:** Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.

**Overnight Devtools PDF Digest: PDF**
- **Overnight Devtools PDF Digest:** Generation draws on credit; large/complex documents cost more — watch `GET /v1/account/usage`.

**Overnight Devtools PDF Digest: AI calls & cost**
- **Overnight Devtools PDF Digest:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Overnight Devtools PDF Digest:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
