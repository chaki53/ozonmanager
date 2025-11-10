from celery import Celery
from app.core.config import settings

celery = Celery(__name__, broker=settings.REDIS_URL, backend=settings.REDIS_URL)

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(settings.SYNC_PERIOD_SECONDS, sync_all_accounts.s(), name="sync_all")
    sender.add_periodic_task(settings.DAILY_REPORT_SECONDS, send_daily_reports.s(), name="daily_reports")

@celery.task
def sync_all_accounts():
    from app.services.sync import force_sync_all
    force_sync_all()

@celery.task
def send_daily_reports():
    # TODO: собрать и отправить PDF
    pass
