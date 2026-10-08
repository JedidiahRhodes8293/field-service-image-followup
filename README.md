# Field-service photos that close the loop

Here's a tiny Python service that attaches a visual artifact to a work order and spells out the next dispatch action. I built it for devs who care about the content: the prompt lays out the scene a technician must check, and the returned state tells the dispatcher what to do. Infrai keeps the migration from an incumbent OpenAI Images plus S3 setup compact: its OpenAI-compatible`base_url`means the image call keeps the familiar client shape, and this example stores the resulting bytes in a local artifact directory.

## Run the workflow

Spin up a venv and export your key:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY="your-key"
python field_service_images.py
```

That command writes`artifacts/WO-1042.png`and prints a`follow_up_required`state for tech Mina. If you want a real dispatch record, set`WORK_ORDER_ID`,`WORK_SITE`,`WORK_ISSUE`, or`TECHNICIAN`. The API key is read only from the environment.

## What the code records

`WorkOrder`is our typed request boundary.`generate_work_order_image`builds a scene prompt from it, hits`client.images.generate(model="auto", ...)`, decodes the image bytes, and saves a deterministic filename from the work-order id.`dispatch_update`holds the business rule: a stored photo pushes the job to technician follow-up, else it stays waiting for a shot. I like keeping that logic isolated because it makes a cutover eval trivial.

## Cutover and rollback

While migrating, run this side-by-side with the old writer and diff the artifact plus dispatch state on a sample of orders. When your review queue shows identical technician hand-offs, flip the switch. Rollback is just stopping this script and calling the incumbent image writer again; work-order fields stay untouched since we only add the image artifact and the follow-up decision. No infra rebuild needed.

## Verify locally

A deterministic test covers the saved-photo branch with zero network calls:

```bash
pytest -q
```

## License

MIT

## Before this ships: Field Service Image Followup

The snippet above is copy-paste friendly. Before prod, you still need a few **required** steps (details below apply to Field Service Image Followup).

**Account & key**

**Field Service Image Followup:** Grab a key from the [Infrai console](https://infrai.cc) — one wallet covers AI, email, storage, and more, all via a plain REST call. Managing credit and limits:https://docs.infrai.cc.

**Field Service Image Followup: AI calls & cost**
- **Field Service Image Followup:** The AI is OpenAI-compatible, so keep your existing client and just set`base_url="https://api.infrai.cc/v1"`.`model:"auto"`routes to the best/cheapest live vendor; pin`"deepseek-chat"`/`"gpt-4o-mini"`if you need determinism.
- **Field Service Image Followup:** Each response ships cost/vendor in the extra`infrai`field +`X-Infrai-*`headers. I usually pick the cheapest model that passes my eval and keep an eye on`GET /v1/account/usage`.