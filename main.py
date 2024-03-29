import argparse

import uvicorn

import system.global_vars
from config.system_config import SystemConfig
from router.app_router import AppRouter
from spiders.bilinovel_spider import BiliNovelSpider
from system.application import Application

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--env', help='Setting up the running environment')
    parser.add_argument('-p', '--port', help='Set port')
    args = parser.parse_args()
    env = args.env
    port = args.port
    if env is None:
        env = 'test'
    if port is None:
        port = 8083
    print('env : ', env, ', port : ', port)
    system.global_vars.application = Application()
    system.global_vars.application.set_env(env)
    system.global_vars.application.set_name('liaz-spider')
    system.global_vars.systemConfig = SystemConfig()
    BiliNovelSpider().search('关于')
    uvicorn.run(AppRouter.instance(), host='0.0.0.0', port=int(port), workers=1)
