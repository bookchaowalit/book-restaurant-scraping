import asyncio
import sys
import tempfile
import unittest
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
