from aiohttp import web
import handlers

def setup_routes(app):
    app.router.add_get('/', handlers.helloworld)
    app.router.add_get('/transactions/', handlers.helloworld)
    app.router.add_get('/hello/{name}', handlers.helloworld)
    app.router.add_get('/ws/', handlers.helloworld)


def main():
    app = web.Application()
    setup_routes(app)
    web.run_app(app, host='127.0.0.1', port=8888)


if __name__ == "__main__":
    main()
