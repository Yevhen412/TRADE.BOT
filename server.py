from aiohttp import web

routes = web.RouteTableDef()

@routes.get("/")
async def status(request):
    return web.Response(text="✅ Bot is running")

def create_app():
    app = web.Application()
    app.add_routes(routes)
    return app
