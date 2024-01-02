from fastapi import FastAPI
from controller import root_controller, admin_spider_controller


class AppRouter:
    @classmethod
    def instance(cls):
        app = FastAPI()
        app.include_router(root_controller.router)
        app.include_router(admin_spider_controller.router)
        return app
