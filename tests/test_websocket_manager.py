import asyncio

from python_mastery_portfolio.websocket_manager import ConnectionManager


class FakeWebSocket:
    def __init__(self):
        self._accepted = False
        self.sent = []

    async def accept(self):
        self._accepted = True

    async def send_text(self, message: str):
        # simulate send
        self.sent.append(message)


async def _run_smoke_test():
    manager = ConnectionManager()
    ws = FakeWebSocket()
    await manager.connect(ws)
    assert manager.get_connection_count() == 1
    await manager.send_personal_message("hello", ws)
    assert ws.sent == ["hello"]
    manager.disconnect(ws)
    assert manager.get_connection_count() == 0


def test_websocket_manager_smoke():
    asyncio.get_event_loop().run_until_complete(_run_smoke_test())

