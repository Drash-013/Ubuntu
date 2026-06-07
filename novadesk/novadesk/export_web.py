from __future__ import annotations

import base64
import json
from pathlib import Path

from .build_os import DEFAULT_IMAGE, build_image
from .image import BootImage


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_HTML = ROOT / "novadesk.html"


def export_html(image_path: Path = DEFAULT_IMAGE, out_path: Path = DEFAULT_HTML) -> Path:
    if not image_path.exists():
        build_image(image_path)
    image = BootImage.read(image_path)
    encoded = base64.b64encode(image.to_bytes()).decode("ascii")
    html = TEMPLATE.replace("__IMAGE_B64__", encoded).replace("__PAYLOAD_JSON__", json.dumps(image.payload))
    out_path.write_text(html, encoding="utf-8")
    return out_path


def main() -> None:
    print(f"wrote {export_html()}")


TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>NovaDesk on NovaCell</title>
<style>
html, body { margin: 0; height: 100%; background: #111820; font-family: system-ui, sans-serif; }
#screen { width: 100vw; height: 100vh; display: block; touch-action: none; }
</style>
</head>
<body>
<canvas id="screen" width="960" height="600"></canvas>
<script>
const bootImageBase64 = "__IMAGE_B64__";
const imagePayload = __PAYLOAD_JSON__;
const state = structuredClone(imagePayload.state);
const widgets = imagePayload.scenes[imagePayload.boot].widgets;
const canvas = document.getElementById("screen");
const ctx = canvas.getContext("2d");
const logical = {w: 960, h: 600};

function resize() {
  const dpr = window.devicePixelRatio || 1;
  canvas.width = Math.floor(window.innerWidth * dpr);
  canvas.height = Math.floor(window.innerHeight * dpr);
  ctx.setTransform(canvas.width / logical.w, 0, 0, canvas.height / logical.h, 0, 0);
  draw();
}

function visible(widget) {
  if (widget.when && widget.when !== state.active) return false;
  if (widget.kind === "panel" && widget.id !== state.active) return false;
  return true;
}

function hit(widget, x, y) {
  return x >= (widget.x || 0) && x <= (widget.x || 0) + (widget.w || 0) &&
    y >= (widget.y || 0) && y <= (widget.y || 0) + (widget.h || 0);
}

function intent(name) {
  if (["about", "notes", "system"].includes(name)) {
    state.active = name;
    state.focused = name === "notes" ? "notes" : "";
  } else if (name === "focus_notes") {
    state.focused = "notes";
  } else if (name === "clear_notes") {
    state.notes = "";
    state.focused = "notes";
  } else if (name === "toggle_theme") {
    state.theme = state.theme === "day" ? "night" : "day";
  }
  draw();
}

function tap(clientX, clientY) {
  const r = canvas.getBoundingClientRect();
  const x = (clientX - r.left) * logical.w / r.width;
  const y = (clientY - r.top) * logical.h / r.height;
  const list = widgets.filter(visible).reverse();
  for (const widget of list) {
    if (!hit(widget, x, y)) continue;
    if (widget.intent) return intent(widget.intent);
    if (widget.kind === "field") state.focused = widget.id;
  }
  draw();
}

function draw() {
  ctx.fillStyle = state.theme === "night" ? "#20262d" : "#dfe7e4";
  ctx.fillRect(0, 0, logical.w, logical.h);
  for (const widget of widgets.filter(visible)) drawWidget(widget);
}

function drawWidget(w) {
  if (w.kind === "bar" || w.kind === "rail") {
    ctx.fillStyle = w.color; ctx.fillRect(w.x, w.y, w.w, w.h);
  } else if (w.kind === "text") {
    ctx.fillStyle = w.color; ctx.font = `${w.size || 12}px system-ui`; ctx.fillText(w.text, w.x, w.y + (w.size || 12));
  } else if (w.kind === "button") {
    ctx.fillStyle = "#f5f7f8"; ctx.strokeStyle = "#637180"; ctx.lineWidth = 1;
    ctx.fillRect(w.x, w.y, w.w, w.h); ctx.strokeRect(w.x, w.y, w.w, w.h);
    ctx.fillStyle = "#121820"; ctx.font = "700 11px system-ui"; ctx.textAlign = "center"; ctx.textBaseline = "middle";
    ctx.fillText(w.label, w.x + w.w / 2, w.y + w.h / 2); ctx.textAlign = "start"; ctx.textBaseline = "alphabetic";
  } else if (w.kind === "panel") {
    ctx.fillStyle = "#fbfcfc"; ctx.strokeStyle = "#8ea0a7"; ctx.fillRect(w.x, w.y, w.w, w.h); ctx.strokeRect(w.x, w.y, w.w, w.h);
    ctx.fillStyle = "#e7eeee"; ctx.fillRect(w.x, w.y, w.w, 38); ctx.strokeRect(w.x, w.y, w.w, 38);
    ctx.fillStyle = "#17212b"; ctx.font = "700 13px system-ui"; ctx.fillText(w.title, w.x + 16, w.y + 25);
  } else if (w.kind === "field") {
    ctx.fillStyle = "#fff"; ctx.strokeStyle = state.focused === w.id ? "#2f7366" : "#9aa8ad"; ctx.lineWidth = state.focused === w.id ? 2 : 1;
    ctx.fillRect(w.x, w.y, w.w, w.h); ctx.strokeRect(w.x, w.y, w.w, w.h);
    ctx.fillStyle = "#111820"; ctx.font = "14px ui-monospace, monospace";
    wrap(String(state.notes || ""), 62).forEach((line, i) => ctx.fillText(line, w.x + 12, w.y + 26 + i * 18));
  } else if (w.kind === "meter") {
    ctx.fillStyle = "#1c2830"; ctx.font = "11px system-ui"; ctx.fillText(w.label, w.x, w.y - 6);
    ctx.fillStyle = "#e7eeee"; ctx.strokeStyle = "#85959c"; ctx.fillRect(w.x, w.y, w.w, w.h); ctx.strokeRect(w.x, w.y, w.w, w.h);
    ctx.fillStyle = "#3c8d7b"; ctx.fillRect(w.x, w.y, w.w * w.value, w.h);
  }
}

function wrap(text, width) {
  const out = [];
  for (const raw of text.split("\\n")) {
    let line = raw;
    while (line.length > width) { out.push(line.slice(0, width)); line = line.slice(width); }
    out.push(line);
  }
  return out;
}

canvas.addEventListener("pointerdown", e => tap(e.clientX, e.clientY));
window.addEventListener("keydown", e => {
  if (state.focused !== "notes") return;
  if (e.key === "Backspace") state.notes = String(state.notes || "").slice(0, -1);
  else if (e.key === "Enter") state.notes = String(state.notes || "") + "\\n";
  else if (e.key.length === 1) state.notes = String(state.notes || "") + e.key;
  else return;
  e.preventDefault(); draw();
});
window.addEventListener("resize", resize);
resize();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
