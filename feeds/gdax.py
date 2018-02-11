import aiohttp
import asyncio
import json
import aioredis
from aioredis.pubsub import Receiver

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

class GdaxFeed(object):
    def __init__(self):
        self.MESSAGE_CAP = 100
        self.loop = asyncio.get_event_loop()
        self.channel = 'feed.gdax.transactions'

    def start(self):
        self.loop.run_until_complete(self.receive())
        self.loop.run_until_complete(self.run())
        
   
    async def subscribe(self, ws):
        ws.send_json(SUBSCRIBE)

    async def receive(self):
        print('Receive from redis')
        sub = await aioredis.create_connection(('localhost', 6379))
        receiver = Receiver()
        sub.execute_pubsub('subscribe', receiver.channel(self.channel))
        while (await receiver.wait_message()):
            msg = await receiver.get()
            print("Got Message:", msg)

    async def run(self):
        pub = await aioredis.create_connection(('localhost', 6379))
        
        session = aiohttp.ClientSession()
        async with session.ws_connect(url='wss://ws-feed.gdax.com') as ws:
            await self.subscribe(ws)
            print('Subscribed')
            while self.MESSAGE_CAP > 0:
                msg = await ws.receive_json()
                
                res = await pub.execute('publish' ,self.channel, 'HELLO')
                print('Publish to redis, {}'.format(res))
                # print('Received message {}'.format(msg))
                self.MESSAGE_CAP = self.MESSAGE_CAP - 1
        await session.close()

if __name__ == '__main__':
    feed = GdaxFeed()
    feed.start()
