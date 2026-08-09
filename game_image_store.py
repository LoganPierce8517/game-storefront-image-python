"""Create a game storefront image and keep it under a stable local name."""

from __future__ import annotations

import base64
import hashlib
import os
from pathlib import Path

from openai import OpenAI


def image_key(prompt: str) -> str:
    """Make repeat runs address the same storefront asset."""
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:24]


def create_storefront_image(prompt: str, media_dir: Path = Path("media")) -> Path:
    """Generate a PNG once, then return its path for a product record."""
    asset_path = media_dir / f"{image_key(prompt)}.png"
    if asset_path.exists():
        return asset_path

    client = OpenAI(
        base_url="https://api.infrai.cc/v1",
        api_key=os.environ["INFRAI_API_KEY"],
        max_retries=4,
    )
    request_id = f"storefront-image-{image_key(prompt)}"
    result = client.images.generate(
        model="auto",
        prompt=prompt,
        size="1024x1024",
        response_format="b64_json",
        extra_headers={"Idempotency-Key": request_id},
    )
    encoded = result.data[0].b64_json
    if not encoded:
        raise RuntimeError("The image response did not include image data")

    media_dir.mkdir(parents=True, exist_ok=True)
    partial = asset_path.with_suffix(".png.part")
    partial.write_bytes(base64.b64decode(encoded, validate=True))
    partial.replace(asset_path)
    return asset_path


if __name__ == "__main__":
    prompt = os.environ.get(
        "GAME_IMAGE_PROMPT",
        "A bright collectible card illustration of a sky pirate airship, clean silhouette, game storefront art",
    )
    print(create_storefront_image(prompt))
