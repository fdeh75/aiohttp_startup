#!/usr/bin/python3.6
import asyncio
from aiohttp import web
import aiohttp_jinja2
import jinja2
from requests.api import request

async def handle(request):
    name = request.match_info.get('name', 'Anonimus')
    text = " Hello, " + name
    return web.Response(text=text)

async def wshandle(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    async for msg in ws:
        if msg.type == web.WSMsgType.text:
            await ws.send_str("Hello, {}".format(msg.data))
        elif msg.type == web.WSMsgType.binary:
            await ws.send_bytes(msg.data)
        elif msg.type == web.WSMsgType.close:
            break
        
    return ws    
  
async def index_handle(request):   
    response = aiohttp_jinja2.render_template('index.html', request, {})
    response.headers['Content-Language'] = 'en'
    return response

async def settings_handle(request):   
    response = aiohttp_jinja2.render_template('settings.html', request, {})
    response.headers['Content-Language'] = 'en'
    return response

async def edit_handle(request):   
    response = aiohttp_jinja2.render_template('edit.html', request, {})
    response.headers['Content-Language'] = 'en'
    return response

app = web.Application()
app.add_routes([web.get('/index',index_handle),
                web.get('/echo', wshandle),
                web.get('/settings', settings_handle),
                web.get('/edit', edit_handle),
                web.get('/{name}', handle)])

aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('templates/'))


web.run_app(app)
    