from fastapi import FastAPI
from controller import root_controller


class AppRouter:
    @classmethod
    def instance(cls):
        app = FastAPI()
        app.include_router(root_controller.router)
        return app
