class DestinationFailure(Exception):
    pass


class TemporaryFailure(Exception):
    pass


class Client:
    def __init__(self, transport):
        self.transport = transport

    def send(self, target):
        return self.transport.send(target)

    def try_send(self, target):
        try:
            self.send(target)
        except (DestinationFailure, TemporaryFailure):
            return False
        return True
