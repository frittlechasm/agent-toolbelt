import importlib.util
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "fetch_pr.py"
spec = importlib.util.spec_from_file_location("fetch_pr", SCRIPT_PATH)
fetch_pr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fetch_pr)


class NormalizeCommentsTests(unittest.TestCase):
    def test_resolved_reflects_presence_of_resolution_even_when_empty(self):
        comments = fetch_pr.normalize_comments([
            {"id": 1, "resolution": {}},
            {"id": 2, "resolution": {"type": "comment_resolution"}},
            {"id": 3, "resolution": None},
            {"id": 4},
        ])

        self.assertEqual([comment["resolved"] for comment in comments], [True, True, False, False])
        self.assertEqual(comments[0]["resolution"], {})


if __name__ == "__main__":
    unittest.main()
