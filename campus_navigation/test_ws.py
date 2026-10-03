import asyncio
import json

import websockets


async def run_manual_websocket_check():
    """Manual smoke test; start Django before running this file directly."""
    uri = "ws://localhost:8000/ws/tracker/"
    async with websockets.connect(uri) as websocket:
        print("Connected!")
        print(await websocket.recv())
        await websocket.send(json.dumps({
            "action": "start_share",
            "consent": True,
            "display_name": "Manual test",
            "duration": 15,
        }))
        print(await websocket.recv())


if __name__ == "__main__":
    asyncio.run(run_manual_websocket_check())
