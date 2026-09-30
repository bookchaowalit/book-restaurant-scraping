import asyncio
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from run_restaurants import JOBS, run_restaurants


class RunRestaurantsTests(unittest.TestCase):
    def test_job_roster(self):
        self.assertEqual(
            [job["name"] for job in JOBS],
            ["wongnai_bangkok", "wongnai_upcountry"],
        )

    def test_dry_run_does_not_collect(self):
        with tempfile.TemporaryDirectory() as directory:
            result = asyncio.run(run_restaurants(Path(directory), dry_run=True))
        self.assertEqual([item["status"] for item in result], ["dry-run", "dry-run"])
        self.assertTrue(all(item["network"] == "not-used" for item in result))

    def test_failing_job_does_not_block_the_next_one(self):
        calls = []

        async def fake_run(self, max_pages=3, **_kwargs):
            calls.append(self.output_stem)
            if self.output_stem == "wongnai_bangkok":
                raise RuntimeError("page content must not leak")
            return [{"source": self.output_stem, "count": 7}]

        with tempfile.TemporaryDirectory() as directory:
            with patch("restaurants.wongnai_scraper.WongnaiScraper.run", fake_run):
                result = asyncio.run(run_restaurants(Path(directory)))
        self.assertEqual(calls, ["wongnai_bangkok", "wongnai_upcountry"])
        self.assertEqual(result[0], {"job": "wongnai_bangkok", "error": "RuntimeError"})
        self.assertEqual(result[1]["count"], 7)


if __name__ == "__main__":
    unittest.main()
