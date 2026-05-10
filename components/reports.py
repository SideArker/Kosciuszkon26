import json
import os
from datetime import datetime

REPORTS_DIR = os.path.abspath(os.path.join("data", "reports"))


def _ensure_dir() -> None:
    os.makedirs(REPORTS_DIR, exist_ok=True)


def _safe_path(report_id: str) -> str:
    # Strip any directory components from the id itself
    safe_id = os.path.basename(report_id)
    # Only allow alphanumeric, dots, hyphens, underscores
    if not all(c.isalnum() or c in "._-" for c in safe_id):
        raise ValueError(f"Invalid report_id: {report_id!r}")
    resolved = os.path.realpath(os.path.join(REPORTS_DIR, f"{safe_id}.json"))
    if not resolved.startswith(REPORTS_DIR + os.sep):
        raise ValueError(f"Path traversal detected for report_id: {report_id!r}")
    return resolved


def save_report(payload: dict) -> str:
    """Saves a report to disk and returns id"""
    _ensure_dir()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = os.path.basename(payload.get("analyzed_file", "unknown"))
    safe_name = "".join(c if c.isalnum() or c in "._-" else "_" for c in safe_name)
    report_id = f"{ts}_{safe_name}"
    record = {**payload, "id": report_id}
    path = _safe_path(report_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)
    return report_id


def load_all_reports() -> list[dict]:
    """Loads all reports from disk, sorted by timestamp descending."""
    _ensure_dir()
    reports = []
    for fname in sorted(os.listdir(REPORTS_DIR), reverse=True):
        if fname.endswith(".json"):
            try:
                full_path = os.path.realpath(os.path.join(REPORTS_DIR, fname))
                if not full_path.startswith(REPORTS_DIR + os.sep):
                    continue
                with open(full_path, "r", encoding="utf-8") as f:
                    reports.append(json.load(f))
            except (json.JSONDecodeError, OSError, ValueError):
                pass
    return reports


def load_report(report_id: str) -> dict:
    """Loads a single report by id."""
    path = _safe_path(report_id)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def delete_report(report_id: str) -> None:
    """Deletes a report by id."""
    path = _safe_path(report_id)
    if os.path.exists(path):
        os.remove(path)
