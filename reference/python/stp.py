"""STP reference parser (minimal).

Parses TSV rows in the STP format:
SeqNo \t Timestamp \t Action \t PrimaryKey \t Record
"""

from dataclasses import dataclass
from typing import Iterable, Iterator

@dataclass(frozen=True)
class Row:
    seqno: int
    ts: str
    action: str
    primary_key: str
    record: str

def parse_lines(lines: Iterable[str]) -> Iterator[Row]:
    for line in lines:
        line = line.rstrip("\n")
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) < 4:
            raise ValueError(f"Invalid STP row: {line!r}")
        seqno = int(parts[0])
        ts = parts[1]
        action = parts[2]
        pk = parts[3]
        record = parts[4] if len(parts) > 4 else ""
        yield Row(seqno=seqno, ts=ts, action=action, primary_key=pk, record=record)
