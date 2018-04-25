#!/usr/bin/python3.6
import asyncio
from aiohttp import web
import aiohttp_jinja2
import jinja2
from requests.api import request

from graphql.type.definition import (
    GraphQLArgument,
    GraphQLField,
    GraphQLNonNull,
    GraphQLObjectType,
)

from aiohttp_graphql import GraphQLView
from graphql.type.scalars import GraphQLString
from graphql.type.schema import GraphQLSchema

#from routes import routes


def resolve_raises(*args):
    # pylint: disable=unused-argument
    raise Exception("Throws!")

# Sync schema
QueryRootType = GraphQLObjectType(
    name='QueryRoot',
    fields={
        'thrower': GraphQLField(
            GraphQLNonNull(GraphQLString),
            resolver=resolve_raises,
        ),
        'request': GraphQLField(
            GraphQLNonNull(GraphQLString),
            resolver=lambda obj, info, *args: \
                info.context['request'].query.get('q'),
            ),
        'context': GraphQLField(
            GraphQLNonNull(GraphQLString),
            resolver=lambda obj, info, *args: info.context,
        ),
        'test': GraphQLField(
            type=GraphQLString,
            args={'who': GraphQLArgument(GraphQLString)},
            # resolver=lambda obj, args, context, info: \
            resolver=lambda obj, info, **args: \
                'Hello %s' % (args.get('who') or 'World'),
        ),
    },
)


MutationRootType = GraphQLObjectType(
    name='MutationRoot',
    fields={
        'writeTest': GraphQLField(
            type=QueryRootType,
            resolver=lambda *args: QueryRootType
        )
    }
)

Shema = GraphQLSchema(QueryRootType,MutationRootType)

async def resolver(context, *args):
    return 'hey'

async def resolver_1(context, *args):
    return  'hey2'

async def resolver_2(context, *args):
    return 'hey3'

AsyncQueryType = GraphQLObjectType('AsyncQueryType', {
    'a': GraphQLField(GraphQLString, resolver=resolver),
    'b': GraphQLField(GraphQLString, resolver=resolver_1),
    'c': GraphQLField(GraphQLString, resolver=resolver_2)
})

AsyncShema = GraphQLSchema(AsyncQueryType)

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

async def test_handle(request):
    content = """
    <!DOCTYPE html>
<html>
<body>

<h2>INDEX</h2>

<p><a href="./settings">Settings</a> </p>

<p><a href="./edit">Edit</a></p>

</body>
</html>
    """
    return web.Response(body=content,content_type='text/html')


async def settings_handle(request):   
    response = aiohttp_jinja2.render_template('settings.html', request, {})
    response.headers['Content-Language'] = 'en'
    return response

async def edit_handle(request):   
    response = aiohttp_jinja2.render_template('edit.html', request, {})
    response.headers['Content-Language'] = 'en'
    return response

async def login_handle(request):
    response = aiohttp_jinja2.render_template('login.html', request, {})
    response.headers['Content-Language'] = 'en'
    response.headers['login']            = 'yes'
    return response

async def verify_handle(request):
    return web.Response(text="Hello, world")

async def error403_handle(request):
    return web.Response(text="ERROR 403")


@web.middleware
async def my_first_middl(request,handler):
    info = await request.post()
    fname = info.get('fname')
    lname = info.get('lname')
    if fname == '' or lname == '':
#        print("403")
        return web.Response(text="ERROR 403")
#    print("name:  ", fname, "\n")
#    print("lname: ", lname, "\n")
    response = await handler(request)
    return response

app = web.Application(middlewares = [ my_first_middl ])
app.add_routes([web.get('/index',       index_handle),
                web.get('/echo',        wshandle),
                web.get('/settings',    settings_handle),
                web.get('/test',        test_handle),
                web.get('/login',       login_handle),
                web.post('/verify',      verify_handle),
                web.get('/edit',        edit_handle)])

#for route in routes:
#        app.router.add_route(route[0], route[1], route[2])

aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('templates/'))

GraphQLView.attach(app, schema=AsyncShema, graphiql=True)

web.run_app(app)
    
