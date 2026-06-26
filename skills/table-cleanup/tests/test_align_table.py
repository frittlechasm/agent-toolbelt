import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPT_PATH = SKILL_DIR / "scripts" / "align_table.py"

spec = importlib.util.spec_from_file_location("align_table", SCRIPT_PATH)
align_table_module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(align_table_module)


class AlignTableTests(unittest.TestCase):
    def test_strip_cleans_markdown_artifacts_and_reference_definitions(self):
        source = [
            "Intro **note**\n",
            "\n",
            "| Team | Status | Notes |\n",
            "|---|---|---|\n",
            "| **Platform** | ✅ Ready | [runbook](https://example.com) ([source][1]) |\n",
            "| *Data* | ❌ Blocked | waiting on vendor |\n",
            "\n",
            "[1]: https://example.com/source\n",
        ]

        output = "".join(align_table_module.align_table(source, strip=True))

        self.assertIn("Intro note\n", output)
        self.assertIn("| Platform | Ready   | runbook           |", output)
        self.assertIn("| Data     | Blocked | waiting on vendor |", output)
        self.assertNotIn("**", output)
        self.assertNotIn("https://", output)
        self.assertNotIn("✅", output)
        self.assertNotIn("❌", output)
        self.assertNotIn("[1]:", output)

    def test_separator_is_rebuilt_without_alignment_markers(self):
        source = [
            "| Owner | Q1 | Q2 |\n",
            "|:---|---:|:---:|\n",
            "| Ada | 10 | complete |\n",
            "| Linus | 200 | blocked |\n",
        ]

        output = align_table_module.align_table(source, strip=True)

        self.assertEqual(output[1], "|-------|-----|----------|\n")
        self.assertNotIn(":", output[1])

    def test_stdout_mode_does_not_mutate_input_file(self):
        original = "| Name | Status | Version |\n|---|---|---|\n| **Alpha** | ✅ Good | `1.2.0` |\n"

        with tempfile.NamedTemporaryFile("w+", encoding="utf-8") as temp_file:
            temp_file.write(original)
            temp_file.flush()

            result = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), "--strip", temp_file.name],
                check=True,
                capture_output=True,
                text=True,
            )

            temp_file.seek(0)
            self.assertEqual(temp_file.read(), original)

        self.assertIn("| Alpha | Good   | 1.2.0   |", result.stdout)
        self.assertNotIn("`", result.stdout)


if __name__ == "__main__":
    unittest.main()
