import unittest
from unittest.mock import patch

from app.api.server import execute_pipeline_task


class ExecutePipelineTaskTests(unittest.TestCase):
    @patch("app.api.server.task_manager")
    @patch(
        "app.api.server.crawl_quotes",
        return_value=[
            {
                "quote": "Hope shapes the future.",
                "author": "Ada Lovelace",
                "tags": ["hope"],
                "page": 1,
                "record_id": "record-1",
                "source_id": "quotes.toscrape.com",
                "source_url": "https://quotes.toscrape.com/page/1/",
                "captured_at": "2026-10-12T07:00:00Z",
            }
        ],
    )
    def test_crawls_enriches_and_persists_quotes(self, crawl_quotes, task_manager):
        execute_pipeline_task("task-test", pages=1, mode="local")

        crawl_quotes.assert_called_once_with(pages=1, headless=True)
        task_manager.mark_running.assert_called_once_with("task-test")
        task_manager.mark_success.assert_called_once()
        quotes = task_manager.mark_success.call_args.kwargs["quotes"]
        report = task_manager.mark_success.call_args.kwargs["report"]
        self.assertEqual(quotes[0]["text"], "Hope shapes the future.")
        self.assertEqual(quotes[0]["analysis_method"], "local_keyword_rules")
        self.assertEqual(quotes[0]["record_id"], "record-1")
        self.assertEqual(quotes[0]["source_id"], "quotes.toscrape.com")
        self.assertEqual(quotes[0]["source_url"], "https://quotes.toscrape.com/page/1/")
        self.assertEqual(quotes[0]["captured_at"], "2026-10-12T07:00:00Z")
        self.assertEqual(report["quote_count"], 1)
        self.assertEqual(report["analysis_method"], "local_keyword_rules")
        self.assertEqual(report["provenance_version"], 1)
        task_manager.mark_failed.assert_not_called()

    @patch("app.api.server.task_manager")
    @patch("app.api.server.crawl_quotes", return_value=[])
    def test_empty_crawl_marks_task_failed(self, crawl_quotes, task_manager):
        execute_pipeline_task("task-empty", pages=1, mode="local")

        crawl_quotes.assert_called_once_with(pages=1, headless=True)
        task_manager.mark_running.assert_called_once_with("task-empty")
        task_manager.mark_success.assert_not_called()
        task_manager.mark_failed.assert_called_once()
        self.assertIn("no quotes", task_manager.mark_failed.call_args.kwargs["error"])

    @patch("app.api.server.task_manager")
    @patch(
        "app.api.server.crawl_quotes",
        return_value=[
            {
                "quote": "Same text",
                "author": "Ada",
                "tags": [],
                "page": 1,
                "record_id": "record-1",
                "source_id": "quotes.toscrape.com",
                "source_url": "https://quotes.toscrape.com/page/1/",
                "captured_at": "2026-10-12T07:00:00Z",
            },
            {
                "quote": " Same   text ",
                "author": "ADA",
                "tags": [],
                "page": 2,
                "record_id": "record-2",
                "source_id": "quotes.toscrape.com",
                "source_url": "https://quotes.toscrape.com/page/2/",
                "captured_at": "2026-10-12T07:00:00Z",
            },
        ],
    )
    def test_duplicate_quotes_are_counted_and_saved_once(self, crawl_quotes, task_manager):
        execute_pipeline_task("task-duplicates", pages=2, mode="local")

        crawl_quotes.assert_called_once_with(pages=2, headless=True)
        saved_quotes = task_manager.mark_success.call_args.kwargs["quotes"]
        saved_report = task_manager.mark_success.call_args.kwargs["report"]
        self.assertEqual(len(saved_quotes), 1)
        self.assertEqual(saved_report["duplicate_count"], 1)

    @patch("app.api.server.task_manager")
    @patch(
        "app.api.server.crawl_quotes",
        return_value=[{"quote": "Missing provenance", "author": "Unknown", "tags": [], "page": 1}],
    )
    def test_missing_provenance_marks_task_failed(self, crawl_quotes, task_manager):
        execute_pipeline_task("task-provenance", pages=1, mode="local")

        crawl_quotes.assert_called_once_with(pages=1, headless=True)
        task_manager.mark_success.assert_not_called()
        self.assertIn(
            "missing valid source provenance",
            task_manager.mark_failed.call_args.kwargs["error"],
        )


if __name__ == "__main__":
    unittest.main()