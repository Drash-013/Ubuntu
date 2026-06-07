# NovaDesk OS Design

NovaDesk OS is not based on Windows, macOS, Linux, Unix, or POSIX. It is a small scene-oriented desktop system built for NovaCell.

## Concepts

- A `scene` is a runnable UI surface.
- A `surface` is a rectangular interactive layer.
- An `intent` is a user action emitted by a control.
- A `keeper` is persistent OS state stored by the hardware `store` plane.

## User Interface

The first boot scene is a desktop with:

- top status band
- launcher rail
- Notes app
- System panel
- About panel

Keyboard text is routed to the focused field in Notes. Pointer, mouse, and touch contact events all use the same tap path.

## Why This Is Not Unix-Like

NovaDesk has no files, directories, fork/exec, shell process model, terminal TTY, POSIX permissions, sockets, or Unix syscalls. Application state is represented as keeper values and scenes.

## Compatibility Limits

The hardware can emulate a friendly desktop OS, but it cannot run mainstream OS binaries without either:

- adding a known architecture compatibility layer, which violates the hardware requirement, or
- porting those operating systems to NovaCell, which is a separate multi-year engineering effort.
