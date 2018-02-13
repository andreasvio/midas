import tornado.gen as gen
import tornado.web
import tornado.websocket
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer

class HelloWorld(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    @gen.coroutine
    def get(self):
        json_string = '{"first_name": "R", "last_name":"G"}'

        self.write(json_string)

class WebsocketHandler(tornado.websocket.WebSocketHandler):
    def on_connected(self):
        pass

    def open(self):
        pass
 
    def on_message(self, message):
        self.write_message(u"Your message was: " + message)
 
    def on_close(self):
        pass

class TransactionsHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        pass
 
    def on_message(self, message):
        self.write_message(u"Your message was: " + message)
 
    def on_close(self):
        pass

class EchoWebSocket(tornado.websocket.WebSocketHandler):        
    async def consume(self, consumer):
        await consumer.start()
        try:
            async for msg in consumer:
                consumed = msg.value.decode('utf-8')
                print("consumed: ", consumed)
                self.write_message(u'Consumed: ' + consumed)
        finally:
            # Will leave consumer group; perform autocommit if enabled.
            await consumer.stop()

    def check_origin(self, origin):
        return True

    def open(self):
        print("WebSocket opened")
        self.loop = tornado.ioloop.IOLoop.current()
        consumer = AIOKafkaConsumer('testing_topic', loop=tornado.ioloop.IOLoop.current().asyncio_loop, bootstrap_servers='localhost:9092')
        self.is_active = True
        self.loop.spawn_callback(self.consume, consumer)

    def on_message(self, message):
        print(message)
        self.write_message(u"You said: " + message)

    def on_close(self):
        self.is_active = False
        print("WebSocket closed")