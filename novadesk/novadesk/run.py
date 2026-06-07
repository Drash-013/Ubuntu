from __future__ import annotations

import argparse
from pathlib import Path

from .build_os import DEFAULT_IMAGE, build_image
from .vm import NovaCell, NovaDesktop


def main() -> None:
    parser = argparse.ArgumentParser(description="Boot NovaDesk OS on NovaCell hardware.")
    parser.add_argument("image", nargs="?", default=str(DEFAULT_IMAGE))
    parser.add_argument("--headless", action="store_true", help="boot and tick without opening a desktop window")
    parser.add_argument("--ticks", type=int, default=1)
    args = parser.parse_args()

    image_path = Path(args.image)
    if not image_path.exists():
        build_image(image_path)

    vm = NovaCell.boot(image_path)
    if args.headless:
        for _ in range(args.ticks):
            vm.tick()
        print(f"booted {vm.image.name} on {vm.image.machine}")
        print(f"scene={vm.scene_name} active={vm.active} ticks={vm.tick_count}")
        print(f"widgets={len(vm.visible_widgets())}")
        return

    NovaDesktop(vm).run()


if __name__ == "__main__":
    main()
