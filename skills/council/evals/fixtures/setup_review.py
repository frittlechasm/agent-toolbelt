#!/usr/bin/env python3
"""Create staged, unstaged, and untracked evidence for a tenant-cache review."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> None:
    workspace = Path(sys.argv[1])
    baseline = """def read_document(cache, store, tenant_id, document_id):
    key = (tenant_id, document_id)
    if key not in cache:
        cache[key] = store[(tenant_id, document_id)]
    return cache[key]
"""
    source = workspace / "documents.py"
    source.write_text(baseline, encoding="utf-8")
    (workspace / "CONTRACT.md").write_text(
        "# Document cache contract\n\n"
        "Document IDs are unique within a tenant and may repeat across tenants.\n"
        "The caller supplies a tenant ID established by authentication.\n"
        "One cache is shared across tenants; responses must belong to the requesting tenant.\n"
        "Documents are immutable for the cache lifetime, so update invalidation is out of scope.\n",
        encoding="utf-8",
    )
    for arguments in (
        ("init", "-q", "-b", "main"),
        ("config", "user.name", "Eval Fixture"),
        ("config", "user.email", "eval@example.invalid"),
        ("add", "documents.py", "CONTRACT.md"),
        ("commit", "-q", "-m", "Create tenant-scoped document cache"),
    ):
        subprocess.run(["git", *arguments], cwd=workspace, check=True)

    source.write_text(
        baseline.replace("key = (tenant_id, document_id)", "key = document_id"),
        encoding="utf-8",
    )
    subprocess.run(["git", "add", "documents.py"], cwd=workspace, check=True)
    source.write_text(
        """def read_document(cache, store, tenant_id, document_id):
    key = document_id
    if key in cache:
        return cache[key]
    document = store[(tenant_id, document_id)]
    cache[key] = document
    return document
""",
        encoding="utf-8",
    )
    (workspace / "test_documents.py").write_text(
        """import unittest

from documents import read_document


class DocumentCacheTests(unittest.TestCase):
    def test_same_document_id_is_isolated_by_tenant(self):
        cache = {}
        store = {
            ("alpha", "42"): {"tenant_id": "alpha", "body": "Alpha private document"},
            ("beta", "42"): {"tenant_id": "beta", "body": "Beta private document"},
        }
        read_document(cache, store, "alpha", "42")
        result = read_document(cache, store, "beta", "42")
        self.assertEqual(result["tenant_id"], "beta")
        self.assertEqual(result["body"], "Beta private document")

    def test_same_tenant_reuses_cached_document(self):
        cache = {}
        store = {("alpha", "42"): {"tenant_id": "alpha", "body": "Alpha private document"}}
        first = read_document(cache, store, "alpha", "42")
        del store[("alpha", "42")]
        self.assertIs(read_document(cache, store, "alpha", "42"), first)


if __name__ == "__main__":
    unittest.main()
""",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
