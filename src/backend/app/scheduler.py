"""APScheduler background jobs: analytics daily, alert check every 6h."""
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


async def _run_daily_analytics():
    """Compute product_analytics for all products."""
    from .database import AsyncSessionLocal
    from .ml.trainer import compute_daily_analytics

    async with AsyncSessionLocal() as db:
        try:
            summary = await compute_daily_analytics(db)
            logger.info(f"Daily analytics complete: {summary}")
        except Exception as e:
            logger.error(f"Daily analytics failed: {e}")


async def _check_alerts():
    """Trigger price alerts after crawl."""
    from .database import AsyncSessionLocal
    from .services.alert_service import check_and_trigger_alerts

    async with AsyncSessionLocal() as db:
        try:
            await check_and_trigger_alerts(db)
            await db.commit()
            logger.info("Alert check complete")
        except Exception as e:
            logger.error(f"Alert check failed: {e}")


def start_scheduler():
    """Register jobs and start the scheduler."""
    # Daily analytics at 02:00
    scheduler.add_job(
        _run_daily_analytics,
        CronTrigger(hour=2, minute=0),
        id="daily_analytics",
        replace_existing=True,
        misfire_grace_time=3600,
    )

    # Alert check every 6 hours (after crawl would run)
    scheduler.add_job(
        _check_alerts,
        IntervalTrigger(hours=6),
        id="alert_check",
        replace_existing=True,
        misfire_grace_time=600,
    )

    scheduler.start()
    logger.info("APScheduler started: daily_analytics @ 02:00, alert_check every 6h")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("APScheduler stopped")
