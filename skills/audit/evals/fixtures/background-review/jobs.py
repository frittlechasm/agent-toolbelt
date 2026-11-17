from client import DestinationFailure, TemporaryFailure


def run_pending(store, client, tick):
    for item in store.pending():
        if not store.claim(item.id):
            continue
        try:
            client.send(item.target)
        except TemporaryFailure:
            store.release(item.id)
        except DestinationFailure:
            # Stop after four hourly runs.
            if store.bump_failure(item.id) >= 4:
                store.stop(item.id)
            else:
                store.release(item.id)
        else:
            store.complete(item.id)


def run_cleanup(store, tick):
    with store.job_lock("cleanup", tick) as acquired:
        if acquired:
            store.delete_expired()
