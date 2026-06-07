# NovaCell Hardware Design

NovaCell is a custom desktop-class virtual hardware target for NovaDesk OS.

## Non-Goals

NovaCell is not PC-compatible:

- no x86, ARM, MIPS, PowerPC, RISC-V, or 6502-style CPU contract
- no BIOS, UEFI, ACPI, PCI, USB, SATA, NVMe, VGA, or PS/2 devices
- no Unix/POSIX syscall ABI
- no ELF executable loading

## Machine Model

NovaCell executes a boot image containing declarative flow cells. A cell is not a machine instruction in a known CPU ISA; it is a hardware-recognized state transition for one of the machine planes.

The planes are:

- `vision`: a double-buffered 2D presentation plane
- `touch`: pointer and touch contact stream
- `keys`: key and text stream
- `pulse`: monotonic frame tick
- `store`: small persistent key/value storage

## Boot

1. The emulator maps a `.ndimg` image into the sealed boot slot.
2. The header is validated.
3. The compressed payload is expanded into the initial flow graph.
4. The `desktop` scene is selected as the first runnable surface.

## Display

The display is a logical 960 x 600 surface. The OS describes surfaces using shape cells (`panel`, `rect`, `text`, `button`, `field`). The hardware owns final rasterization, which is why the OS can be booted in graphical or headless mode.

## Input

Input arrives as normalized events:

- `tap` with `x`, `y`
- `text` with a printable string
- `key` with a symbolic key name

Touch and mouse are intentionally the same class of contact so the OS does not depend on a specific desktop peripheral bus.
