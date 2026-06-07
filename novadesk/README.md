# NovaDesk

NovaDesk is a custom desktop hardware and OS prototype. It deliberately avoids PC-compatible architecture: there is no x86/ARM/RISC-V CPU, BIOS/UEFI, PCI bus, VGA device, POSIX kernel ABI, or Unix-style process model.

The project contains:

- `novadesk/image.py` - bootable image container (`.ndimg`)
- `novadesk/vm.py` - custom virtual hardware and desktop emulator
- `novadesk/build_os.py` - builds the NovaDesk OS boot image
- `novadesk/run.py` - boots the image in the emulator
- `docs/` - hardware and OS design notes

## Run

Build the boot image:

```bash
python3 -m novadesk.build_os
```

Boot in the graphical emulator:

```bash
python3 -m novadesk.run
```

Or export a browser-based virtual desktop:

```bash
python3 -m novadesk.export_web
```

Then open `novadesk.html`.

For environments without a display, run headless verification:

```bash
python3 -m novadesk.run --headless --ticks 3
```

Run tests:

```bash
python3 -m unittest discover -s tests
```

## Scope

This is a working first-stage emulated desktop: it boots a custom OS image, paints a desktop UI, accepts pointer/touch style clicks, accepts keyboard text in the Notes app, and handles a few shell actions.

Running today’s mainstream operating systems on this hardware would require porting those OS kernels and applications to the NovaCell hardware contract. That is outside this repository and conflicts with the requirement to avoid known CPU/PC architecture compatibility.
