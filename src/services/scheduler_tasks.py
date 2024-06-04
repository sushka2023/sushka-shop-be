from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.database.db import get_db
from src.repository import nova_poshta as repository_novaposhta

scheduler = AsyncIOScheduler()


async def scheduled_update():
    db = next(get_db())
    await repository_novaposhta.update_warehouses_data(db=db)


def start_scheduler():
    scheduler.add_job(scheduled_update, "cron", hour=22, minute=0)
    scheduler.start()


def stop_scheduler():
    scheduler.shutdown()
