from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from novadesk.build_os import build_image
from novadesk.image import BootImage
from novadesk.vm import NovaCell


class BootTests(unittest.TestCase):
    def test_image_round_trips_and_boots(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "os.ndimg"
            build_image(path)
            image = BootImage.read(path)
            self.assertEqual(image.machine, "NovaCell-Flow-1")
            vm = NovaCell.boot(path)
            self.assertEqual(vm.scene_name, "desktop")
            self.assertEqual(vm.active, "about")

    def test_desktop_interactions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "os.ndimg"
            build_image(path)
            vm = NovaCell.boot(path)
            vm.tap(20, 145)
            self.assertEqual(vm.active, "notes")
            vm.text("!")
            self.assertTrue(str(vm.state["notes"]).endswith("!"))
            vm.tap(285, 392)
            self.assertEqual(vm.state["notes"], "")


if __name__ == "__main__":
    unittest.main()
