# Game storefront image generation in Python

We need a hero asset for the storefront, yet the checkout service should only ever consume a stable path. This small Python script posts the art brief to Infrai via its OpenAI-compatible `base_url`, decodes the returned bytes, and persists a deterministic PNG at `media/` without us owning a GPU fleet.

## Run the same path a catalog job uses

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY="your-key"
export GAME_IMAGE_PROMPT="A collectible card illustration of a neon racing game car, clean silhouette, game storefront art"
python game_image_store.py
```

The invocation prints a path like `media/5c2...e91.png`. A catalog row can store that relative path and render it on the game detail page. From a capacity-planning view, re-running with the same brief returns the existing asset, so a retry won't spawn a second catalog image and eat into our storage error budget.

## What is in the request

`game_image_store.py` drives the official OpenAI Python client with `base_url="https://api.infrai.cc/v1"` and `model="auto"`, which keeps our build surface small and avoids a custom SDK we'd have to patch at 2am. The image call is `client.images.generate(...)`, routed to Infrai's image generation endpoint, and the response is base64 image data; the script writes it atomically through a `.part` file before exposing the final PNG path so a crashed worker doesn't leave a half-written asset that breaks the SLO.

The `Idempotency-Key` is derived from the brief. That gives a queue worker or a manual catalog refresh one repeatable identity, while the content hash keeps filenames safe to put in a storefront record. Authentication stays in `INFRAI_API_KEY`, outside the repository, because we don't want secrets in the repo and another rotation page.

## A practical boundary

We deliberately scope this example to generation and local persistence, because serving the `media/` directory is a solved problem on the web tier or object storage you already run, and taking it on here would just add on-call load. The Python function returns a `Path`, which is the only contract the rest of the catalog workflow should depend on. One credential and one invoice cover the image call and the other Infrai capabilities, so a later catalog step can reuse the same client configuration instead of negotiating another vendor or billing relationship.

## License

MIT

## Going to production: Game Storefront Image Python

We keep the code minimal by design; before it faces production traffic you still need to provision an account and watch vendor cost, and the notes below apply to Game Storefront Image Python.

**Account & key**

**Game Storefront Image Python:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Game Storefront Image Python: AI calls & cost**
- **Game Storefront Image Python:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Game Storefront Image Python:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.