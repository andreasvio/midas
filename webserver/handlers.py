from aiohttp import web
import asyncio
import aioredis

async def helloworld(request):
    name = request.match_info.get('name', "Anonymous")
    text = "Hello, " + name
    return web.Response(text=text)

async def redisadd():
    conn = await aioredis.create_connection(
        'redis://localhost', loop=asyncio.get_event_loop())
    await conn.execute('set', 'my-key', 'value')
    val = await conn.execute('get', 'my-key')
    print(val)
    conn.close()
    await conn.wait_closed()
    print('Connection closed')
