from config.system_config import SystemConfig
from router.app_router import AppRouter
from spiders.dongmanla_spider import DongManLaSpider
from system.application import Application
import system.global_vars
import argparse
import uvicorn


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--env', help='Setting up the running environment')
    args = parser.parse_args()
    env = args.env
    if env is None:
        env = 'dev'
    system.global_vars.application = Application()
    system.global_vars.application.set_env(env)
    system.global_vars.application.set_name('liaz-spider')
    system.global_vars.systemConfig = SystemConfig()
    DongManLaSpider().parse()
    # uvicorn.run(AppRouter.instance(), host='0.0.0.0', port=8083, workers=1)
