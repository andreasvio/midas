import tornado.gen as gen
import tornado.web
import tornado.websocket

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
    def check_origin(self, origin):
        return True

    def open(self):
        print("WebSocket opened")

    def on_message(self, message):
        self.write_message(u"You said: " + message)

    def on_close(self):
        print("WebSocket closed")