import tempfile
import unittest
from pathlib import Path

from app.task.task_manager import TaskManager, safe_write_json


class TaskProvenanceTests(unittest.TestCase):
    def test_mark_success_persists_analysis_method(self):
        project_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(dir=project_root) as temp_dir:
            manager = TaskManager(Path(temp_dir))
            task = manager.create_task(pages=1, mode="local")
            manager.mark_running(task["task_id"])

            manager.mark_success(
                task["task_id"],
                quotes=[{"text": "Example", "author": "Author", "tags": []}],
                report={
                    "summary": "Analyzed one quote.",
                    "analysis_method": "local_keyword_rules",
                    "provenance_version": 1,
                },
            )

            persisted_task = manager.get_task(task["task_id"])
            if persisted_task is None:
                self.fail("Created task could not be reloaded.")
            self.assertEqual(persisted_task["analysis_method"], "local_keyword_rules")
            self.assertEqual(persisted_task["provenance_version"], 1)

            full_task = manager.get_task(task["task_id"], include_quotes=True)
            if full_task is None:
                self.fail("Created task with quotes could not be reloaded.")
            self.assertEqual(full_task["quotes"], [{"text": "Example", "author": "Author", "tags": []}])

    def test_list_tasks_reads_provenance_from_existing_report(self):
        project_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(dir=project_root) as temp_dir:
            manager = TaskManager(Path(temp_dir))
            task = manager.create_task(pages=1, mode="local")
            safe_write_json(
                manager._report_file(task["task_id"]),
                {"analysis_method": "local_keyword_rules"},
            )

            listed_task = manager.list_tasks()[0]
            stored_task = manager._task_file(task["task_id"]).read_text(encoding="utf-8")

            self.assertEqual(listed_task["analysis_method"], "local_keyword_rules")
            self.assertNotIn("analysis_method", stored_task)

    def test_metrics_exclude_tasks_without_provenance_version(self):
        project_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(dir=project_root) as temp_dir:
            manager = TaskManager(Path(temp_dir))
            legacy = manager.create_task(pages=1, mode="local")
            manager.update_task(
                legacy["task_id"],
                {"status": "success", "quote_count": 500},
            )

            verified = manager.create_task(pages=1, mode="local")
            manager.mark_running(verified["task_id"])
            manager.mark_success(
                verified["task_id"],
                quotes=[{"text": "Example", "author": "Author", "tags": []}],
                report={
                    "summary": "Analyzed one quote.",
                    "analysis_method": "local_keyword_rules",
                    "provenance_version": 1,
                },
            )

            failed = manager.create_task(pages=1, mode="local")
            manager.update_task(
                failed["task_id"],
                {"provenance_version": 1, "source_id": "quotes.toscrape.com"},
            )
            manager.mark_running(failed["task_id"])
            manager.mark_failed(failed["task_id"], "ConnectionError: source unavailable")

            metrics = manager.get_metrics_summary()

            self.assertEqual(metrics["total_tasks"], 2)
            self.assertEqual(metrics["unverified_tasks"], 1)
            self.assertEqual(metrics["success_tasks"], 1)
            self.assertEqual(metrics["failed_tasks"], 1)
            self.assertEqual(metrics["total_quotes"], 1)


if __name__ == "__main__":
    unittest.main()