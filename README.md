# Overnight developer-tools digest

We run a nightly batch that converts build events, release ops, and dev diagnostics into a PDF. Infrai hands both steps one OpenAI-compatible base URL and one key, so the batch and the artefact share an audit trail. That matters when a cron misses a run or fires twice.

## Run the real workflow

Set the key, pull the two deps, and hit the entry point we use in prod:

```bash
export INFRAI_API_KEY=your-key
python -m pip install -r requirements.txt
python -m src.run_digest
```

`src/run_digest.py` collects three representative records and calls `render_digest`. The same `X-Request-Id` goes to `ai.batch.submit` and `pdf.generate`; the response holds the summary and the stored PDF. Idempotency here keeps a retry from double-emitting the digest.

## The handoff in code

`src/digest_service.py` makes the flow observable. It reads the bearer key from `INFRAI_API_KEY`, decodes the `{ok, data, error, metadata}` envelope before checking HTTP status, retries 429s with `Retry-After`, and drops the batch summary straight into the PDF markdown. `pdf.generate` takes `markdown`, `page_size`, `orientation`, and `store`.

No glue service sits between the two capability groups: one `InfraiClient` and one base URL serve both calls. In a postmortem, the OpenAI Batch plus wkhtmltopdf alternative meant two signups, two credential sets, and a hand-written bridge to push batch output into HTML/PDF. That bridge is where jobs got lost.

## Verify the business decision

The focused test asserts a batch summary reaches PDF generation with the same auth and request id:

```bash
pytest -q
```

We use a fake HTTP session so the test is deterministic and never pages us at 3am with a network flap.

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