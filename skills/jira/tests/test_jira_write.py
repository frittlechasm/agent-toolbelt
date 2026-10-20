import contextlib
import copy
import importlib.machinery
import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "jira-write"
loader = importlib.machinery.SourceFileLoader("jira_write", str(SCRIPT))
spec = importlib.util.spec_from_loader(loader.name, loader)
write = importlib.util.module_from_spec(spec)
loader.exec_module(write)

API = "/rest/api/3"
ISSUE = API + "/issue/DEMO-1"
CONFIG = {"JIRA_SITE_URL": "https://example.atlassian.net", "JIRA_EMAIL": "me@example.com",
          "JIRA_API_TOKEN": "fixture-token"}
EDIT_META = {"fields": {"summary": {"operations": ["set"]}, "labels": {"operations": ["set"]}}}


class FakeJira:
    """Stands in for Client.request; values may be callables receiving the request body."""

    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    def __call__(self, method, path, *, body=None, query=None, **_):
        self.calls.append((method, path, body))
        value = self.responses[(method, path)]
        return value(body) if callable(value) else copy.deepcopy(value)

    def writes(self):
        return [call for call in self.calls if call[0] != "GET"]


class JiraWriteTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.directory = Path(directory.name)
        self.env_file = self.directory / "empty.env"
        self.env_file.write_text("")
        self.issue = {"key": "DEMO-1", "fields": {"updated": "T1", "summary": "Old", "labels": ["a"],
                                                  "assignee": None, "status": {"id": "1"}}}

    def file(self, name, value):
        path = self.directory / name
        path.write_text(value if isinstance(value, str) else json.dumps(value), encoding="utf-8")
        return str(path)

    def run_cli(self, argv, fake):
        out, err = io.StringIO(), io.StringIO()
        with (mock.patch.object(sys, "argv", ["jira-write", "--env-file", str(self.env_file), *argv]),
              mock.patch.dict(os.environ, CONFIG, clear=True),
              mock.patch.object(write.Client, "request", new=fake),
              contextlib.redirect_stdout(out), contextlib.redirect_stderr(err)):
            try:
                code = write.main()
            except SystemExit as exit_result:
                code = exit_result.code
        return code, out.getvalue(), err.getvalue()

    def edit_jira(self, apply_change=True):
        def put(body):
            if apply_change:
                self.issue["fields"].update(body["fields"])
                self.issue["fields"]["updated"] = "T2"
        return FakeJira({("GET", ISSUE): lambda _: copy.deepcopy(self.issue),
                         ("GET", ISSUE + "/editmeta"): EDIT_META, ("PUT", ISSUE): put})

    def test_help_exits_without_config_or_network(self):
        fake = FakeJira({})
        with (mock.patch.object(sys, "argv", ["jira-write", "--help"]), mock.patch.object(write.Client, "request", new=fake),
              contextlib.redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as exit_result):
            write.main()
        self.assertEqual(exit_result.exception.code, 0)
        self.assertEqual(fake.calls, [])

    def test_edit_preview_only_reads(self):
        fields = self.file("fields.json", {"summary": "New"})
        fake = self.edit_jira()
        code, out, _ = self.run_cli(["edit", "DEMO-1", "--fields-file", fields], fake)
        self.assertEqual(code, 0)
        preview = json.loads(out)
        self.assertEqual((preview["applied"], preview["expected_updated"]), (False, "T1"))
        self.assertEqual(preview["body"], {"fields": {"summary": "New"}})
        self.assertEqual(fake.writes(), [])

    def test_apply_without_or_with_stale_timestamp_does_not_write(self):
        fields = self.file("fields.json", {"summary": "New"})
        for extra in ([], ["--expected-updated", "T0"]):
            with self.subTest(extra=extra):
                fake = self.edit_jira()
                code, _, _ = self.run_cli(["edit", "DEMO-1", "--fields-file", fields, "--apply", *extra], fake)
                self.assertNotEqual(code, 0)
                self.assertEqual(fake.writes(), [])

    def test_change_after_preview_read_blocks_write(self):
        fields = self.file("fields.json", {"summary": "New"})
        versions = iter(["T1", "T2"])
        fake = self.edit_jira()
        fake.responses[("GET", ISSUE)] = lambda _: {**self.issue, "fields": {**self.issue["fields"], "updated": next(versions)}}
        code, _, err = self.run_cli(["edit", "DEMO-1", "--fields-file", fields, "--expected-updated", "T1", "--apply"], fake)
        self.assertEqual(code, 1)
        self.assertIn("stale", err)
        self.assertEqual(fake.writes(), [])

    def test_verified_edit_writes_once(self):
        fields = self.file("fields.json", {"summary": "New", "labels": ["b", "a"]})
        self.issue["fields"]["labels"] = ["a"]
        fake = self.edit_jira()
        fake.responses[("PUT", ISSUE)] = lambda body: self.issue["fields"].update(summary="New", labels=["a", "b"])
        code, out, _ = self.run_cli(["edit", "DEMO-1", "--fields-file", fields, "--expected-updated", "T1", "--apply"], fake)
        self.assertEqual(code, 0)
        result = json.loads(out)
        self.assertEqual((result["applied"], result["verified"]), (True, True))
        self.assertEqual(fake.writes(), [("PUT", ISSUE, {"fields": {"summary": "New", "labels": ["b", "a"]}})])

    def test_readback_mismatch_exits_3(self):
        fields = self.file("fields.json", {"summary": "New"})
        fake = self.edit_jira(apply_change=False)
        code, out, _ = self.run_cli(["edit", "DEMO-1", "--fields-file", fields, "--expected-updated", "T1", "--apply"], fake)
        self.assertEqual(code, 3)
        self.assertIn("warning", json.loads(out))
        self.assertEqual(len(fake.writes()), 1)

    def test_create_checks_required_fields_and_converts_plain_text(self):
        meta_path = API + "/issue/createmeta/DEMO/issuetypes/10001"
        meta = {"startAt": 0, "total": 3, "fields": [
            {"fieldId": "summary", "required": True, "operations": ["set"]},
            {"fieldId": "description", "required": False, "operations": ["set"]},
            {"fieldId": "customfield_1", "required": True, "hasDefaultValue": False, "operations": ["set"]}]}
        fake = FakeJira({("GET", meta_path): meta})
        args = ["create", "--project", "DEMO", "--issue-type", "10001", "--fields-file"]
        code, _, err = self.run_cli([*args, self.file("a.json", {"summary": "S"}), "--apply"], fake)
        self.assertEqual(code, 1)
        self.assertIn("customfield_1", err)
        self.assertEqual(fake.writes(), [])

        fields = self.file("b.json", {"summary": "S", "description": "One\n\nTwo", "customfield_1": "x"})
        code, out, _ = self.run_cli([*args, fields], fake)
        self.assertEqual(code, 0)
        body = json.loads(out)["body"]["fields"]
        self.assertEqual((body["project"], body["issuetype"]), ({"key": "DEMO"}, {"id": "10001"}))
        self.assertEqual([len(p["content"]) for p in body["description"]["content"]], [1, 0, 1])

    def test_create_meta_reads_every_page(self):
        meta_path = API + "/issue/createmeta/DEMO/issuetypes"
        pages = {0: {"total": 3, "issueTypes": [{"id": "1"}, {"id": "2"}]}, 2: {"total": 3, "issueTypes": [{"id": "3"}]}}
        fake = FakeJira({})
        with mock.patch.object(write.Client, "get", autospec=True,
                               side_effect=lambda _, path, **query: pages[query["startAt"]]):
            code, out, _ = self.run_cli(["create-meta", "DEMO"], fake)
        self.assertEqual(code, 0)
        self.assertEqual([item["id"] for item in json.loads(out)], ["1", "2", "3"])

    def test_comment_edit_checks_comment_timestamp_and_visibility(self):
        comment_path = ISSUE + "/comment/10042"
        body = self.file("comment.txt", "Fixed")
        for visibility_after, expected_code in (({"type": "role", "value": "Staff"}, 0), (None, 3)):
            with self.subTest(visibility_after=visibility_after):
                comment = {"id": "10042", "updated": "C1", "visibility": {"type": "role", "value": "Staff"},
                           "body": write.adf("Old")}

                def put(request_body, comment=comment, visibility_after=visibility_after):
                    comment.update(body=request_body["body"], visibility=visibility_after)
                fake = FakeJira({("GET", ISSUE): self.issue, ("GET", comment_path): lambda _, c=comment: copy.deepcopy(c),
                                 ("PUT", comment_path): put})
                argv = ["comment-edit", "DEMO-1", "--comment-id", "10042", "--body-file", body, "--apply"]
                code, _, _ = self.run_cli([*argv, "--expected-updated", "T1"], fake)
                self.assertEqual((code, fake.writes()), (1, []))
                code, out, _ = self.run_cli([*argv, "--expected-updated", "C1"], fake)
                self.assertEqual(code, expected_code)
                self.assertEqual(json.loads(out)["visibility_preserved"], expected_code == 0)
                self.assertEqual(fake.writes(), [("PUT", comment_path, {"body": write.adf("Fixed")})])

    def test_failed_write_is_not_retried_and_output_is_redacted(self):
        issue = json.dumps({"key": "DEMO-1", "fields": {"updated": "T1", "echo": "fixture-token"}}).encode()
        opener = mock.Mock()

        def open_request(request, timeout):
            if request.get_method() == "GET":
                return io.BytesIO(issue)
            raise urllib.error.HTTPError(request.full_url, 503, "Unavailable", {}, io.BytesIO(b"fixture-token"))
        opener.open.side_effect = open_request
        body = self.file("comment.txt", "Verified in staging\n")
        out, err = io.StringIO(), io.StringIO()
        with (mock.patch.dict(os.environ, CONFIG, clear=True),
              mock.patch("urllib.request.build_opener", return_value=opener),
              contextlib.redirect_stdout(out), contextlib.redirect_stderr(err)):
            codes = []
            for argv in (["get", "DEMO-1"], ["comment", "DEMO-1", "--body-file", body, "--apply"]):
                with mock.patch.object(sys, "argv", ["jira-write", "--env-file", str(self.env_file), *argv]):
                    codes.append(write.main())
        self.assertEqual(codes, [0, 1])
        self.assertIn("unknown", err.getvalue())
        self.assertNotIn("fixture-token", out.getvalue() + err.getvalue())
        self.assertIn("[REDACTED]", out.getvalue())
        posts = [call for call in opener.open.call_args_list if call.args[0].get_method() == "POST"]
        self.assertEqual(len(posts), 1)

    def test_settings_parse_file_without_executing_and_prefer_environment(self):
        marker = self.directory / "must-not-exist"
        path = self.file(".env", "export JIRA_SITE_URL='https://example.atlassian.net'\nJIRA_EMAIL=file@example.com\n"
                                 f"JIRA_API_TOKEN=$(touch {marker})\n# JIRA_CLOUD_ID=ignored\n")
        with mock.patch.dict(os.environ, {"JIRA_API_TOKEN": "env-token"}, clear=True):
            values = write.settings(path)
        self.assertEqual(values, {"JIRA_SITE_URL": "https://example.atlassian.net",
                                  "JIRA_EMAIL": "file@example.com", "JIRA_API_TOKEN": "env-token"})
        self.assertFalse(marker.exists())
        with mock.patch.dict(os.environ, {}, clear=True), self.assertRaises(write.JiraError):
            write.settings(self.file("partial.env", "JIRA_EMAIL=file@example.com\n"))

    def test_issue_urls_must_match_configured_site(self):
        site = "https://example.atlassian.net"
        self.assertEqual(write.issue_key(site + "/browse/demo-1", site), "DEMO-1")
        for value in ("https://other.atlassian.net/browse/DEMO-1", site + "/issues/DEMO-1", "DEMO-0"):
            with self.subTest(value=value), self.assertRaises(write.JiraError):
                write.issue_key(value, site)


if __name__ == "__main__":
    unittest.main()
