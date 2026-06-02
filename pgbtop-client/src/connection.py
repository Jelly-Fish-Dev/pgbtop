import asyncio
import websockets

async def connect():
    async with websockets.connect("ws://localhost:8080") as ws:
        async for messsage in ws:
            App.update(messsage)