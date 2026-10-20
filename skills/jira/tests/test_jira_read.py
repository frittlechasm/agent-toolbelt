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


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "jira-read"
loader = importlib.machinery.SourceFileLoader("jira_read", str(SCRIPT))
spec = importlib.util.spec_from_loader(loader.name, loader)
read = importlib.util.module_from_spec(spec)
loader.exec_module(read)

API = "/rest/api/3"
SEARCH = API + "/search/jql"
PARSE = API + "/jql/parse"
ISSUE = API + "/issue/DEMO-1"
CONFIG = {"JIRA_SITE_URL": "https://example.atlassian.net", "JIRA_EMAIL": "me@example.com",
          "JIRA_API_TOKEN": "fixture-token"}


def issues(*ids):
    return [{"id": str(i), "key": f"DEMO-{i}", "fields": {}} for i in ids]


class FakeJira:
    """Stands in for Client.request; values may be callables receiving the request body and query.

    JQL validation passes unless a test overrides it.
    """

    def __init__(self, responses):
        self.responses = {("POST", PARSE): {"queries": [{}]}, **responses}
        self.calls = []

    def __call__(self, method, path, *, body=None, query=None):
        self.calls.append((method, path, body, query))
        value = self.responses[(method, path)]
        return value(body, query) if callable(value) else copy.deepcopy(value)


class JiraReadTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.env_file = Path(directory.name) / "empty.env"
        self.env_file.write_text("")

    def run_cli(self, argv, fake):
        out, err = io.StringIO(), io.StringIO()
        with (mock.patch.object(sys, "argv", ["jira-read", "--env-file", str(self.env_file), *argv]),
              mock.patch.dict(os.environ, CONFIG, clear=True),
              mock.patch.object(read.Client, "request", new=fake),
              contextlib.redirect_stdout(out), contextlib.redirect_stderr(err)):
            try:
                code = read.main()
            except SystemExit as exit_result:
                code = exit_result.code
        return code, out.getvalue(), err.getvalue()

    def test_help_exits_without_config_or_network(self):
        fake = FakeJira({})
        with (mock.patch.object(sys, "argv", ["jira-read", "--help"]), mock.patch.object(read.Client, "request", new=fake),
              contextlib.redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as exit_result):
            read.main()
        self.assertEqual(exit_result.exception.code, 0)
        self.assertEqual(fake.calls, [])

    def test_search_stops_at_limit_with_resume_token_and_keeps_warnings(self):
        pages = {None: {"issues": issues(1, 2), "nextPageToken": "t1", "warnings": [{"type": "TRUNCATED"}]},
                 "t1": {"issues": issues(3), "nextPageToken": "t2", "isLast": False}}
        fake = FakeJira({("POST", SEARCH): lambda body, _: pages[body.get("nextPageToken")]})
        code, out, _ = self.run_cli(["search", "--jql", "project = DEMO", "--limit", "3"], fake)
        self.assertEqual(code, 0)
        result = json.loads(out)
        self.assertEqual([i["key"] for i in result["issues"]], ["DEMO-1", "DEMO-2", "DEMO-3"])
        self.assertEqual((result["complete"], result["next_page_token"]), (False, "t2"))
        self.assertEqual(result["warnings"], [{"type": "TRUNCATED"}])
        self.assertEqual(result["issues"][0]["url"], "https://example.atlassian.net/browse/DEMO-1")
        self.assertEqual([call[2]["maxResults"] for call in fake.calls if call[1] == SEARCH], [3, 1])

    def test_search_completion_follows_the_page_token_not_is_last(self):
        # isLast has been reported missing or wrong; only the token decides whether more pages exist.
        pages = {None: {"issues": issues(1), "nextPageToken": "t1", "isLast": True}, "t1": {"issues": issues(2)}}
        fake = FakeJira({("POST", SEARCH): lambda body, _: pages[body.get("nextPageToken")]})
        code, out, _ = self.run_cli(["search", "--jql", "project = DEMO"], fake)
        self.assertEqual(code, 0)
        result = json.loads(out)
        self.assertEqual([i["key"] for i in result["issues"]], ["DEMO-1", "DEMO-2"])
        self.assertEqual((result["complete"], result["next_page_token"]), (True, None))

    def test_search_rejects_repeated_issues(self):
        for name, response in (("across pages", lambda body, _: {"issues": issues(1), "nextPageToken": "again"}),
                               ("within a page", {"issues": issues(1, 1)})):
            with self.subTest(name):
                code, out, err = self.run_cli(["search", "--jql", "project = DEMO"], FakeJira({("POST", SEARCH): response}))
                self.assertEqual((code, out), (1, ""))
                self.assertIn("repeated", err)

    def test_invalid_jql_fails_instead_of_returning_nothing(self):
        # Jira answers an unknown field, value, or project with an empty result, not an error.
        invalid = {"queries": [{"errors": ["Field 'sprintt' does not exist or you do not have permission to view it."]}]}
        for command in ("search", "count"):
            with self.subTest(command=command):
                fake = FakeJira({("POST", PARSE): invalid})
                code, out, err = self.run_cli([command, "--jql", "project = DEMO AND sprintt = 1"], fake)
                self.assertEqual((code, out), (1, ""))
                self.assertIn("Field 'sprintt' does not exist", err)
                self.assertEqual([call[1] for call in fake.calls], [PARSE])

    def test_get_reads_comment_collection_and_reports_where_to_resume(self):
        comments = [{"id": str(i)} for i in range(3)]

        def comment_page(_, query):
            start = query["startAt"]
            return {"comments": comments[start:start + query["maxResults"]], "total": len(comments)}
        fake = FakeJira({("GET", ISSUE): {"key": "DEMO-1", "fields": {}}, ("GET", ISSUE + "/comment"): comment_page})
        code, out, _ = self.run_cli(["get", "demo-1", "--comments", "--limit", "2"], fake)
        self.assertEqual(code, 0)
        result = json.loads(out)["comments"]
        self.assertEqual((len(result["items"]), result["complete"], result["next_start"]), (2, False, 2))
        self.assertEqual(fake.calls[0][3], {"fields": "*all,-comment"})

        code, out, _ = self.run_cli(["comments", "DEMO-1", "--start", "2"], fake)
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), {"items": [{"id": "2"}], "complete": True, "next_start": None})

    def test_issue_urls_must_match_configured_site(self):
        fake = FakeJira({})
        code, _, err = self.run_cli(["get", "https://other.atlassian.net/browse/DEMO-1"], fake)
        self.assertEqual(code, 1)
        self.assertIn("configured Jira site", err)
        self.assertEqual(fake.calls, [])

    def test_client_refuses_mutations_without_sending(self):
        opener = mock.Mock()
        with mock.patch("urllib.request.build_opener", return_value=opener):
            client = read.Client(CONFIG)
        for method, path in (("PUT", ISSUE), ("DELETE", ISSUE), ("POST", ISSUE + "/comment")):
            with self.subTest(method=method, path=path), self.assertRaises(read.JiraError):
                client.request(method, path, body={})
        opener.open.assert_not_called()

    def test_bad_request_message_is_reported_and_redacted(self):
        body = json.dumps({"errorMessages": ["Unbounded JQL queries are not allowed here."], "errors": {"x": "fixture-token"}})

        def reject(request, timeout):
            raise urllib.error.HTTPError(request.full_url, 400, "Bad Request", {}, io.BytesIO(body.encode()))
        opener = mock.Mock()
        opener.open.side_effect = reject
        with (mock.patch.object(sys, "argv", ["jira-read", "--env-file", str(self.env_file), "count", "--jql", "ORDER BY updated"]),
              mock.patch.dict(os.environ, CONFIG, clear=True),
              mock.patch("urllib.request.build_opener", return_value=opener),
              contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as err):
            code = read.main()
        self.assertEqual(code, 1)
        self.assertIn("Unbounded JQL queries are not allowed here.", err.getvalue())
        self.assertNotIn("fixture-token", err.getvalue())


if __name__ == "__main__":
    unittest.main()
