from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from router.aemet_routes import fill_db_aemet
from main import scheduler

# Schedule the fill_db_aemet job
scheduler.add_job(
    fill_db_aemet,
    IntervalTrigger(days=15),
    #IntervalTrigger(minutes=1),
    id="fill_db_aemet_job",
    replace_existing=True,
    max_instances=1
)

scheduler.start()