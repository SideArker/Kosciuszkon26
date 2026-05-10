import json
import os
from datetime import datetime

REPORTS_DIR = os.path.join("data", "reports")


def _ensure_dir() -> None:
    os.makedirs(REPORTS_DIR, exist_ok=True)


def save_report(payload: dict) -> str:
    """Persist analysis metadata to a JSON file. Returns the report_id (filename stem)."""
    _ensure_dir()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = os.path.basename(payload.get("analyzed_file", "unknown"))
    safe_name = "".join(c if c.isalnum() or c in "._-" else "_" for c in safe_name)
    report_id = f"{ts}_{safe_name}"
    record = {**payload, "id": report_id}
    path = os.path.join(REPORTS_DIR, f"{report_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)
    return report_id


def load_all_reports() -> list[dict]:
    """Return all saved reports sorted newest-first."""
    _ensure_dir()
    reports = []
    for fname in sorted(os.listdir(REPORTS_DIR), reverse=True):
        if fname.endswith(".json"):
            try:
                with open(os.path.join(REPORTS_DIR, fname), "r", encoding="utf-8") as f:
                    reports.append(json.load(f))
            except (json.JSONDecodeError, OSError):
                pass
    return reports


def load_report(report_id: str) -> dict:
    """Load a single report by its ID."""
    path = os.path.join(REPORTS_DIR, f"{report_id}.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def delete_report(report_id: str) -> None:
    """Delete a saved report file."""
    path = os.path.join(REPORTS_DIR, f"{report_id}.json")
    if os.path.exists(path):
        os.remove(path)
