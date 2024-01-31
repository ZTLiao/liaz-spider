from fastapi import FastAPI
from controller import root_controller, script_controller, transfer_controller
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from task import dongmanla_task, dongmanzhijia_task

app = FastAPI()


class AppRouter:
    @classmethod
    def instance(cls):
        app.include_router(root_controller.router)
        app.include_router(script_controller.router)
        app.include_router(transfer_controller.router)
        return app


@app.on_event("startup")
async def start_scheduler():
    scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")
    scheduler.add_job(dongmanla_task.execute, 'cron', hour=20, minute=00)
    scheduler.add_job(dongmanzhijia_task.execute, 'cron', minute=59)
    scheduler.start()
