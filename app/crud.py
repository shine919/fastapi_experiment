from db import resources


async def get_resourse(username: str):
    return resources[username]

async def add_resource(username: str, content: str,is_public: bool = False):
    resources[username] = {'content':  content, 'is_public': is_public}
    return

async def patch_resourse(username: str, content: str,is_public:bool  = None):
    if is_public:
        resources[username] = {'content':  content, 'is_public': is_public}
    else:
        resources[username] = {'content':  content,'is_public' : resources[username]['is_public']}
    return

async def delete_resource(username: str):
    del resources[username]
    return