from __future__ import annotations

import json
import struct
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any


MAGIC = b"NDIM"
VERSION = 1
HEADER = struct.Struct(">4sHHI")


@dataclass(frozen=True)
class BootImage:
    name: str
    machine: str
    payload: dict[str, Any]

    def to_bytes(self) -> bytes:
        body = json.dumps(
            {"name": self.name, "machine": self.machine, "payload": self.payload},
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        compressed = zlib.compress(body, level=9)
        return HEADER.pack(MAGIC, VERSION, 0, len(compressed)) + compressed

    @classmethod
    def from_bytes(cls, blob: bytes) -> "BootImage":
        if len(blob) < HEADER.size:
            raise ValueError("boot image is too small")
        magic, version, _flags, size = HEADER.unpack(blob[: HEADER.size])
        if magic != MAGIC:
            raise ValueError("not a NovaDesk boot image")
        if version != VERSION:
            raise ValueError(f"unsupported boot image version {version}")
        compressed = blob[HEADER.size : HEADER.size + size]
        if len(compressed) != size:
            raise ValueError("boot image payload is truncated")
        doc = json.loads(zlib.decompress(compressed).decode("utf-8"))
        return cls(name=doc["name"], machine=doc["machine"], payload=doc["payload"])

    def write(self, path: str | Path) -> None:
        Path(path).write_bytes(self.to_bytes())

    @classmethod
    def read(cls, path: str | Path) -> "BootImage":
        return cls.from_bytes(Path(path).read_bytes())
