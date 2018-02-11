import aiohttp
import asyncio
import json

SUBSCRIBE = {
    "type": "subscribe",
    "product_ids": ["BTC-USD","ETH-USD","ETH-EUR"],
    "channels": [
        "level2",
        "heartbeat",
        {
            "name": "ticker",
            "product_ids": ["BTC-USD"]
        },
        {
            "name": "full",
            "product_ids": ["BTC-USD"]
        }
    ]
}

UNSUBSCRIBE = {
    "type": "unsubscribe",
    "product_ids": [],  # empty means all
    "channels": [
        "level2",
        "heartbeat",
        {
            "name": "ticker",
            "product_ids": []  # empty means all
        }
    ]
}

MESSAGE_CAP = 100

async def run():
    global MESSAGE_CAP
    session = aiohttp.ClientSession()
    async with session.ws_connect(url='wss://ws-feed.gdax.com') as ws:
        await subscribe(ws)
        print('Subscribed')
        while MESSAGE_CAP > 0:
            msg = await ws.receive_json()
            print('Received message {}'.format(msg))
            MESSAGE_CAP = MESSAGE_CAP - 1
    await session.close()

async def subscribe(ws):
    ws.send_json(SUBSCRIBE)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
