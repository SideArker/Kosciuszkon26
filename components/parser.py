import csv
from dataclasses import dataclass
from typing import List


@dataclass
class TexbatEntry:
    c_n0: float
    doppler: float
    carrier_phase: float
    code_phase: float


def parse_csv(filepath: str) -> List[TexbatEntry]:
    entries = []
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            entry = TexbatEntry(
                c_n0=float(row["C_N0"]),
                doppler=float(row["Doppler"]),
                carrier_phase=float(row["Carrier_Phase"]),
                code_phase=float(row["Code_Phase"]),
            )
            entries.append(entry)
    return entries