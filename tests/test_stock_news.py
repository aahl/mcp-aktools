import unittest
from unittest.mock import patch

import mcp_aktools


class StockNewsFailureTest(unittest.TestCase):
    @patch("mcp_aktools.ak_cache", return_value=None)
    def test_reports_unavailable_when_source_fetch_fails(self, _mock_cache):
        self.assertEqual(
            mcp_aktools.stock_news("SYNTHETIC"),
            "News unavailable for SYNTHETIC",
        )


if __name__ == "__main__":
    unittest.main()
