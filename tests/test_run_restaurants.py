import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from run_restaurants import JOBS


class RunRestaurantsTests(unittest.TestCase):
    def test_job_roster(self):
        self.assertEqual(
            [job["name"] for job in JOBS],
            ["wongnai_bangkok", "wongnai_upcountry"],
        )


if __name__ == "__main__":
    unittest.main()
