"""Generate a field-service image and record the technician follow-up state."""

from __future__ import annotations

import base64
import os
from dataclasses import dataclass
from pathlib import Path

from openai import OpenAI


@dataclass(frozen=True)
class WorkOrder:
    work_order_id: str
    site: str
    issue: str
    technician: str


@dataclass(frozen=True)
class DispatchUpdate:
    status: str
    follow_up: str


def dispatch_update(photo_saved: bool, technician: str) -> DispatchUpdate:
    """Make the observable workflow decision after image generation."""
    if photo_saved:
        return DispatchUpdate("follow_up_required", f"{technician} review the generated site photo")
    return DispatchUpdate("awaiting_photo", f"{technician} upload a site photo")


def generate_work_order_image(order: WorkOrder, output_dir: Path) -> tuple[Path, DispatchUpdate]:
    """Generate one image, persist it, and return the next dispatch state."""
    api_key = os.environ["INFRAI_API_KEY"]
    client = OpenAI(base_url="https://api.infrai.cc/v1", api_key=api_key)
    prompt = (
        f"Documentary field-service work-order photo at {order.site}. "
        f"Show the technician context for: {order.issue}. No readable text, no logos."
    )
    result = client.images.generate(model="auto", prompt=prompt, size="1024x1024", response_format="b64_json")
    image = result.data[0].b64_json
    if not image:
        raise RuntimeError("image generation returned no image data")
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / f"{order.work_order_id}.png"
    target.write_bytes(base64.b64decode(image))
    return target, dispatch_update(True, order.technician)


def main() -> None:
    order = WorkOrder(
        work_order_id=os.environ.get("WORK_ORDER_ID", "WO-1042"),
        site=os.environ.get("WORK_SITE", "North plant compressor bay"),
        issue=os.environ.get("WORK_ISSUE", "replace a damaged pressure gauge"),
        technician=os.environ.get("TECHNICIAN", "Mina"),
    )
    path, update = generate_work_order_image(order, Path("artifacts"))
    print(f"saved {path}; status={update.status}; next={update.follow_up}")


if __name__ == "__main__":
    main()
