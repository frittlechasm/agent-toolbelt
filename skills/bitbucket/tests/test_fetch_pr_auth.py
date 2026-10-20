import base64
import contextlib
import importlib.util
import io
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "fetch_pr.py"
spec = importlib.util.spec_from_file_location("fetch_pr", SCRIPT_PATH)
fetch_pr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fetch_pr)


class FetchPrAuthTests(unittest.TestCase):
    def setUp(self):
        self.addCleanup(fetch_pr.CREDS.clear)
        fetch_pr.CREDS.clear()

    def test_api_token_file_builds_basic_auth_with_atlassian_email(self):
        with tempfile.TemporaryDirectory() as temporary:
            env_file = Path(temporary) / ".env"
            env_file.write_text(
                'BITBUCKET_EMAIL="reviewer@example.invalid"\n'
                "BITBUCKET_API_TOKEN='test-api-token'\n",
                encoding="utf-8",
            )
            fetch_pr.load_env_file(str(env_file))

        scheme, encoded = fetch_pr.auth_header().split(" ", 1)
        self.assertEqual(scheme, "Basic")
        self.assertEqual(base64.b64decode(encoded).decode(), "reviewer@example.invalid:test-api-token")

    def test_explicit_file_requires_both_api_token_credentials(self):
        invalid_contents = (
            "BITBUCKET_EMAIL=reviewer@example.invalid\n",
            "BITBUCKET_API_TOKEN=test-api-token\n",
            "BITBUCKET_USERNAME=old-user\nBITBUCKET_APP_PASSWORD=old-password\n",
        )
        with tempfile.TemporaryDirectory() as temporary:
            env_file = Path(temporary) / ".env"
            for contents in invalid_contents:
                with self.subTest(contents=contents):
                    env_file.write_text(contents, encoding="utf-8")
                    stderr = io.StringIO()
                    with contextlib.redirect_stderr(stderr), self.assertRaises(SystemExit):
                        fetch_pr.load_env_file(str(env_file))
                    self.assertIn("BITBUCKET_EMAIL", stderr.getvalue())
                    self.assertIn("BITBUCKET_API_TOKEN", stderr.getvalue())
                    self.assertEqual(fetch_pr.CREDS, {})

    def test_discovery_skips_legacy_file_and_uses_skill_api_token_file(self):
        with tempfile.TemporaryDirectory() as temporary:
            current_dir = Path(temporary) / "current"
            skill_dir = Path(temporary) / "skill"
            current_dir.mkdir()
            skill_dir.mkdir()
            (current_dir / ".env").write_text(
                "BITBUCKET_USERNAME=old-user\nBITBUCKET_APP_PASSWORD=old-password\n",
                encoding="utf-8",
            )
            (skill_dir / ".env").write_text(
                "BITBUCKET_EMAIL=reviewer@example.invalid\nBITBUCKET_API_TOKEN=test-api-token\n",
                encoding="utf-8",
            )
            with (
                mock.patch.object(fetch_pr.os, "getcwd", return_value=str(current_dir)),
                mock.patch.object(fetch_pr, "SKILL_DIR", str(skill_dir)),
                mock.patch.object(fetch_pr, "REAL_SKILL_DIR", str(skill_dir)),
            ):
                fetch_pr.load_env_file()

        self.assertEqual(fetch_pr.CREDS["BITBUCKET_EMAIL"], "reviewer@example.invalid")
        self.assertEqual(fetch_pr.CREDS["BITBUCKET_API_TOKEN"], "test-api-token")

    def test_ambient_credentials_are_not_used_without_an_env_file(self):
        with tempfile.TemporaryDirectory() as temporary:
            stderr = io.StringIO()
            with (
                mock.patch.dict(os.environ, {
                    "BITBUCKET_EMAIL": "reviewer@example.invalid",
                    "BITBUCKET_API_TOKEN": "test-api-token",
                }),
                mock.patch.object(fetch_pr.os, "getcwd", return_value=temporary),
                mock.patch.object(fetch_pr, "SKILL_DIR", temporary),
                mock.patch.object(fetch_pr, "REAL_SKILL_DIR", temporary),
                contextlib.redirect_stderr(stderr),
                self.assertRaises(SystemExit),
            ):
                fetch_pr.load_env_file()

        self.assertEqual(fetch_pr.CREDS, {})
        self.assertIn("BITBUCKET_EMAIL", stderr.getvalue())
        self.assertIn("BITBUCKET_API_TOKEN", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
