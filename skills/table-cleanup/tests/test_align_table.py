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

        output_lines = align_table_module.align_table(source, strip=True)
        output = "".join(output_lines)

        self.assertIn("Intro note\n", output)
        # Markdown is stripped from cells...
        self.assertNotIn("**", output)
        self.assertNotIn("https://", output)
        self.assertNotIn("[1]:", output)
        # ...but meaningful status emoji are preserved (they are the cell's value).
        self.assertIn("✅ Ready", output)
        self.assertIn("❌ Blocked", output)
        self.assertIn("runbook", output)
        self.assertIn("waiting on vendor", output)
        # Columns align: every rendered table row has identical width.
        table_widths = {
            align_table_module.display_width(line.rstrip("\n"))
            for line in output_lines
            if line.lstrip().startswith("|")
        }
        self.assertEqual(len(table_widths), 1)

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

    def test_short_separator_is_accepted(self):
        source = ["| A | B |\n", "|-|:-:|\n", "| 1 | 2 |\n"]

        output = align_table_module.align_table(source, strip=True)

        self.assertEqual(output[0], "| A | B |\n")
        self.assertEqual(output[1], "|---|---|\n")

    def test_optional_outer_pipes_preserve_all_cells(self):
        variants = [
            ["Name | Status\n", "--- | ---\n", "API | Ready\n"],
            ["| Name | Status\n", "| --- | ---\n", "| API | Ready\n"],
            ["Name | Status |\n", "--- | --- |\n", "API | Ready |\n"],
        ]

        for source in variants:
            with self.subTest(header=source[0].rstrip()):
                output = align_table_module.align_table(source, strip=True)

                self.assertEqual(output[0], "| Name | Status |\n")
                self.assertEqual(output[2], "| API  | Ready  |\n")

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

        self.assertIn("✅ Good", result.stdout)
        self.assertIn("Alpha", result.stdout)
        self.assertIn("1.2.0", result.stdout)
        self.assertNotIn("`", result.stdout)
        self.assertNotIn("**", result.stdout)

    def test_prose_with_pipe_is_not_treated_as_table(self):
        source = [
            "Choose red | blue before continuing.\n",
            "\n",
            "| Name | Status |\n",
            "|---|---|\n",
            "| API | Ready |\n",
        ]

        output = align_table_module.align_table(source, strip=True)

        self.assertEqual(output[0], source[0])
        self.assertEqual(output[2], "| Name | Status |\n")

    def test_cell_pipes_do_not_create_columns(self):
        source = [
            "| Pattern | Meaning |\n",
            "|---|---|\n",
            "| `grep a|b` | alternation |\n",
            "| a \\| b | literal pipe |\n",
        ]

        output = align_table_module.align_table(source, strip=True)

        self.assertIn(r"grep a\|b", output[2])
        self.assertIn(r"a \| b", output[3])
        self.assertEqual(output[2].count("|"), 4)

    def test_escaped_pipe_at_end_of_unclosed_row_is_preserved(self):
        source = [
            "Name | Value\n",
            "- | -\n",
            "Example | ends with \\|\n",
        ]

        output = align_table_module.align_table(source, strip=True)

        self.assertIn(r"ends with \|", output[2])

    def test_tables_are_aligned_independently(self):
        source = [
            "| A | B |\n",
            "|---|---|\n",
            "| 1 | 2 |\n",
            "\n",
            "| Longer heading | Value |\n",
            "|---|---|\n",
            "| x | y |\n",
        ]

        output = align_table_module.align_table(source, strip=True)

        self.assertLess(len(output[0]), len(output[4]))

    def test_adjacent_tables_are_aligned_independently(self):
        source = [
            "| A | B |\n",
            "|-|-|\n",
            "| 1 | 2 |\n",
            "| Longer heading | Value |\n",
            "|-|-|\n",
            "| x | y |\n",
        ]

        output = align_table_module.align_table(source, strip=True)

        self.assertLess(len(output[0]), len(output[3]))

    def test_wide_characters_use_display_width(self):
        source = [
            "| Team | Status |\n",
            "|---|---|\n",
            "| API | ✅ Ready |\n",
            "| 数据 | Blocked |\n",
        ]

        output = align_table_module.align_table(source, strip=True)
        widths = {align_table_module.display_width(line.rstrip("\n")) for line in output}

        self.assertEqual(len(widths), 1)


if __name__ == "__main__":
    unittest.main()
