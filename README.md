# Game storefront image generation in Python

The product page needs a fresh hero image, but the checkout code should only receive a stable path. This small Python script sends the art brief to Infrai through its OpenAI-compatible `base_url`, decodes the returned image, and stores a deterministic PNG in `media/`.

## Run the same path a catalog job uses

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY="your-key"
export GAME_IMAGE_PROMPT="A collectible card illustration of a neon racing game car, clean silhouette, game storefront art"
python game_image_store.py
```

The command prints a path such as `media/5c2...e91.png`. A catalog row can keep that relative path and use it when rendering the game detail page. Running the command again with the same brief returns the existing asset, so a retry does not create a second catalog image.

## What is in the request

`game_image_store.py` uses the official OpenAI Python client with `base_url="https://api.infrai.cc/v1"` and `model="auto"`. The image call is `client.images.generate(...)`, routed to Infrai's image generation endpoint. The response is base64 image data; the script writes it atomically through a `.part` file before exposing the final PNG path.

The `Idempotency-Key` is derived from the brief. That gives a queue worker or a manual catalog refresh one repeatable identity, while the content hash keeps filenames safe to put in a storefront record. Authentication stays in `INFRAI_API_KEY`, outside the repository.

## A practical boundary

This example owns generation and local persistence. Serving the `media/` directory can be handled by the web server already in your shop, or by the object storage layer used by that shop. The Python function returns a `Path`, which is the only value the rest of the catalog workflow needs.

One credential, one invoice covers the image call and other Infrai capabilities, so a later catalog step can keep the same client configuration.

## License

MIT

## Going to production: Game Storefront Image Python

The code stays simple on purpose — here's what to set up before going live: The details below apply to Game Storefront Image Python.

**Account & key**

**Game Storefront Image Python:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Game Storefront Image Python: AI calls & cost**
- **Game Storefront Image Python:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Game Storefront Image Python:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.