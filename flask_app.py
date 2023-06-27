import asyncio
from aiohttp import web
from models import User, Advertisement


async def get_advertisements(request):
    try:
        advertisements = await Advertisement.query.gino.all()
        return web.json_response([adv.to_dict() for adv in advertisements])
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)


async def get_advertisement(request):
    advertisement_id = int(request.match_info['advertisement_id'])
    try:
        advertisement = await Advertisement.get_or_404(advertisement_id)
        return web.json_response(advertisement.to_dict())
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)


async def create_advertisement(request):
    data = await request.json()
    try:
        advertisement = Advertisement(
            title=data['title'],
            description=data['description'],
            owner=data['owner'],
            user_id=data['user_id']
        )
        await advertisement.create()
        return web.json_response({'message': 'Advertisement created successfully'})
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)


async def update_advertisement(request):
    advertisement_id = int(request.match_info['advertisement_id'])
    data = await request.json()
    try:
        advertisement = await Advertisement.get_or_404(advertisement_id)
        await advertisement.update(
            title=data['title'],
            description=data['description'],
            owner=data['owner'],
            user_id=data['user_id']
        ).apply()
        return web.json_response({'message': 'Advertisement updated successfully'})
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)


async def delete_advertisement(request):
    advertisement_id = int(request.match_info['advertisement_id'])
    try:
        advertisement = await Advertisement.get_or_404(advertisement_id)
        await advertisement.delete()
        return web.json_response({'message': 'Advertisement deleted successfully'})
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)


async def create_user(request):
    data = await request.json()
    try:
        user = User(
            name=data['name'],
            email=data['email'],
            password=data['password']
        )
        await user.create()
        return web.json_response({'message': 'User created successfully'})
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)


async def update_user(request):
    user_id = int(request.match_info['user_id'])
    data = await request.json()
    try:
        user = await User.get_or_404(user_id)
        await user.update(
            name=data['name'],
            email=data['email'],
            password=data['password']
        ).apply()
        return web.json_response({'message': 'User updated successfully'})
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)


async def delete_user(request):
    user_id = int(request.match_info['user_id'])
    try:
        user = await User.get_or_404(user_id)
        await user.delete()
        return web.json_response({'message': 'User deleted successfully'})
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)


async def create_app():
    app = web.Application()

    app.router.add_get('/advertisements', get_advertisements)
    app.router.add_get('/advertisements/{advertisement_id}', get_advertisement)
    app.router.add_post('/advertisements', create_advertisement)
    app.router.add_patch('/advertisements/{advertisement_id}', update_advertisement)
    app.router.add_delete('/advertisements/{advertisement_id}', delete_advertisement)
    app.router.add_post('/users', create_user)
    app.router.add_patch('/users/{user_id}', update_user)
    app.router.add_delete('/users/{user_id}', delete_user)

    return app


if __name__ == '__main__':
    app = asyncio.run(create_app())
    web.run_app(app, host='localhost', port=8000)
