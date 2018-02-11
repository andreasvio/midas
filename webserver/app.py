from aiohttp import web
import handlers
import asyncio

def setup_routes(app):
    app.router.add_get('/', handlers.helloworld)
    app.router.add_get('/transactions/', handlers.helloworld)
    app.router.add_get('/hello/{name}', handlers.helloworld)
    app.router.add_get('/ws/', handlers.helloworld)
    app.router.add_get('/redisadd/', handlers.redisadd)


def main():
    app = web.Application()
    setup_routes(app)
    web.run_app(app, host='127.0.0.1', port=8888, loop=asyncio.get_event_loop())

if __name__ == "__main__":
    main()
