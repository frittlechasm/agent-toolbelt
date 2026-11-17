import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from client import DestinationFailure
from jobs import run_pending


class JobTests(unittest.TestCase):
    def test_failed_delivery_counts_once(self):
        store = Mock()
        store.pending.return_value = [SimpleNamespace(id=1, target="test@example.invalid")]
        store.claim.return_value = True
        store.bump_failure.return_value = 1
        client = Mock()
        client.send.side_effect = DestinationFailure()
        run_pending(store, client, tick=1)
        store.bump_failure.assert_called_once_with(1)
        store.release.assert_called_once_with(1)
