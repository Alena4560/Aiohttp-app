import asyncio
import asyncpg
from werkzeug.security import check_password_hash, generate_password_hash

from aiohttp import web
from models import User, Advertisement, PG_DSN, engine, Base, Session
from schema import CreateUser, UpdateUser, CreateAdvertisement, UpdateAdvertisement
# from pydantic import validate_model


async def app_context(app: web.Application):
    # start database migrations
    print("START")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()
    print("SHUTDOWN")


@web.middleware
async def session_middleware(request: web.Request, handler):
    # make session like middleware
    async with Session() as session:
        request['session'] = session
        response = await handler(request)
        return response


class AdvertisementView:
    # def __init__(self, pool):
    #     self.pool = pool

    async def get_advertisements(self, request):
        try:
            async with self.pool.acquire() as connection:
                async with connection.transaction():
                    # advertisements = await Advertisement.query.gino.all()
                    advertisements = await Advertisement.query.all()
                    return web.json_response([adv.to_dict() for adv in advertisements])
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)

    async def get_advertisement(self, request):
        advertisement_id = int(request.match_info['advertisement_id'])
        try:
            async with self.pool.acquire() as connection:
                async with connection.transaction():
                    advertisement = await Advertisement.get_or_404(advertisement_id)
                    return web.json_response(advertisement.to_dict())
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)

    async def create_advertisement(self, request):
        data = await request.json()
        try:
            async with self.pool.acquire() as connection:
                async with connection.transaction():
                    data = dict(
                        title=data['title'],
                        description=data['description'],
                        owner=data['owner'],
                        user_id=data['user_id']
                    )
                    advertisement = CreateAdvertisement(**data)
                    advertisement_dict = advertisement.dict()
                    # validate_model(CreateAdvertisement, advertisement_dict)
                    new_advertisement = await Advertisement.create(**advertisement_dict)
                    return web.json_response({'message': 'Advertisement created successfully'})
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)

    async def update_advertisement(self, request):
        advertisement_id = int(request.match_info['advertisement_id'])
        data = await request.json()
        try:
            async with self.pool.acquire() as connection:
                async with connection.transaction():
                    advertisement = await Advertisement.get_or_404(advertisement_id)
                    advertisement_dict = advertisement.dict()
                    updated_data = UpdateAdvertisement(
                        title=data.get('title', advertisement_dict['title']),
                        description=data.get('description', advertisement_dict['description']),
                        owner=data.get('owner', advertisement_dict['owner']),
                        user_id=data.get('user_id', advertisement_dict['user_id'])
                    )
                    advertisement_dict = updated_data.dict()
                    # validate_model(UpdateAdvertisement, advertisement_dict)
                    await advertisement.update(**advertisement_dict).apply()
                    return web.json_response({'message': 'Advertisement updated successfully'})
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)

    async def delete_advertisement(self, request):
        advertisement_id = int(request.match_info['advertisement_id'])
        try:
            async with self.pool.acquire() as connection:
                async with connection.transaction():
                    advertisement = await Advertisement.get_or_404(advertisement_id)
                    await advertisement.delete()
                    return web.json_response({'message': 'Advertisement deleted successfully'})
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)


class UserView(web.View):
    # def __init__(self, pool):
    #     self.pool = pool

    @property
    def session(self) -> Session:
        # change middleware session to self.session
        return self.request['session']

    @property
    def user_id(self) -> int:
        # get user_id from url like self.user_id
        return int(self.request.match_info['user_id'])

    async def get(self):
        user = await self.session.get(User, self.user_id)
        if user is not None:
            return web.json_response({
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'creation_time': user.creation_time.strftime("%Y-%m-%d %H:%M")
            })
        return web.json_response({'error': 'User not found'})

    async def post(self):
        # create new user
        data = await self.request.json()
        # print(data)
        try:
            user = User(**data)
            self.session.add(user)
            await self.session.commit()
            return web.json_response({'message': 'User created successfully', 'id': user.id})
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)

    async def patch(self):
        # update user (self.user_id)
        user = await self.session.get(User, self.user_id)
        if user is None:
            return web.json_response({'error': 'User not found'})
        data = await self.request.json()

        if 'password' in data:
            data['password'] = generate_password_hash(data['password'])
        try:
            for field, value in data.items():
                if hasattr(user, field):
                    setattr(user, field, value)
            self.session.add(user)
            await self.session.commit()
            return web.json_response({'message': 'User updated successfully', 'id': user.id})
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)

    async def delete(self):
        # delete user
        user = await self.session.get(User, self.user_id)
        if user is None:
            return web.json_response({'error': 'User not found'})
        try:
            await self.session.delete(user)
            await self.session.commit()
            return web.json_response({'message': 'User deleted successfully'})
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)


async def create_app():
    app = web.Application()

    app.cleanup_ctx.append(app_context)
    app.middlewares.append(session_middleware)

    advertisement_view = AdvertisementView()

    app.router.add_get('/advertisements', advertisement_view.get_advertisements)
    app.router.add_get('/advertisements/{advertisement_id}', advertisement_view.get_advertisement)
    app.router.add_post('/advertisements', advertisement_view.create_advertisement)
    app.router.add_patch('/advertisements/{advertisement_id}', advertisement_view.update_advertisement)
    app.router.add_delete('/advertisements/{advertisement_id}', advertisement_view.delete_advertisement)


    app.router.add_route('POST', '/users', UserView)
    # app.router.add_post('/users', user_view.create_user)
    app.router.add_route('PATCH', '/users/{user_id}', UserView)
    # app.router.add_patch('/users/{user_id}', user_view.update_user)
    app.router.add_route('DELETE', '/users/{user_id}', UserView)
    # app.router.add_delete('/users/{user_id}', user_view.delete_user)
    app.router.add_route('GET', '/users/{user_id}', UserView)

    return app


if __name__ == '__main__':
    # my_app = asyncio.run(create_app(), debug=True)
    # web.run_app(my_app, host='localhost', port=8000)
    web.run_app(create_app(), host='localhost', port=8080)
