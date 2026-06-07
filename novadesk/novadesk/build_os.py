from __future__ import annotations

from pathlib import Path

from .image import BootImage


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = ROOT / "novadesk.ndimg"


def build_payload() -> dict:
    return {
        "boot": "desktop",
        "state": {
            "active": "about",
            "notes": "NovaDesk notes are stored in the custom keeper plane.",
            "focused": "",
            "theme": "day",
        },
        "scenes": {
            "desktop": {
                "background": "#dfe7e4",
                "widgets": [
                    {"kind": "bar", "x": 0, "y": 0, "w": 960, "h": 42, "color": "#17212b"},
                    {"kind": "text", "x": 18, "y": 12, "text": "NovaDesk OS", "color": "#f7fbff", "size": 14},
                    {"kind": "text", "x": 776, "y": 12, "text": "NovaCell online", "color": "#b7d5ca", "size": 12},
                    {"kind": "rail", "x": 0, "y": 42, "w": 78, "h": 558, "color": "#233241"},
                    {"kind": "button", "id": "open_about", "x": 12, "y": 64, "w": 54, "h": 54, "label": "Info", "intent": "about"},
                    {"kind": "button", "id": "open_notes", "x": 12, "y": 130, "w": 54, "h": 54, "label": "Note", "intent": "notes"},
                    {"kind": "button", "id": "open_system", "x": 12, "y": 196, "w": 54, "h": 54, "label": "Sys", "intent": "system"},
                    {"kind": "panel", "id": "about", "x": 112, "y": 78, "w": 390, "h": 250, "title": "About NovaDesk"},
                    {"kind": "text", "when": "about", "x": 136, "y": 128, "text": "Booted from a NovaDesk .ndimg image", "color": "#111820", "size": 13},
                    {"kind": "text", "when": "about", "x": 136, "y": 158, "text": "Custom hardware planes: vision, touch, keys, pulse, store", "color": "#111820", "size": 12},
                    {"kind": "text", "when": "about", "x": 136, "y": 188, "text": "No PC bus, BIOS, Unix ABI, or commodity CPU ISA", "color": "#111820", "size": 12},
                    {"kind": "panel", "id": "notes", "x": 112, "y": 78, "w": 560, "h": 360, "title": "Notes"},
                    {"kind": "field", "when": "notes", "id": "notes", "x": 136, "y": 128, "w": 512, "h": 238},
                    {"kind": "button", "when": "notes", "id": "focus_notes", "x": 136, "y": 382, "w": 126, "h": 34, "label": "Edit", "intent": "focus_notes"},
                    {"kind": "button", "when": "notes", "id": "clear_notes", "x": 276, "y": 382, "w": 126, "h": 34, "label": "Clear", "intent": "clear_notes"},
                    {"kind": "panel", "id": "system", "x": 112, "y": 78, "w": 500, "h": 310, "title": "System"},
                    {"kind": "meter", "when": "system", "x": 138, "y": 138, "w": 330, "h": 24, "label": "Vision plane", "value": 0.74},
                    {"kind": "meter", "when": "system", "x": 138, "y": 184, "w": 330, "h": 24, "label": "Store plane", "value": 0.22},
                    {"kind": "meter", "when": "system", "x": 138, "y": 230, "w": 330, "h": 24, "label": "Pulse load", "value": 0.36},
                    {"kind": "button", "when": "system", "id": "toggle_theme", "x": 138, "y": 286, "w": 150, "h": 34, "label": "Theme", "intent": "toggle_theme"},
                ],
            }
        },
    }


def build_image(path: Path = DEFAULT_IMAGE) -> Path:
    image = BootImage(name="NovaDesk OS", machine="NovaCell-Flow-1", payload=build_payload())
    image.write(path)
    return path


def main() -> None:
    path = build_image()
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
