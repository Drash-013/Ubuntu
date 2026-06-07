from __future__ import annotations

import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .image import BootImage


WIDTH = 960
HEIGHT = 600


@dataclass
class NovaCell:
    image: BootImage
    state: dict[str, Any] = field(default_factory=dict)
    scene_name: str = ""
    widgets: list[dict[str, Any]] = field(default_factory=list)
    tick_count: int = 0
    event_log: list[str] = field(default_factory=list)

    @classmethod
    def boot(cls, image_path: str | Path) -> "NovaCell":
        image = BootImage.read(image_path)
        if image.machine != "NovaCell-Flow-1":
            raise ValueError(f"unsupported hardware target {image.machine}")
        vm = cls(image=image)
        payload = image.payload
        vm.state.update(payload.get("state", {}))
        vm.scene_name = payload["boot"]
        vm.widgets = payload["scenes"][vm.scene_name]["widgets"]
        vm.event_log.append(f"boot:{image.name}")
        return vm

    @property
    def background(self) -> str:
        scene = self.image.payload["scenes"][self.scene_name]
        if self.state.get("theme") == "night":
            return "#20262d"
        return scene.get("background", "#dfe7e4")

    @property
    def active(self) -> str:
        return str(self.state.get("active", "about"))

    def visible_widgets(self) -> list[dict[str, Any]]:
        active = self.active
        result = []
        for widget in self.widgets:
            condition = widget.get("when")
            widget_id = widget.get("id")
            if condition and condition != active:
                continue
            if widget["kind"] == "panel" and widget_id != active:
                continue
            result.append(widget)
        return result

    def tick(self) -> None:
        self.tick_count += 1

    def tap(self, x: int, y: int) -> None:
        for widget in reversed(self.visible_widgets()):
            if not _contains(widget, x, y):
                continue
            intent = widget.get("intent")
            if intent:
                self.apply_intent(intent)
                self.event_log.append(f"tap:{intent}")
                return
            if widget["kind"] == "field":
                self.state["focused"] = widget["id"]
                self.event_log.append(f"focus:{widget['id']}")
                return

    def text(self, value: str) -> None:
        focused = self.state.get("focused")
        if focused == "notes":
            self.state["notes"] = str(self.state.get("notes", "")) + value
            self.event_log.append("text:notes")

    def key(self, name: str) -> None:
        focused = self.state.get("focused")
        if focused == "notes" and name == "BackSpace":
            self.state["notes"] = str(self.state.get("notes", ""))[:-1]
        elif focused == "notes" and name == "Return":
            self.state["notes"] = str(self.state.get("notes", "")) + "\n"
        self.event_log.append(f"key:{name}")

    def apply_intent(self, intent: str) -> None:
        if intent in {"about", "notes", "system"}:
            self.state["active"] = intent
            self.state["focused"] = "notes" if intent == "notes" else ""
        elif intent == "focus_notes":
            self.state["focused"] = "notes"
        elif intent == "clear_notes":
            self.state["notes"] = ""
            self.state["focused"] = "notes"
        elif intent == "toggle_theme":
            self.state["theme"] = "night" if self.state.get("theme") == "day" else "day"


class NovaDesktop:
    def __init__(self, vm: NovaCell):
        try:
            import tkinter as tk
        except ModuleNotFoundError as exc:
            raise RuntimeError("graphical mode requires Python tkinter support") from exc
        self.tk = tk
        self.vm = vm
        self.root = tk.Tk()
        self.root.title("NovaDesk on NovaCell")
        self.root.geometry(f"{WIDTH}x{HEIGHT}")
        self.root.minsize(720, 450)
        self.canvas = tk.Canvas(self.root, width=WIDTH, height=HEIGHT, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self._tap)
        self.canvas.bind("<B1-Motion>", self._tap)
        self.root.bind("<Key>", self._key)
        self.root.after(16, self._frame)

    def run(self) -> None:
        self.root.mainloop()

    def _scale(self) -> tuple[float, float]:
        return self.canvas.winfo_width() / WIDTH, self.canvas.winfo_height() / HEIGHT

    def _tap(self, event: tk.Event) -> None:
        sx, sy = self._scale()
        self.vm.tap(int(event.x / sx), int(event.y / sy))
        self.draw()

    def _key(self, event: tk.Event) -> None:
        if event.char and event.char >= " ":
            self.vm.text(event.char)
        else:
            self.vm.key(event.keysym)
        self.draw()

    def _frame(self) -> None:
        self.vm.tick()
        self.draw()
        self.root.after(250, self._frame)

    def draw(self) -> None:
        sx, sy = self._scale()
        self.canvas.delete("all")
        self.canvas.create_rectangle(0, 0, WIDTH * sx, HEIGHT * sy, fill=self.vm.background, outline="")
        for widget in self.vm.visible_widgets():
            self._draw_widget(widget, sx, sy)

    def _draw_widget(self, widget: dict[str, Any], sx: float, sy: float) -> None:
        kind = widget["kind"]
        x, y = widget.get("x", 0) * sx, widget.get("y", 0) * sy
        w, h = widget.get("w", 0) * sx, widget.get("h", 0) * sy
        if kind in {"bar", "rail"}:
            self.canvas.create_rectangle(x, y, x + w, y + h, fill=widget["color"], outline="")
        elif kind == "text":
            self.canvas.create_text(x, y, anchor="nw", text=widget["text"], fill=widget["color"], font=("TkDefaultFont", widget.get("size", 12)))
        elif kind == "button":
            self.canvas.create_rectangle(x, y, x + w, y + h, fill="#f5f7f8", outline="#637180", width=1)
            self.canvas.create_text(x + w / 2, y + h / 2, text=widget["label"], fill="#121820", font=("TkDefaultFont", 11, "bold"))
        elif kind == "panel":
            self.canvas.create_rectangle(x, y, x + w, y + h, fill="#fbfcfc", outline="#8ea0a7", width=1)
            self.canvas.create_rectangle(x, y, x + w, y + 38 * sy, fill="#e7eeee", outline="#8ea0a7")
            self.canvas.create_text(x + 16 * sx, y + 11 * sy, anchor="nw", text=widget["title"], fill="#17212b", font=("TkDefaultFont", 13, "bold"))
        elif kind == "field":
            focused = self.vm.state.get("focused") == widget["id"]
            self.canvas.create_rectangle(x, y, x + w, y + h, fill="#ffffff", outline="#2f7366" if focused else "#9aa8ad", width=2 if focused else 1)
            notes = str(self.vm.state.get("notes", ""))
            wrapped = "\n".join(textwrap.wrap(notes, width=66, replace_whitespace=False)) or " "
            self.canvas.create_text(x + 12 * sx, y + 12 * sy, anchor="nw", text=wrapped, fill="#111820", font=("TkFixedFont", 11))
        elif kind == "meter":
            label = widget["label"]
            value = float(widget["value"])
            self.canvas.create_text(x, y - 18 * sy, anchor="nw", text=label, fill="#1c2830", font=("TkDefaultFont", 11))
            self.canvas.create_rectangle(x, y, x + w, y + h, fill="#e7eeee", outline="#85959c")
            self.canvas.create_rectangle(x, y, x + w * value, y + h, fill="#3c8d7b", outline="")


def _contains(widget: dict[str, Any], x: int, y: int) -> bool:
    return (
        widget.get("x", -1) <= x <= widget.get("x", -1) + widget.get("w", 0)
        and widget.get("y", -1) <= y <= widget.get("y", -1) + widget.get("h", 0)
    )
