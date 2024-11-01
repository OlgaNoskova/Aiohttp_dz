import json

from aiohttp import web
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models import Session, Advertisement, init_orm, close_orm


app = web.Application()


async def orm_context(app):
    print("START")
    await init_orm()
    yield
    await close_orm()
    print("FINISH")


@web.middleware
async def session_middleware(request: web.Request, handler):
    async with Session() as session:
        request.session = session
        response = await handler(request)
        return response


app.cleanup_ctx.append(orm_context)
app.middlewares.append(session_middleware)


def get_http_error(error_cls, error_msg):
    error = error_cls(
        text=json.dumps(
            {
                "error": error_msg,
            },
        ),
        content_type="application/json",
    )
    return error


async def get_advertisement_by_id(session: AsyncSession, advertisement_id: int) -> Advertisement:
    advertisement = await session.get(Advertisement, advertisement_id)
    if advertisement is None:
        raise get_http_error(web.HTTPNotFound, 'advertisement not found')
    return advertisement


async def add_advertisement(session: AsyncSession, advertisement: Advertisement):
    session.add(advertisement)
    try:
        await session.commit()
    except IntegrityError:
        raise get_http_error(web.HTTPConflict, "advertisement already exists")
    return advertisement


class AdvertisementView(web.View):

    @property
    def session(self) -> AsyncSession:
        return self.request.session

    @property
    def advertisement_id(self):
        return int(self.request.match_info["advertisement_id"])

    async def get(self):
        advertisement = await get_advertisement_by_id(self.session, self.advertisement_id)
        return web.json_response(advertisement.json)

    async def post(self):
        json_data = await self.request.json()
        advertisement = Advertisement(**json_data)
        advertisement = await add_advertisement(self.session, advertisement)
        return web.json_response({"id": advertisement.id})

    async def delete(self):
        advertisement = await get_advertisement_by_id(self.session, self.advertisement_id)
        await self.session.delete(advertisement)
        await self.session.commit()
        return web.json_response({"status": "deleted"})


app.add_routes(
    [
        web.get(r"/advertisement/{advertisement_id:\d+}", AdvertisementView),
        web.delete(r"/advertisement/{advertisement_id:\d+}", AdvertisementView),
        web.post("/advertisement/", AdvertisementView),
    ]
)


web.run_app(app)