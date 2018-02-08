import tornado.gen as gen
from tornado.web import RequestHandler

class HelloWorld(RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    @gen.coroutine
    def get(self):
        json_string = '{"first_name": "R", "last_name":"G"}'

        self.write(json_string)

