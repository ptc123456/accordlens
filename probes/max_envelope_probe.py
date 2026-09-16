# v0.1.0
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
from dataclasses import dataclass, asdict
import hashlib
import json


@allow_storage
@dataclass
class SourceRow:
    uri: str
    commit: str
    blob: str
    digest: str
    length: u32
    scope: str


@allow_storage
@dataclass
class AnchorRow:
    anchor: str
    level: u16
    role: str
    parent: u16
    start: u32
    end: u32
    subtree_end: u32


@allow_storage
@dataclass
class RangeRow:
    start: u32
    end: u32
    stored_start: u32
    stored_end: u32


@allow_storage
@dataclass
class IntegrityRow:
    start: u32
    end: u32
    digest: str


@allow_storage
@dataclass
class ResultRow:
    consumer: str
    verdict: str
    action_type: str
    target: str
    required_value: str


class MaxEnvelopeProbe(gl.Contract):
    sources: TreeMap[u256, SourceRow]
    anchors: TreeMap[u256, AnchorRow]
    ranges: TreeMap[u256, RangeRow]
    integrity: TreeMap[u256, IntegrityRow]
    results: TreeMap[u256, ResultRow]
    selected: bytes
    version: u256
    payload_digest: str
    payload_size: u32

    def __init__(self):
        self.version = u256(0)
        self.selected = b""
        self.payload_digest = ""
        self.payload_size = u32(0)

    @gl.public.write
    def exercise(self, padding: int, counter: int) -> str:
        if padding < 0 or padding > 262145:
            raise ValueError("padding")
        if counter < 0 or counter >= 2**256 - 1:
            raise ValueError("counter overflow")
        sources = []
        anchors = []
        ranges = []
        cores = []
        results = []
        # Independent maximum structural bounds; not a valid authored document.
        for s in range(9):
            sources.append(SourceRow("u" * 2048, "a" * 40, "b" * 40, "c" * 64, u32(65536), "declared"))
            for a in range(129):
                anchors.append(AnchorRow(str(a).zfill(48), u16(6), "informative", u16(128), u32(65534), u32(65535), u32(65536)))
                i = s * 129 + a
                start = i * 8000 // 1161
                end = (i + 1) * 8000 // 1161
                ranges.append(RangeRow(u32(65534), u32(65535), u32(start), u32(end)))
            for c in range(9):
                cores.append(IntegrityRow(u32(c * 65536 // 9), u32((c + 1) * 65536 // 9), "d" * 64))
        for i in range(8):
            results.append(ResultRow(str(i).zfill(48), "CONDITIONAL", "ENDPOINT_MIGRATION", "t" * 256, "v" * 1024))
        selected = b"x" * 8000
        # Positional canonical encoding avoids repeating schema keys 2,403 times.
        payload = json.dumps({"sources": [list(asdict(x).values()) for x in sources], "anchors": [list(asdict(x).values()) for x in anchors], "ranges": [list(asdict(x).values()) for x in ranges], "cores": [list(asdict(x).values()) for x in cores], "results": [list(asdict(x).values()) for x in results], "selected": selected.hex(), "counter": str(counter + 1), "padding": "p" * padding}, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        if len(payload) > 262144:
            raise ValueError("storage budget")
        # Admission/counter validation precedes every storage mutation.
        for i, row in enumerate(sources):
            self.sources[u256(i)] = row
        for i, row in enumerate(anchors):
            self.anchors[u256(i)] = row
        for i, row in enumerate(ranges):
            self.ranges[u256(i)] = row
        for i, row in enumerate(cores):
            self.integrity[u256(i)] = row
        for i, row in enumerate(results):
            self.results[u256(i)] = row
        self.selected = selected
        self.version = u256(counter + 1)
        self.payload_digest = hashlib.sha256(payload).hexdigest()
        self.payload_size = u32(len(payload))
        return self.inspect()

    @gl.public.view
    def inspect(self) -> str:
        return json.dumps({"version": str(self.version), "size": int(self.payload_size), "digest": self.payload_digest, "selected": len(self.selected), "sources": len(self.sources), "anchors": len(self.anchors), "ranges": len(self.ranges), "cores": len(self.integrity), "results": len(self.results)})

    @gl.public.view
    def verify_all(self) -> bool:
        for i in range(9):
            assert len(self.sources[u256(i)].uri) == 2048
        for i in range(1161):
            assert len(self.anchors[u256(i)].anchor) == 48
            assert self.anchors[u256(i)].subtree_end == 65536
            assert self.ranges[u256(i)].stored_start == i * 8000 // 1161
            assert self.ranges[u256(i)].stored_end == (i + 1) * 8000 // 1161
        for i in range(81):
            assert self.integrity[u256(i)].digest == "d" * 64
        for i in range(8):
            assert self.results[u256(i)].required_value == "v" * 1024
        assert self.selected == b"x" * 8000
        return True
