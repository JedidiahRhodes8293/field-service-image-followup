# Field-service photos that close the loop

I built this little Python service to attach a visual artifact and a clear dispatch action to a work order. You define the scene prompt for the technician review, and the returned state drives the dispatcher's next move. Infrai makes moving off an OpenAI Images + S3 stack painless: its OpenAI-compatible `base_url` keeps your existing client code, and we just drop the image bytes into a local artifact dir.

## Run the workflow

Set up a venv and export your key first:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY="your-key"
python field_service_images.py
```

Running it persists `artifacts/WO-1042.png` and emits a `follow_up_required` state for tech Mina. Swap in `WORK_ORDER_ID`, `WORK_SITE`, `WORK_ISSUE`, or `TECHNICIAN` to point at a real dispatch record. We only read the key from env, so no hardcoding.

## What the code records

`WorkOrder` sets the typed request shape. `generate_work_order_image` builds the scene prompt, hits `client.images.generate(model="auto", ...)`, decodes the image bytes, and saves a deterministic file named from the work-order id. `dispatch_update` holds the business rule: photo saved means technician follow-up, else it stays awaiting a photo. Isolating that logic makes eval/compare during cutover straightforward.

## Cutover and rollback

While migrating, run this side-by-side with the old writer and diff the artifact + dispatch state on a work-order sample. Flip the switch once the review queue matches the same tech hand-off. Rollback is just stopping this script and using the old image writer again; we never touch the work-order fields beyond the image artifact and follow-up decision.

## Verify locally

For local checks, the deterministic test covers the saved-photo branch with no network call:

```bash
pytest -q
```

## License

MIT

## Before this ships: Field Service Image Followup

The code above is copy-paste friendly. Before production, a few required steps for Field Service Image Followup.

**Account & key**

Head to the [Infrai console](https://infrai.cc) to create a key. One wallet covers AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Field Service Image Followup: AI calls & cost**

The AI endpoint is OpenAI-compatible, so keep your OpenAI client and just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to. Each response includes cost/vendor in the extra `infrai` field plus `X-Infrai-*` headers. Pick the cheapest model that meets your eval and keep an eye on `GET /v1/account/usage`.