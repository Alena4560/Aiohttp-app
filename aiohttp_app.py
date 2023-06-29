import asyncio
import asyncpg
from aiohttp import web
from models import User, Advertisement, PG_DSN
from schema import CreateUser, UpdateUser, CreateAdvertisement, UpdateAdvertisement
from pydantic import validate_model


class AdvertisementView:
    def __init__(self, pool):
        self.pool = pool

    async def get_advertisements(self, request):
        try:
            async with self.pool.acquire() as connection:
                async with connection.transaction():
                    advertisements = await Advertisement.query.gino.all()
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
                    advertisement = CreateAdvertisement(
                        title=data['title'],
                        description=data['description'],
                        owner=data['owner'],
                        user_id=data['user_id']
                    )
                    advertisement_dict = advertisement.dict()
                    validate_model(CreateAdvertisement, advertisement_dict)
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
                    validate_model(UpdateAdvertisement, advertisement_dict)
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


class UserView:
    def __init__(self, pool):
        self.pool = pool

    async def create_user(self, request):
        data = await request.json()
        try:
            async with self.pool.acquire() as connection:
                async with connection.transaction():
                    user = CreateUser(
                        name=data['name'],
                        email=data['email'],
                        password=data['password']
                    )
                    user_dict = user.dict()
                    validate_model(CreateUser, user_dict)
                    new_user = await User.create(**user_dict)
                    return web.json_response({'message': 'User created successfully'})
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)

    async def update_user(self, request):
        user_id = int(request.match_info['user_id'])
        data = await request.json()
        try:
            async with self.pool.acquire() as connection:
                async with connection.transaction():
                    user = await User.get_or_404(user_id)
                    user_dict = user.dict()
                    updated_data = UpdateUser(
                        name=data.get('name', user_dict['name']),
                        email=data.get('email', user_dict['email']),
                        password=data.get('password', user_dict['password'])
                    )
                    user_dict = updated_data.dict()
                    validate_model(UpdateUser, user_dict)
                    await user.update(**user_dict).apply()
                    return web.json_response({'message': 'User updated successfully'})
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)

    async def delete_user(self, request):
        user_id = int(request.match_info['user_id'])
        try:
            async with self.pool.acquire() as connection:
                async with connection.transaction():
                    user = await User.get_or_404(user_id)
                    await user.delete()
                    return web.json_response({'message': 'User deleted successfully'})
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)


async def create_app():
    app = web.Application()
    dsn = PG_DSN
    pool = await asyncpg.create_pool(dsn=dsn)

    advertisement_view = AdvertisementView(pool)
    user_view = UserView(pool)

    app.router.add_get('/advertisements', advertisement_view.get_advertisements)
    app.router.add_get('/advertisements/{advertisement_id}', advertisement_view.get_advertisement)
    app.router.add_post('/advertisements', advertisement_view.create_advertisement)
    app.router.add_patch('/advertisements/{advertisement_id}', advertisement_view.update_advertisement)
    app.router.add_delete('/advertisements/{advertisement_id}', advertisement_view.delete_advertisement)
    app.router.add_post('/users', user_view.create_user)
    app.router.add_patch('/users/{user_id}', user_view.update_user)
    app.router.add_delete('/users/{user_id}', user_view.delete_user)

    return app


if __name__ == '__main__':
    my_app = asyncio.run(create_app())
    web.run_app(my_app, host='localhost', port=8000)
