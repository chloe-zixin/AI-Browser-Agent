import unittest

from app.crawler.quotes_spider import deduplicate_quotes


class DeduplicateQuotesTests(unittest.TestCase):
    def test_deduplicates_case_and_whitespace_variants(self):
        quotes = [
            {"quote": "Same text", "author": "Ada"},
            {"quote": " Same   text ", "author": "ADA"},
            {"quote": "Same text", "author": "Grace"},
            {"quote": "  ", "author": "Unknown"},
        ]

        unique_quotes = deduplicate_quotes(quotes)

        self.assertEqual(unique_quotes, [quotes[0], quotes[2]])


if __name__ == "__main__":
    unittest.main()