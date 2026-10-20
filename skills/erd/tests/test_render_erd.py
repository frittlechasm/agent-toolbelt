import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPT_PATH = SKILL_DIR / "scripts" / "render_erd.py"

spec = importlib.util.spec_from_file_location("render_erd", SCRIPT_PATH)
render_erd = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(render_erd)


def valid_model():
    return {
        "title": "Orders",
        "groups": [{"id": "core", "label": "Core"}],
        "tables": [
            {
                "id": "orders",
                "name": "orders",
                "group": "core",
                "columns": [
                    {"name": "tenant_id", "type": "uuid", "primaryKey": True},
                    {"name": "id", "type": "uuid", "primaryKey": True},
                ],
                "constraints": [
                    {
                        "kind": "primary-key",
                        "columns": ["tenant_id", "id"],
                        "text": "PRIMARY KEY (tenant_id, id)",
                    }
                ],
            },
            {
                "id": "items",
                "name": "order_items",
                "group": "core",
                "columns": [
                    {"name": "tenant_id", "type": "uuid", "nullable": False},
                    {"name": "order_id", "type": "uuid", "nullable": False},
                    {"name": "line_no", "type": "integer", "nullable": False},
                ],
            },
        ],
        "relationships": [
            {
                "id": "items_order",
                "from": {
                    "table": "items",
                    "columns": ["tenant_id", "order_id"],
                    "cardinality": "0..*",
                },
                "to": {
                    "table": "orders",
                    "columns": ["tenant_id", "id"],
                    "cardinality": "1",
                },
                "enforcement": "foreign-key",
                "onDelete": "CASCADE",
            }
        ],
    }


class RenderErdTests(unittest.TestCase):
    def test_validates_and_normalizes_primary_key_columns(self):
        model = render_erd.validate_model(valid_model())

        self.assertFalse(model["tables"][0]["columns"][0]["nullable"])
        self.assertFalse(model["tables"][0]["existing"])
        self.assertEqual(len(model["relationships"]), 1)

    def test_rejects_mismatched_composite_relationship(self):
        model = valid_model()
        model["relationships"][0]["to"]["columns"] = ["id"]

        with self.assertRaisesRegex(
            render_erd.ModelError, "must have equal length"
        ):
            render_erd.validate_model(model)

    def test_rejects_unknown_relationship_column(self):
        model = valid_model()
        model["relationships"][0]["from"]["columns"][1] = "missing"

        with self.assertRaisesRegex(
            render_erd.ModelError, "unknown column items.missing"
        ):
            render_erd.validate_model(model)

    def test_rejects_referential_actions_on_logical_relationship(self):
        model = valid_model()
        model["relationships"][0]["enforcement"] = "logical"

        with self.assertRaisesRegex(
            render_erd.ModelError, "valid only for foreign-key"
        ):
            render_erd.validate_model(model)

    def test_rejects_foreign_key_target_without_candidate_key(self):
        model = valid_model()
        model["tables"][0]["columns"][0]["primaryKey"] = False
        model["tables"][0]["columns"][1]["primaryKey"] = False
        model["tables"][0]["constraints"] = []

        with self.assertRaisesRegex(
            render_erd.ModelError, "must match a declared primary or unique key"
        ):
            render_erd.validate_model(model)

    def test_renderer_escapes_script_closing_text(self):
        model = valid_model()
        model["subtitle"] = "Unsafe </script><script>alert(1)</script>"

        html = render_erd.render(render_erd.validate_model(model))

        self.assertNotIn("Unsafe </script>", html)
        self.assertIn(r"Unsafe \u003c/script\u003e", html)
        self.assertNotIn(render_erd.PLACEHOLDER, html)
        self.assertNotIn("https://", html)

    def test_cli_renders_and_refuses_unrequested_overwrite(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "schema.json"
            output = root / "erd.html"
            source.write_text(json.dumps(valid_model()), encoding="utf-8")

            first = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), str(source), "--output", str(output)],
                check=False,
                capture_output=True,
                text=True,
            )
            second = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), str(source), "--output", str(output)],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertTrue(output.is_file())
            self.assertEqual(second.returncode, 2)
            self.assertIn("output already exists", second.stderr)


if __name__ == "__main__":
    unittest.main()
