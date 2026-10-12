from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
TASKS_DIR = DATA_DIR / "tasks"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def safe_read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def safe_write_json(path: Path, data: Any) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@dataclass
class TaskCreatePayload:
    pages: int = 3
    mode: str = "llm"


class TaskManager:
    """
    A lightweight file-based task manager for the AI Browser Agent project.

    Directory layout:
    data/
      tasks/
        <task_id>/
          task.json
          quotes_all.json
          report.json
          meta.json
    """

    def __init__(self, tasks_dir: Path = TASKS_DIR) -> None:
        self.tasks_dir = tasks_dir
        ensure_dir(self.tasks_dir)

    def _task_dir(self, task_id: str) -> Path:
        return self.tasks_dir / task_id

    def _task_file(self, task_id: str) -> Path:
        return self._task_dir(task_id) / "task.json"

    def _quotes_file(self, task_id: str) -> Path:
        return self._task_dir(task_id) / "quotes_all.json"

    def _report_file(self, task_id: str) -> Path:
        return self._task_dir(task_id) / "report.json"

    def _meta_file(self, task_id: str) -> Path:
        return self._task_dir(task_id) / "meta.json"

    def _build_task_id(self) -> str:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        short = uuid.uuid4().hex[:8]
        return f"task_{ts}_{short}"

    def create_task(self, pages: int = 3, mode: str = "llm") -> Dict[str, Any]:
        task_id = self._build_task_id()
        task_dir = self._task_dir(task_id)
        ensure_dir(task_dir)

        task = {
            "task_id": task_id,
            "status": "pending",
            "pages": int(pages),
            "mode": mode,
            "created_at": utc_now_iso(),
            "updated_at": utc_now_iso(),
            "started_at": None,
            "finished_at": None,
            "duration_seconds": None,
            "quote_count": 0,
            "unique_authors": 0,
            "total_tags": 0,
            "top_authors": [],
            "top_tags": [],
            "error": None,
            "summary": "",
            "quotes_path": str(self._quotes_file(task_id).relative_to(BASE_DIR)),
            "report_path": str(self._report_file(task_id).relative_to(BASE_DIR)),
            "meta_path": str(self._meta_file(task_id).relative_to(BASE_DIR)),
        }
        safe_write_json(self._task_file(task_id), task)

        meta = {
            "task_id": task_id,
            "pages": int(pages),
            "mode": mode,
            "created_at": task["created_at"],
        }
        safe_write_json(self._meta_file(task_id), meta)
        return task

    def get_task(self, task_id: str, include_quotes: bool = False) -> Optional[Dict[str, Any]]:
        task = safe_read_json(self._task_file(task_id))
        if not task:
            return None

        quotes = safe_read_json(self._quotes_file(task_id), default=[])
        report = safe_read_json(self._report_file(task_id), default={})
        meta = safe_read_json(self._meta_file(task_id), default={})

        task["quotes_preview"] = quotes[:10] if isinstance(quotes, list) else []
        if include_quotes:
            task["quotes"] = quotes if isinstance(quotes, list) else []
        task["quotes_count_from_file"] = len(quotes) if isinstance(quotes, list) else 0
        task["report"] = report if isinstance(report, dict) else {}
        task["meta"] = meta if isinstance(meta, dict) else {}

        return task

    def list_tasks(self) -> List[Dict[str, Any]]:
        tasks: List[Dict[str, Any]] = []
        if not self.tasks_dir.exists():
            return tasks

        for item in self.tasks_dir.iterdir():
            if not item.is_dir():
                continue
            task_file = item / "task.json"
            task = safe_read_json(task_file)
            if task:
                report = safe_read_json(item / "report.json", default={})
                if isinstance(report, dict):
                    for key in ("analysis_method", "provenance_version"):
                        if not task.get(key) and report.get(key):
                            task[key] = report[key]
                tasks.append(task)

        def sort_key(x: Dict[str, Any]) -> str:
            return x.get("created_at") or ""

        tasks.sort(key=sort_key, reverse=True)
        return tasks

    def update_task(self, task_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        task = safe_read_json(self._task_file(task_id))
        if not task:
            return None

        task.update(updates)
        task["updated_at"] = utc_now_iso()
        safe_write_json(self._task_file(task_id), task)
        return task

    def mark_running(self, task_id: str) -> Optional[Dict[str, Any]]:
        now = utc_now_iso()
        return self.update_task(
            task_id,
            {
                "status": "running",
                "started_at": now,
                "updated_at": now,
                "error": None,
            },
        )

    def mark_failed(self, task_id: str, error: str) -> Optional[Dict[str, Any]]:
        task = safe_read_json(self._task_file(task_id))
        if not task:
            return None

        finished_at = utc_now_iso()
        duration_seconds = self._compute_duration_seconds(task.get("started_at"), finished_at)

        return self.update_task(
            task_id,
            {
                "status": "failed",
                "finished_at": finished_at,
                "duration_seconds": duration_seconds,
                "error": error,
                "summary": "Task failed during crawling / enrichment pipeline.",
            },
        )

    def mark_success(
        self,
        task_id: str,
        quotes: List[Dict[str, Any]],
        report: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        task = safe_read_json(self._task_file(task_id))
        if not task:
            return None

        safe_write_json(self._quotes_file(task_id), quotes)
        safe_write_json(self._report_file(task_id), report)

        finished_at = utc_now_iso()
        duration_seconds = self._compute_duration_seconds(task.get("started_at"), finished_at)

        quote_count = len(quotes)
        authors = [q.get("author", "Unknown") for q in quotes if isinstance(q, dict)]
        unique_authors = len(set(authors))
        total_tags = sum(len(q.get("tags", [])) for q in quotes if isinstance(q, dict))

        top_authors = self._top_k(authors, k=5)
        all_tags: List[str] = []
        for q in quotes:
            if isinstance(q, dict):
                tags = q.get("tags", [])
                if isinstance(tags, list):
                    all_tags.extend([str(t) for t in tags])

        top_tags = self._top_k(all_tags, k=8)

        summary = report.get("summary") or f"Successfully processed {quote_count} quotes."
        updates = {
            "status": "success",
            "finished_at": finished_at,
            "duration_seconds": duration_seconds,
            "quote_count": quote_count,
            "unique_authors": unique_authors,
            "total_tags": total_tags,
            "top_authors": top_authors,
            "top_tags": top_tags,
            "summary": summary,
            "error": None,
        }
        if report.get("analysis_method"):
            updates["analysis_method"] = report["analysis_method"]
        if report.get("provenance_version"):
            updates["provenance_version"] = report["provenance_version"]

        return self.update_task(task_id, updates)

    def get_metrics_summary(self) -> Dict[str, Any]:
        tasks = self.list_tasks()
        verified_tasks = [t for t in tasks if t.get("provenance_version") == 1]
        total_tasks = len(verified_tasks)
        unverified_tasks = len(tasks) - total_tasks
        success_tasks = sum(1 for t in verified_tasks if t.get("status") == "success")
        failed_tasks = sum(1 for t in verified_tasks if t.get("status") == "failed")
        running_tasks = sum(1 for t in verified_tasks if t.get("status") == "running")
        pending_tasks = sum(1 for t in verified_tasks if t.get("status") == "pending")

        total_quotes = sum(int(t.get("quote_count") or 0) for t in verified_tasks)
        avg_quotes_per_task = round(total_quotes / total_tasks, 2) if total_tasks else 0.0
        success_rate = round((success_tasks / total_tasks) * 100, 2) if total_tasks else 0.0

        latest_task = verified_tasks[0] if verified_tasks else None

        return {
            "total_tasks": total_tasks,
            "unverified_tasks": unverified_tasks,
            "success_tasks": success_tasks,
            "failed_tasks": failed_tasks,
            "running_tasks": running_tasks,
            "pending_tasks": pending_tasks,
            "success_rate": success_rate,
            "total_quotes": total_quotes,
            "avg_quotes_per_task": avg_quotes_per_task,
            "latest_task_id": latest_task.get("task_id") if latest_task else None,
            "latest_status": latest_task.get("status") if latest_task else None,
            "latest_created_at": latest_task.get("created_at") if latest_task else None,
        }

    def _compute_duration_seconds(self, started_at: Optional[str], finished_at: Optional[str]) -> Optional[float]:
        if not started_at or not finished_at:
            return None
        try:
            start = datetime.fromisoformat(started_at.replace("Z", ""))
            end = datetime.fromisoformat(finished_at.replace("Z", ""))
            return round((end - start).total_seconds(), 2)
        except Exception:
            return None

    def _top_k(self, items: List[str], k: int = 5) -> List[Dict[str, Any]]:
        counter: Dict[str, int] = {}
        for item in items:
            key = str(item).strip()
            if not key:
                continue
            counter[key] = counter.get(key, 0) + 1

        ranked = sorted(counter.items(), key=lambda x: (-x[1], x[0]))
        return [{"name": name, "count": count} for name, count in ranked[:k]]


task_manager = TaskManager()