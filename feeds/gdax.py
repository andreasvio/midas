#!/usr/bin/env python

import tornado
import tornado.gen
from tornado.websocket import websocket_connect
import json
import time
import asyncio
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer

MAX_UPDATE_COUNT = 10000

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

async def send_one(msg):
    producer = AIOKafkaProducer(
        loop=tornado.ioloop.IOLoop.current().asyncio_loop, bootstrap_servers='localhost:9092')
    # Get cluster layout and initial topic/partition leadership information
    await producer.start()
    try:
        # Produce message
        print('Sending message')
        await producer.send_and_wait("testing_topic", msg)
    finally:
        # Wait for all pending messages to be delivered or expire.
        await producer.stop()

async def consume():
    consumer = AIOKafkaConsumer('testing_topic', loop=tornado.ioloop.IOLoop.current().asyncio_loop, bootstrap_servers='localhost:9092')
    # Get cluster layout and join group `my-group`
    await consumer.start()
    try:
        # Consume messages
        async for msg in consumer:
            print("consumed: ", msg)
    finally:
        # Will leave consumer group; perform autocommit if enabled.
        await consumer.stop()

class WSClient(tornado.websocket.WebSocketHandler):
    clients = set()

    def __init__(self, url):
        self.url = url
        self.conn = None
        self.count = 0
        self.loop = tornado.ioloop.IOLoop.current()
        self.producer = AIOKafkaProducer(
            loop=tornado.ioloop.IOLoop.current().asyncio_loop, 
            bootstrap_servers='localhost:9092',
            value_serializer=self.serializer
        )

    def serializer(self, value):
        return json.dumps(value).encode()

    async def start(self):
        websocket_connect(
            self.url,
            callback=self.on_connected,
            on_message_callback=self.on_message)
        await self.producer.start()
        

    def on_connected(self, conn):
        try:
            self.conn = conn.result()
            print('*** SUBSCRIBE ***')
            self.conn.write_message(json.dumps(SUBSCRIBE))
        except Exception as e:
            print(str(e))
            tornado.ioloop.IOLoop.current().stop()

    def on_message(self, data):
        msg = json.loads(data)
        try:
            if msg['type'] == 'received':
                # getattr(self, 'on_{}'.format(msg['type']))(msg)
                self.loop.spawn_callback(self.producer.send_and_wait,'testing_topic',msg)
                print('Message sent')
                # time.sleep(2)
        except:
            print(msg)
            tornado.ioloop.IOLoop.current().stop()
        else:
            self.count += 1
            if self.count == MAX_UPDATE_COUNT:
                print('*** UNSUBSCRIBE ***')
                self.conn.write_message(json.dumps(UNSUBSCRIBE))
            if self.count > MAX_UPDATE_COUNT:
                print('*** STOP ***')
                tornado.ioloop.IOLoop.current().stop()

    # any response
    def on_error(self, msg):
        print('error', msg['message'], msg['original'])
        print('*** STOP ***')
        tornado.ioloop.IOLoop.current().stop()

    # subscribe response
    def on_subscriptions(self, msg):
        print('subscriptions', ','.join([channel['name'] for channel in msg['channels']]))

    # update channel=level2
    def on_snapshot(self, msg):
        # bids,asks are arrays of [price,size], size is total
        print('snapshot', msg['product_id'], len(msg['bids']), len(msg['asks']))

    # update channel=level2
    def on_l2update(self, msg):
        # guaranteed delivery
        # changes is array of [side,price,size], side in (buy|sell), size is total
        print('l2update', msg['product_id'], len(msg['changes']))

    # update channel=ticker,...?
    def on_heartbeat(self, msg):
        print('heartbeat', msg['product_id'], msg['sequence'], msg['time'])

    # update channel=ticker
    def on_ticker(self, msg):
        # may experience dropped or out-of-order messages
        # may batch updates
        # initial update without time,side,last_size,trade_id
        print('ticker', msg['product_id'], msg['sequence'], msg.get('time'), msg['price'], msg.get('side'), msg.get('last_size'), msg.get('trade_id'))

    # update channel=full
    def on_received(self, msg):
        # order: (+price,-funds)
        # cash?: (-price,+funds) -- maybe size
        print('received', msg['product_id'], msg['sequence'], msg['time'], msg.get('price'), msg['side'], msg.get('size'), msg['order_id'], msg['order_type'], msg.get('funds'))

    # update channel=full
    def on_open(self, msg):
        print('received open', msg['product_id'], msg['sequence'], msg['time'], msg['price'], msg['side'], msg['remaining_size'], msg['order_id'])

    # update channel=full
    def on_done(self, msg):
        # when do we not get the price? cash (funds)?
        print('received', msg['product_id'], msg['sequence'], msg['time'], msg.get('price'), msg['side'], msg.get('remaining_size'), msg['order_id'], msg['reason'])

    # update channel=full
    def on_match(self, msg):
        print('received', msg['product_id'], msg['sequence'], msg['time'], msg['price'], msg['side'], msg['size'], msg['maker_order_id'], msg['taker_order_id'])


if __name__ == '__main__':
    wsc = WSClient('wss://ws-feed.gdax.com')
    # wsc.start()
    loop = tornado.ioloop.IOLoop.current()
    # loop.spawn_callback(send_one, b'a string here')
    # loop.spawn_callback(consume)
    loop.spawn_callback(wsc.start)
    loop.spawn_callback(consume)
    tornado.ioloop.IOLoop.current().start()
    