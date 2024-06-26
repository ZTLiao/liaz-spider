import random

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI

from controller import root_controller, script_controller, transfer_controller
from task import dongmanla_task, dongmanzhijia_task, copymanga_task, \
    bilinovel_task, acgnbus_task

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
    random_number = random.randint(30, 59)
    scheduler.add_job(id="dongmanla", func=dongmanla_task.execute, trigger='cron', minute=random_number)
    random_number = random.randint(30, 59)
    scheduler.add_job(id="dongmanzhijia_comic", func=dongmanzhijia_task.execute_comic, trigger='cron',
                      minute=random_number)
    random_number = random.randint(30, 59)
    scheduler.add_job(id="dongmanzhijia_novel", func=dongmanzhijia_task.execute_novel, trigger='cron',
                      minute=random_number)
    random_number = random.randint(30, 59)
    scheduler.add_job(id="copymanga", func=copymanga_task.execute, trigger='cron', minute=random_number)
    random_number = random.randint(30, 59)
    scheduler.add_job(id="bilinovel", func=bilinovel_task.execute, trigger='cron', minute=random_number)
    random_number = random.randint(30, 59)
    scheduler.add_job(id="acgnbus", func=acgnbus_task.execute, trigger='cron', minute=random_number)
    scheduler.add_job(id="copymanga_task_upgrade_job", func=copymanga_task.upgrade_job, trigger='cron', hour=12,
                      minute=00)
    scheduler.start()
